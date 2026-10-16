"""Notify IndexNow after a successful Pages deployment. Standard library only."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HOST = "hiroshindia.com"
ORIGIN = "https://" + HOST
KEY_PATH = "indexnow-key.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"


def git(*args):
    return subprocess.check_output(["git", "-c", "safe.directory=" + str(ROOT), *args], cwd=ROOT).decode("utf-8")


def sitemap_urls(text):
    urls = []
    for node in ET.fromstring(text).iter():
        if node.tag.rsplit("}", 1)[-1] != "loc":
            continue
        url = (node.text or "").strip()
        parts = urlsplit(url)
        if parts.scheme != "https" or parts.netloc != HOST or parts.query or parts.fragment:
            raise ValueError("Unexpected sitemap URL: " + url)
        urls.append(url)
    return sorted(set(urls))


def file_for_url(url):
    path = unquote(urlsplit(url).path).lstrip("/")
    return path + "index.html" if not path or path.endswith("/") else path


def select_urls(current, previous, changed):
    # Assets can change every rendered page; sitemap changes alone only add/remove URLs.
    shared = any(p.startswith("assets/") or p in {KEY_PATH, "robots.txt"} for p in changed)
    added_removed = set(current) ^ set(previous)
    affected = {url for url in set(current) | set(previous) if file_for_url(url) in changed}
    return sorted((set(current) if shared else set()) | added_removed | affected)


def request(url, data=None, token=None):
    headers = {"User-Agent": "Hirosh-IndexNow/1.0"}
    if data is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    if token:
        headers["Authorization"] = "Bearer " + token
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=45) as response:
        return response.status, response.read()


def previous_deployment(event):
    run = event["workflow_run"]
    repo = os.environ["GITHUB_REPOSITORY"]
    # Compare with the previous successful deployment, not merely the parent commit.
    # This includes changes across multi-commit pushes and failed deployments.
    for page in range(1, 6):
        url = (f"https://api.github.com/repos/{repo}/actions/workflows/{run['workflow_id']}/runs"
               f"?branch=main&status=success&per_page=100&page={page}")
        _, body = request(url, token=os.environ.get("GH_TOKEN"))
        runs = json.loads(body)["workflow_runs"]
        for candidate in runs:
            if candidate["id"] < run["id"] and candidate["head_sha"] != run["head_sha"]:
                return candidate["head_sha"]
        if len(runs) < 100:
            break
    return None


def notify(urls, key):
    if not urls:
        print("No public page changes to notify.")
        return []
    key_url = ORIGIN + "/" + KEY_PATH
    # Deployment completion can precede CDN propagation. Never send an unverified key.
    for attempt in range(6):
        try:
            status, body = request(key_url)
            if status == 200 and body.decode("utf-8").strip() == key:
                break
        except (urllib.error.URLError, UnicodeError):
            pass
        if attempt == 5:
            raise RuntimeError("Published IndexNow key could not be verified; no URLs submitted.")
        time.sleep(10)
    results = []
    for offset in range(0, len(urls), 10000):
        batch = urls[offset:offset + 10000]
        payload = {"host": HOST, "key": key, "keyLocation": key_url, "urlList": batch}
        status, _ = request(ENDPOINT, json.dumps(payload).encode("utf-8"))
        if status not in (200, 202):
            raise RuntimeError(f"Unexpected IndexNow HTTP status {status}")
        result = {"count": len(batch), "http_status": status,
                  "meaning": "Received" if status == 200 else "Received; key validation pending"}
        results.append(result)
        print(json.dumps(result))
    print("Receipt is not confirmation of crawling, indexing or ranking.")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="One-off submission of the current sitemap")
    parser.add_argument("--since", help="Compare against a previous deployed Git commit")
    parser.add_argument("--dry-run", action="store_true", help="List URLs without any submission")
    args = parser.parse_args()
    current = sitemap_urls((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    previous = args.since
    if not args.all and not previous and os.environ.get("GITHUB_EVENT_NAME") == "workflow_run":
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
        previous = previous_deployment(event)
    if args.all or not previous:
        urls = current
    else:
        old = sitemap_urls(git("show", previous + ":sitemap.xml"))
        changed = set(git("diff", "--name-only", "--no-renames", previous, "HEAD").splitlines())
        urls = select_urls(current, old, changed)
    key = (ROOT / KEY_PATH).read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[a-f0-9]{32}", key):
        raise ValueError("Invalid IndexNow verification key")
    print(f"Selected {len(urls)} URLs for {HOST}.")
    if args.dry_run:
        print("\n".join(urls))
        return
    results = notify(urls, key)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write("## IndexNow notification\n\n" + str(len(urls)) + " URLs selected.\n\n")
            for result in results:
                stream.write(f"- HTTP {result['http_status']}: {result['count']} URLs — {result['meaning']}.\n")
            stream.write("\nSubmission does not guarantee indexing or ranking.\n")


if __name__ == "__main__":
    main()

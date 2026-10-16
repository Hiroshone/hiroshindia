# IndexNow notifications

After a successful `pages build and deployment` run on main, the IndexNow workflow checks out that published revision and notifies changes since the previous successful Pages deployment. It has read-only repository permissions and does not modify the website or its deployment settings.

The root `indexnow-key.txt` verification file must remain publicly accessible. This is a website ownership proof, not a private account credential. The script verifies its live contents before submitting to `https://api.indexnow.org/indexnow`.

Only canonical HTTPS URLs from the current or previous sitemap are selected. New, edited and removed pages are included. Shared asset changes notify all current sitemap pages. Sitemap-only changes notify additions/removals. The first setup (key file added) submits the current sitemap. No URL parameters or alternate hosts are submitted.

Manual recovery: Actions → Notify IndexNow after deployment → Run workflow, after confirming main is deployed. This sends the current sitemap. Local preview: `python scripts/submit-indexnow.py --all --dry-run`. Local submission: `python scripts/submit-indexnow.py --all`.

HTTP 200 means URLs were received. HTTP 202 means receipt with key validation pending. Neither confirms crawling, indexing or ranking. HTTP errors fail the workflow visibly; do not repeatedly resubmit on throttling. Keep the sitemap and Google Search Console submission process in place.

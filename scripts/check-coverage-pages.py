"""Verify generated pages and local links without external dependencies."""
import json,re,xml.etree.ElementTree as ET
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.links=[];self.ids=[];self.h1=0;self.canonical=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.h1+=1
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
data=json.loads((ROOT/'assets/india-districts.json').read_text(encoding='utf-8'))
guides=list((ROOT/'service-areas').glob('*.html'))
assert len(guides)==36
assert len({d['code'] for s in data['states'] for d in s['districts']})==789
assert all(not s['lgd_only'] and not s['igod_only'] for s in json.loads((ROOT/'data/district-verification.json').read_text())['states'])
locations=[n.text for n in ET.fromstring((ROOT/'sitemap.xml').read_text()).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(locations)==len(set(locations))
pages={p:Page(p.read_text(encoding='utf-8')) for p in ROOT.rglob('*.html')}
for p in guides+[ROOT/'hirosh-trucking-and-logistics.html',ROOT/'service-areas.html']:
    parsed=pages[p];path='/'+p.relative_to(ROOT).as_posix();text=p.read_text(encoding='utf-8')
    assert parsed.h1==1,(path,'H1')
    assert len(parsed.ids)==len(set(parsed.ids)),(path,'duplicate IDs')
    assert parsed.canonical==['https://hiroshindia.com'+path],(path,'canonical')
    assert parsed.canonical[0] in locations,(path,'sitemap')
    assert 'noindex' not in text.lower(),path
    if p in guides:
        assert len({urlsplit(h).path for h in parsed.links if h.startswith('/services/')})==19,(path,'services')
        state_name=re.search(r'<span aria-current="page">(.*?)</span>',text).group(1)
        s=next(s for s in data['states'] if s['name'].removeprefix('The ').replace(' And ',' and ')==state_name)
        assert text.count('data-district=')==len(s['districts']),(path,'district count')
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):json.loads(raw)
    for link in parsed.links:
        u=urlsplit(link)
        if u.scheme or u.netloc:continue
        target=(ROOT/u.path.lstrip('/')) if u.path.startswith('/') else p.parent/u.path
        if not u.path:target=p
        if target.is_dir():target=target/'index.html'
        assert target.exists(),(path,'broken link',link)
        if u.fragment and target in pages:assert unquote(u.fragment) in pages[target].ids,(path,'broken anchor',link)
assert 'Gangaikondan' in (ROOT/'service-areas/tamil-nadu.html').read_text(encoding='utf-8')
for n in ['Nubra','Sham','Changthang','Zanskar','Drass']:assert n in (ROOT/'service-areas/ladakh.html').read_text(encoding='utf-8')
print('PASS: 36 state pages + corporate page; 789 districts; official reconciliation; 19 services per guide; canonicals, sitemap, schema, local links and anchors.')

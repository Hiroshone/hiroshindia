"""Build static coverage pages from reviewed data. Run from any directory; no network required."""
import html,json,re
from pathlib import Path
from urllib.parse import urlencode
ROOT=Path(__file__).resolve().parents[1]
BASE='https://hiroshindia.com'
e=html.escape
data=json.loads((ROOT/'assets/india-districts.json').read_text(encoding='utf-8'))
guides=json.loads((ROOT/'data/state-guides.json').read_text(encoding='utf-8'))['states']
states=data['states']
assert len(states)==36 and set(guides)=={s['code'] for s in states}
assert len({d['code'] for s in states for d in s['districts']})==sum(len(s['districts']) for s in states)
def name(s):return s['name'].removeprefix('The ').replace(' And ',' and ')
def slug(s):return re.sub('[^a-z0-9]+','-',name(s).lower()).strip('-')
def url(s):return '/service-areas/'+slug(s)+'.html'
def write(path,text):
    (ROOT/path).parent.mkdir(parents=True,exist_ok=True)
    (ROOT/path).write_text(text+'\n',encoding='utf-8',newline='\n')
services=[
('truck-trailer-rental','Truck & trailer rental','Vehicle arrangements for a specified load and route.'),
('goods-transport','Goods transport & road logistics','Commercial consignments and business deliveries.'),
('full-truck-load','Full Truck Load (FTL)','Dedicated truck movements assessed by load size and weight.'),
('part-truck-load','Part Truck Load (PTL)','Shared-load enquiries, subject to cargo and route suitability.'),
('express-cargo','Express cargo','Time-sensitive cargo enquiries with confirmed availability.'),
('trailer-transport','Trailer transport','Equipment and cargo requiring a trailer assessment.'),
('container-transport','Container transport','Road movements with collection and return points specified.'),
('reefer-transport','Reefer transport','Temperature-controlled movement enquiries.'),
('odc-cargo-transport','ODC cargo transport','Oversized loads requiring dimensions and route assessment.'),
('machinery-transport','Machinery transport','Packed or unpacked equipment with an agreed lifting plan.'),
('machine-dismantling','Machine dismantling','Dismantling scope assessed for the equipment and site.'),
('factory-plant-shifting','Factory & plant shifting','Coordinated machinery and facility relocation enquiries.'),
('industrial-packers-movers','Industrial packers & movers','Industrial packing and movement requirements.'),
('packing-handling','Packing & handling','Protection, loading and unloading scope agreed per shipment.'),
('car-transport','Car transport & car movers','Car shifting, car moving and car relocation enquiries; ask about covered-carrier or car-container arrangements.'),
('bike-transport','Bike transport','Motorcycle and scooter transport enquiries.'),
('household-furniture','Household & furniture shifting','Packing and relocation enquiries with an inventory.'),
('office-relocation','Office relocation','Furniture, equipment and workplace moves.'),
('vehicle-storage','Vehicle storage','Storage availability and location confirmed separately.')]
template=(ROOT/'about.html').read_text(encoding='utf-8')
header=template.split('<body>',1)[1].split('<main',1)[0].replace(' aria-current="page"','')
footer=template.split('</main>',1)[1].split('</body>',1)[0]
if '/hirosh-trucking-and-logistics.html' not in footer:
    footer=footer.replace('<a href="/about.html">Hirosh Roadways</a>','<a href="/about.html">Hirosh Roadways</a><a href="/hirosh-trucking-and-logistics.html">Our operating company</a>')
def shell(title,description,path,body,schema):
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'+f'<title>{e(title)}</title><meta name="description" content="{e(description)}"><link rel="canonical" href="{BASE}{path}"><meta name="theme-color" content="#071d38"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:type" content="website"><link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/coverage.css"><script src="/assets/site.js" defer></script><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script></head><body>'+header+'<main id="main">'+body+'</main>'+footer+'</body></html>'
def service_list():
    return '<div class="coverage-services">'+''.join(f'<article><h3><a href="/services/{key}.html">{e(label)}</a></h3><p>{e(desc)}</p></article>' for key,label,desc in services)+'</div>'
def district_list(s):
    parts=['<ul class="district-list">']
    for d in s['districts']:
        loc=f'{d["name"]}, {name(s)}'
        parts.append(f'<li data-district="{e(d["name"])}"><strong>{e(d["name"])}</strong><span><a href="/quote.html?{e(urlencode({"origin":loc}))}" aria-label="Pickup from {e(loc)}">Pickup here</a><a href="/quote.html?{e(urlencode({"destination":loc}))}" aria-label="Deliver to {e(loc)}">Deliver here</a></span></li>')
    return ''.join(parts)+'</ul>'
regions=[['32','33','29','28','36','34'],['27','30','24','38','8'],['23','22','21','20','19','10','9'],['6','3','7','4','2','5','1','37'],['18','17','16','11','15','14','13','12'],['35','31','32','33']]
for s in states:
    n=name(s);g=guides[s['code']];path=url(s)
    related=next(r for r in regions if s['code'] in r)
    crumb=f'<nav class="coverage-breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/service-areas.html">Service areas</a><span aria-hidden="true">/</span><span aria-current="page">{e(n)}</span></nav>'
    body=f'<section class="page-intro"><div class="wrap">{crumb}<p class="eyebrow">TRANSPORT · LOGISTICS · RELOCATION</p><h1>Transport &amp; logistics services in {e(n)}</h1><p class="lead">{e(g["intro"])}</p><div class="form-actions"><a class="button" href="/quote.html?{e(urlencode({"origin":n}))}">Request a transport quote ↗</a><a class="button secondary" href="#districts">Browse districts</a></div></div></section>'
    body+=f'<section class="section wrap"><h2>Industrial areas and business locations</h2><p>Selected places for planning pickup and delivery enquiries in {e(n)}. Transport arrangements are coordinated through our agent and transport-partner network.</p><div class="coverage-places">'
    body+=''.join(f'<article><h3>{e(p["area"])}</h3><p>{e(p["context"])}</p></article>' for p in g['places'])+'</div></section>'
    if g.get('local_coverage'):
        body+=f'<section class="section wrap" id="local-coverage"><h2>Local pickup and delivery areas in {e(n)}</h2><p>Find selected towns and industrial localities below, with information to help plan goods transport, logistics, car and bike shifting, machinery movements or relocation. Send the full pickup and delivery address even if your locality is not listed.</p><nav class="state-jumps" aria-label="Local coverage areas">'
        body+=''.join(f'<a href="#local-{i}">{e(p["area"])}</a>' for i,p in enumerate(g['local_coverage'],1))+'</nav><div class="coverage-places">'
        for i,p in enumerate(g['local_coverage'],1):
            body+=f'<article id="local-{i}"><h3>{e(p["area"])}</h3><p class="local-place-names">'+', '.join(e(v) for v in p['places'])+f'.</p><p>{e(p["context"])}</p></article>'
        body+='</div><p>These are service-enquiry locations supported through our agent and transport-partner network. Vehicle availability and handling arrangements are confirmed for your address and consignment.</p><a class="text-link" href="/services.html">Compare our transport and relocation services ↗</a></section>'
    body+='<section class="section wrap coverage-planning"><h2>Plan the pickup, journey and delivery</h2><ol>'+''.join(f'<li>{e(p)}</li>' for p in g['planning'])+'</ol><p>Send the pickup and delivery addresses, cargo description, package dimensions, weight and preferred date. Our team confirms vehicle availability, handling responsibilities, access and quotation terms before booking.</p></section>'
    body+=f'<section class="section wrap" id="districts"><h2>District coverage in {e(n)}</h2><p>Enquiries are welcome from every district listed below, including towns and villages within them. Enter the actual premises or village in your enquiry. Coverage through agents and transport partners does not imply a local office or every equipment type in each district.</p>{district_list(s)}<p class="form-note">District list checked against the <a href="{e(s["official_source"])}">official government directory</a> on 16 October 2026.'
    if s['code']=='37':body+=' Includes the five additional districts in the <a href="https://ladakh.gov.in/historic-milestone-for-ladakh-five-new-districts-notified-in-ladakh-taking-total-districts-to-seven/">Ladakh administration notification</a>.'
    body+=' Names and boundaries may change; you can still enquire using your full address.</p></section>'
    body+='<section class="section wrap"><h2>Explore our 19 transport and relocation services</h2><p>Choose the service that fits your consignment. Availability, equipment, storage location and handling scope are confirmed for your route; island and remote destinations require separate access and onward-movement checks.</p>'+service_list()+'</section>'
    body+=f'<section class="section wrap"><h2>Transport from {e(n)} to other parts of India</h2><p>We accept enquiries both from and to {e(n)} through our nationwide network. Include both ends of the route; the state or district selection is a starting point for planning.</p><div class="coverage-related">'
    body+=''.join(f'<a href="{url(t)}">{e(name(t))} transport guide</a>' for code in related if code!=s['code'] for t in states if t['code']==code)
    body+='</div><p><a class="text-link" href="/service-areas.html">Browse all 36 states and union territories ↗</a></p></section>'
    body+='<section class="section wrap coverage-sources"><h2>Location references</h2><p>Industrial-location references used for this guide; individual operating units and pickup access must be confirmed for the shipment.</p><ul>'+''.join(f'<li><a href="{e(source["url"])}">{e(source["label"])}</a></li>' for source in g['sources'])+'</ul></section>'
    body+='<section class="cta"><div class="wrap cta-row"><div><p class="eyebrow">HIROSH ROADWAYS</p><h2>Tell us what is moving.</h2><p>Operated by <a href="/hirosh-trucking-and-logistics.html">Hirosh Trucking and Logistics Pvt Ltd</a>, with transport coordination through our nationwide agent and partner network.</p></div><a class="button light" href="/quote.html">Send your requirement ↗</a></div></section>'
    schema={'@context':'https://schema.org','@graph':[{'@type':'WebPage','@id':BASE+path,'url':BASE+path,'name':f'Transport and logistics services in {n}','about':{'@type':'Service','name':f'Transport and relocation enquiries in {n}','provider':{'@id':BASE+'/#roadways'},'areaServed':{'@type':'AdministrativeArea','name':n}}},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE+'/'},{'@type':'ListItem','position':2,'name':'Service areas','item':BASE+'/service-areas.html'},{'@type':'ListItem','position':3,'name':n,'item':BASE+path}]}]}
    write(path.lstrip('/'),shell(f'Transport & Logistics in {n} | Hirosh Roadways',f'Goods transport, car shifting, machinery and relocation enquiries across {n}. Browse districts, industrial areas and 19 Hirosh Roadways services.',path,body,schema))

# Replace the existing directory in place, retaining the original URL and surrounding content.
parts=['<section class="section wrap" id="coverage-directory" aria-labelledby="directory-title"><p class="eyebrow">PAN-INDIA SERVICE COVERAGE</p><h2 id="directory-title">States, districts and industrial locations</h2><p>Explore 36 state and union territory guides with district lists, selected industrial areas, transport planning information and links to all 19 services.</p><p>Enquiries are supported through our nationwide agent and transport-partner network. Vehicle availability and access are confirmed for each shipment; island movements require separate onward arrangements.</p><div class="coverage-controls" hidden><label>Search a state or district<input type="search" id="district-search" placeholder="e.g. Kollam, Kolhapur, Maharashtra" autocomplete="off"></label><label>State / union territory<select id="coverage-state"><option value="">All states and union territories</option>']
parts += [f'<option value="{s["code"]}">{e(name(s))}</option>' for s in states]
parts.append('</select></label><button type="button" id="coverage-reset" class="button secondary">Clear filters</button></div><p id="coverage-status" role="status" aria-live="polite"></p><nav class="state-jumps" aria-label="State transport guides">')
south_first=['32','33','29','28','36','27']
ordered=sorted(states,key=lambda s:(south_first.index(s['code']) if s['code'] in south_first else 100,name(s)))
parts += [f'<a href="{url(s)}">{e(name(s))}</a>' for s in ordered]
parts.append('</nav><div id="state-directory">')
for s in ordered:
    parts.append(f'<details class="coverage-state" id="state-{s["code"]}" data-state="{s["code"]}" data-name="{e(name(s))}"><summary>{e(name(s))} <span>({len(s["districts"])} districts)</span></summary><p class="state-guide-link"><a class="text-link" href="{url(s)}">{e(name(s))}: industrial locations and transport services ↗</a></p>{district_list(s)}</details>')
parts.append('</div><p id="coverage-empty" hidden>No matching district found. Try another spelling, or enter your town, state and PIN code directly in the quote form.</p><p><a class="button" href="/quote.html">Enter another location / PIN code ↗</a></p><p class="form-note">District names use an LGD snapshot, cross-checked against the <a href="https://igod.gov.in/sg/district/states">official government directory</a> on 16 October 2026, with the five newly notified Ladakh districts added. A location enquiry does not require your town to have a separate page.</p></section>')
p=ROOT/'service-areas.html';text=p.read_text(encoding='utf-8')
text,n=re.subn(r'<section class="section wrap" id="coverage-directory".*?</section>',''.join(parts),text,count=1,flags=re.S);assert n==1
write('service-areas.html',text.rstrip())

corporate='/hirosh-trucking-and-logistics.html'
body='''<section class="page-intro"><div class="wrap"><p class="eyebrow">THE COMPANY BEHIND HIROSH ROADWAYS</p><h1>Hirosh Trucking and Logistics Pvt Ltd</h1><p class="lead">Hirosh Roadways is operated by Hirosh Trucking and Logistics Pvt Ltd. We coordinate transport and relocation requirements across India through a nationwide network of agents and transport partners.</p></div></section><section class="section wrap prose"><h2>One point of coordination for your movement</h2><p>Customers can approach Hirosh Roadways with a commercial consignment, machinery requirement, vehicle move or relocation project. Our team gathers the pickup and delivery details, assesses the cargo and coordinates suitable transport arrangements through the network.</p><p>A useful transport plan identifies the equipment, loading method, receiving-site access and handling responsibilities. We ask for these details before confirming the scope so that a truck journey, a machinery move and a complete relocation are quoted according to their actual requirements.</p><h2>Transport, logistics and relocation</h2><p>Our existing services include truck and trailer arrangements, commercial goods transport, Full Truck Load and Part Truck Load, express cargo, container and reefer transport, machinery movements and ODC cargo enquiries. Industrial packing, machine dismantling, factory and plant shifting, household and furniture moves, office relocation, car and bike transportation and vehicle-storage enquiries are also part of the service range.</p><p>Vehicle types, specialist equipment, storage locations and handling services are confirmed for the individual requirement. A nationwide service network does not mean company-owned offices or facilities in every location.</p><h2>Coverage built around the customer's location</h2><p>Our main office is in Kazhakuttom, Thiruvananthapuram, with an office near Vizhinjam port. The network supports enquiries from across India, including industrial estates, business towns and district locations. Use the state guides to find district coverage and selected industrial pickup points, then provide your actual site address.</p><p>Island destinations, remote roads and oversized cargo need specific access and onward-transport planning. Any additional transport leg or handling arrangement is confirmed separately before booking.</p><h2>A clear scope before dispatch</h2><p>Tell us the cargo description, package count, dimensions, weight, pickup readiness and final delivery address. For machinery, include lifting and dismantling requirements; for relocation, provide an inventory and access details. The quotation should identify the agreed transport and handling scope, payment terms and applicable charges.</p><p>Explore the current Hirosh Roadways services below, or contact our team to discuss a requirement that needs a tailored transport and handling plan.</p><p><a class="button" href="/quote.html">Discuss your transport requirement ↗</a></p></section><section class="section wrap"><h2>Our current service range</h2>'''+service_list()+'''</section><section class="cta"><div class="wrap cta-row"><div><h2>Explore our nationwide coverage.</h2><p>District lists and practical transport guidance for every state and union territory.</p></div><a class="button light" href="/service-areas.html">View service areas ↗</a></div></section>'''
schema={'@context':'https://schema.org','@graph':[{'@type':'Organization','@id':BASE+'/#company','name':'Hirosh Trucking and Logistics Pvt Ltd','url':BASE+corporate,'brand':{'@type':'Brand','name':'Hirosh Roadways'}},{'@type':'Organization','@id':BASE+'/#roadways','name':'Hirosh Roadways','url':BASE+'/','parentOrganization':{'@id':BASE+'/#company'}}]}
write(corporate.lstrip('/'),shell('Hirosh Trucking and Logistics Pvt Ltd | Hirosh Roadways','Meet the company operating Hirosh Roadways: nationwide transport, logistics and relocation coordination through agents and transport partners.',corporate,body,schema))

# Stable discoverable links on existing entry pages; additions are idempotent.
for file in ['index.html','about.html','services.html','service-areas.html']:
    text=(ROOT/file).read_text(encoding='utf-8')
    if corporate not in text:
        text=text.replace('<a href="/about.html">Hirosh Roadways</a>',f'<a href="/about.html">Hirosh Roadways</a><a href="{corporate}">Our operating company</a>')
    if file=='about.html' and 'id="operating-company"' not in text:
        text=text.replace('<h2>Related websites</h2>',f'<h2 id="operating-company">Our operating company</h2><p>Hirosh Roadways is operated by <a href="{corporate}">Hirosh Trucking and Logistics Pvt Ltd</a>. Explore our <a href="/service-areas.html">state and district service coverage</a>.</p><h2>Related websites</h2>')
    if file=='index.html' and 'id="national-coverage"' not in text:
        section='<section class="section wrap" id="national-coverage"><p class="eyebrow">PICKUP TO DELIVERY, ACROSS INDIA</p><h2>Transport, logistics and relocation across India</h2><p>Explore our state guides for every district, selected industrial locations and practical pickup information. Our nationwide agent and transport-partner network coordinates goods, machinery, car shifting and relocation enquiries.</p><p>'+' · '.join(f'<a class="text-link" href="{url(s)}">{e(name(s))}</a>' for s in ordered[:6])+'</p><a class="button" href="/service-areas.html">Browse all states and districts ↗</a></section>'
        text=text.replace('</main>',section+'</main>')
    write(file,text.rstrip())

p=ROOT/'sitemap.xml';text=p.read_text(encoding='utf-8')
for path in [url(s) for s in states]+[corporate]:
    loc=BASE+path
    if f'<loc>{loc}</loc>' not in text:text=text.replace('</urlset>',f'<url><loc>{loc}</loc></url></urlset>')
write('sitemap.xml',text.rstrip())
print(f'Built {len(states)} state/UT guides + corporate page, {sum(len(s["districts"]) for s in states)} district entries, {len(services)} services.')

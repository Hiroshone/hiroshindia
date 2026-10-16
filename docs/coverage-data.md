# National coverage pages

36 state/UT guides under /service-areas/, the existing /service-areas.html directory, and /hirosh-trucking-and-logistics.html. Existing service URLs are unchanged. All 19 current services are linked from every guide, with route/equipment availability qualified. No fictional branches, ratings, fixed prices or guaranteed transit times are added.

## District evidence: checked 16 October 2026

Base: Ministry of Panchayati Raj Local Government Directory, 23 September 2026 snapshot, GODL-India. Downloaded through https://india-lgd-index-api.vercel.app/v1/states and /v1/districts; upstream mirror https://github.com/ramSeraph/opendata.

All 36 state/UT lists were compared by normalised district name with https://igod.gov.in/sg/district/states. All 784 base entries matched. Per-state URLs and reconciliation results are in data/district-verification.json; official district website links, where present, are in assets/india-districts.json.

IGOD still listed only two Ladakh districts. The UT administration's 27 April 2026 notification names five additional districts: Sham, Nubra, Changthang, Zanskar and Drass. These are added, making 789 coverage entries. Their supplement-* identifiers are internal keys, NOT LGD codes. Source: https://ladakh.gov.in/historic-milestone-for-ladakh-five-new-districts-notified-in-ladakh-taking-total-districts-to-seven/

This is a checked, dated coverage directory, not a live administrative registry. Administrative regions, revenue districts and LGD records can differ. Puducherry's Mahe and Yanam regions are explicitly included in its guide without fabricating extra LGD districts.

## Industrial and town content

Data/state-guides.json stores separately written regional introductions, selected locations, shipment-planning guidance and primary-source URLs. Sources are displayed on each guide. The collection is selected coverage, not an exhaustive inventory of every town, industrial unit or park. Named units, availability and access still require shipment-specific confirmation. No relationship with the industrial authorities is implied.

Sources include SIPCOT, APIIC, Sri City, KIADB/MSME, KSIDC/KINFRA, Telangana investment agencies, MIDC, GIDC, RIICO, MPIDC, CSIDC, IDCO, WBIDC, JIADA, BIADA, UPSIDA, HSIIDC, PSIEC, DSIIDC and the corresponding state/UT departments. Business-town entries are enquiry locations, not claims that Hirosh has premises there.

## Maintenance

1. Update district data only after comparing dated official records; preserve provenance and distinguish supplemental identifiers from LGD codes.
2. Edit reviewed state content in data/state-guides.json.
3. Run python scripts/build-coverage-pages.py. This generator is idempotent and makes no network calls.
4. Run python scripts/check-coverage-pages.py and browser checks for mobile navigation, district filtering and quote prefill.
5. Review the complete diff before deployment. Keep existing URLs stable.

Pages and district lists render without JavaScript. Visitors make no third-party location API calls. The hub adds filtering; quote links prefill pickup/delivery using query parameters. PIN checks validate format only. All 37 new pages have crawlable links and appear in the sitemap.

The corporate page describes the current confirmed roadways services. Broader company objects are not treated as proof of active warehouses, air freight, rail freight or sea-freight operations.

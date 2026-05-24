# Public Data Sources

## Primary MVP Sources

### FEMA National Risk Index

- URL: https://hazards.fema.gov/nri/data-resources
- Use: county or census tract hazard risk scores, expected annual loss, social vulnerability, community resilience.
- MVP join key: county FIPS.
- Refresh cadence: monthly or manual for MVP.
- Storage: raw CSV in S3, normalized county-level records in DynamoDB.

### OpenFEMA Disaster Declarations Summaries

- URL: https://www.fema.gov/about/openfema/disaster-declarations-summaries
- Use: historical federally declared disasters by state/county.
- MVP join key: state, county, FIPS where available.
- Refresh cadence: weekly for MVP.
- Storage: compact county disaster counts and recent declaration list in DynamoDB.

### NOAA Storm Events Database

- URL: https://www.ncdc.noaa.gov/stormevents/ftp.jsp
- Use: historical hail, wind, tornado, flood, winter storm, and severe weather event counts.
- MVP join key: state/county and date range.
- Refresh cadence: annual or quarterly for MVP.
- Storage: pre-aggregated county hazard counts in S3/DynamoDB.

### US Census Geocoder

- URL: https://www.census.gov/programs-surveys/geography/technical-documentation/complete-technical-documentation/census-geocoder.html
- Use: turn an extracted US address into coordinates, county, state, and FIPS codes.
- Runtime use: API call during enrichment.
- Fallback: if geocoding fails, mark submission `NEEDS_REVIEW`.

## Example Normalized Hazard Record

```json
{
  "pk": "COUNTY#06037",
  "sk": "HAZARD_SUMMARY#latest",
  "state": "CA",
  "county": "Los Angeles County",
  "fips": "06037",
  "femaRiskRating": "Relatively High",
  "topHazards": ["Earthquake", "Wildfire", "Riverine Flooding"],
  "expectedAnnualLoss": 123456789,
  "recentDisasterDeclarations": 4,
  "stormEventCounts10Yr": {
    "hail": 16,
    "strongWind": 83,
    "flashFlood": 21
  },
  "sourceVersions": {
    "femaNri": "2025",
    "openFema": "2026-05 snapshot",
    "noaaStormEvents": "2014-2024"
  }
}
```

## Data Ingestion Jobs

Create a small Python ingestion CLI under `backend/scripts/` in the implementation phase:

- `download_fema_nri.py`: downloads FEMA NRI CSV files to S3.
- `download_openfema_disasters.py`: pulls OpenFEMA records and aggregates by county.
- `download_noaa_storm_events.py`: downloads NOAA annual CSV files and aggregates counts.
- `load_hazard_cache.py`: writes normalized county records to DynamoDB.

For local development, allow these scripts to write to `data/raw/` and `data/processed/`, both ignored from git.

## MVP Data Constraints

- Use only public datasets and synthetic submission documents.
- Preserve source URLs and dataset versions in generated summaries.
- Do not claim the AI output is a rating, recommendation to bind, or actuarial model.
- Surface missing or stale data in the UI instead of hiding it.


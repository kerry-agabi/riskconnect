"""Tiny SYNTHETIC in-repo fixtures for public-hazard enrichment.

THESE ARE NOT REAL DATASETS. They are a handful of hand-written sample rows
used to develop and test the enrichment slice without downloading or vendoring
the full FEMA NRI / OpenFEMA / NOAA / Census datasets (which CLAUDE.md forbids
committing). Real data is loaded at runtime from the Terraform-managed S3/Dynamo
hazard cache via the production adapters (see the TODO seams in
``enrichment_service.py``).

Each fixture row preserves the provenance the API contract requires: source
URLs and dataset versions/snapshot dates, mirroring the normalized record shape
documented in ``docs/data-sources.md``. Values below are illustrative only.
"""

from __future__ import annotations

from risklens_api.schemas.submissions import (
    DataSource,
    HazardData,
    StormEventCounts,
)

# ---------------------------------------------------------------------------
# Source provenance (public dataset references)
# ---------------------------------------------------------------------------

FEMA_NRI_SOURCE = DataSource(
    name="FEMA National Risk Index (2025)",
    url="https://hazards.fema.gov/nri/data-resources",
)
OPENFEMA_DISASTERS_SOURCE = DataSource(
    name="OpenFEMA Disaster Declarations Summaries (2026-05 snapshot)",
    url="https://www.fema.gov/about/openfema/disaster-declarations-summaries",
)
NOAA_STORM_EVENTS_SOURCE = DataSource(
    name="NOAA Storm Events Database (2014-2024)",
    url="https://www.ncdc.noaa.gov/stormevents/ftp.jsp",
)
CENSUS_GEOCODER_SOURCE = DataSource(
    name="US Census Geocoder",
    url="https://www.census.gov/programs-surveys/geography/technical-documentation/complete-technical-documentation/census-geocoder.html",
)

# Sources contributing to a hazard summary (FEMA + OpenFEMA + NOAA). The Census
# geocoder source is added by the enrichment stage because it resolved the FIPS.
HAZARD_SUMMARY_SOURCES: tuple[DataSource, ...] = (
    FEMA_NRI_SOURCE,
    OPENFEMA_DISASTERS_SOURCE,
    NOAA_STORM_EVENTS_SOURCE,
)


# ---------------------------------------------------------------------------
# Synthetic county hazard summaries keyed by 5-digit county FIPS
# ---------------------------------------------------------------------------

SAMPLE_COUNTY_HAZARDS: dict[str, HazardData] = {
    # Los Angeles County, CA -- matches the API contract example.
    "06037": HazardData(
        fema_risk_rating="Relatively High",
        top_hazards=["Earthquake", "Wildfire", "Riverine Flooding"],
        recent_disaster_declarations=4,
        storm_event_counts_10yr=StormEventCounts(
            hail=16, strong_wind=83, flash_flood=21
        ),
    ),
    # Harris County, TX (Houston).
    "48201": HazardData(
        fema_risk_rating="Very High",
        top_hazards=["Hurricane", "Riverine Flooding", "Coastal Flooding"],
        recent_disaster_declarations=9,
        storm_event_counts_10yr=StormEventCounts(
            hail=42, strong_wind=110, flash_flood=64
        ),
    ),
    # Miami-Dade County, FL.
    "12086": HazardData(
        fema_risk_rating="Very High",
        top_hazards=["Hurricane", "Coastal Flooding", "Lightning"],
        recent_disaster_declarations=7,
        storm_event_counts_10yr=StormEventCounts(
            hail=8, strong_wind=95, flash_flood=38
        ),
    ),
    # Cook County, IL (Chicago).
    "17031": HazardData(
        fema_risk_rating="Relatively Moderate",
        top_hazards=["Winter Weather", "Strong Wind", "Tornado"],
        recent_disaster_declarations=3,
        storm_event_counts_10yr=StormEventCounts(
            hail=29, strong_wind=120, flash_flood=18
        ),
    ),
}


# ---------------------------------------------------------------------------
# Synthetic address -> county FIPS map for the fixture geocoder
# ---------------------------------------------------------------------------

# Keyed by uppercased "<city>|<state>" for deterministic, tiny lookups.
SAMPLE_CITY_STATE_FIPS: dict[str, str] = {
    "LOS ANGELES|CA": "06037",
    "HOUSTON|TX": "48201",
    "MIAMI|FL": "12086",
    "CHICAGO|IL": "17031",
}

# Keyed by 5-digit ZIP prefix for a secondary fixture resolution path.
SAMPLE_POSTAL_FIPS: dict[str, str] = {
    "90012": "06037",
    "77002": "48201",
    "33101": "12086",
    "60601": "17031",
}

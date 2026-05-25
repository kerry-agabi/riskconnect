"""Behavior tests for the fixture-backed hazard enrichment service.

Uses the tiny synthetic in-repo fixtures only (no HTTP, no AWS, no full public
datasets). Covers the geocode+hazard happy path, the two NEEDS_REVIEW paths
(unresolved geocode and missing hazard row), and source provenance.
"""

from __future__ import annotations

from risklens_api.schemas.processing import EnrichmentOutcome
from risklens_api.schemas.submissions import Address, ExtractedData
from risklens_api.services.enrichment_service import (
    GEOCODE_FAILED_REASON,
    FixtureGeocodeService,
    HazardEnrichmentService,
)

SUBMISSION_ID = "TEST-ENRICH-001"


def _extracted(address: Address | None) -> ExtractedData:
    return ExtractedData(insured_name="Sample Co", address=address)


def test_happy_path_resolves_fips_and_returns_hazards_with_sources() -> None:
    service = HazardEnrichmentService()
    address = Address(
        line1="100 Example Ave",
        city="Los Angeles",
        state="CA",
        postal_code="90012",
        county_fips="06037",
    )

    result = service.enrich(SUBMISSION_ID, _extracted(address))

    assert result.outcome is EnrichmentOutcome.ENRICHED
    assert result.county_fips == "06037"
    assert result.review_reason is None
    assert result.hazards is not None
    assert result.hazards.fema_risk_rating == "Relatively High"
    assert "Earthquake" in result.hazards.top_hazards
    assert result.hazards.storm_event_counts_10yr is not None
    assert result.hazards.storm_event_counts_10yr.hail == 16

    # Provenance: Census geocoder + FEMA NRI + OpenFEMA + NOAA, all public URLs.
    source_names = [s.name for s in result.sources]
    assert any("Census" in n for n in source_names)
    assert any("National Risk Index" in n for n in source_names)
    assert any("NOAA" in n for n in source_names)
    assert all(s.url.startswith("https://") for s in result.sources)


def test_resolves_by_city_state_without_prefilled_fips() -> None:
    service = HazardEnrichmentService()
    address = Address(line1="500 Main St", city="Houston", state="TX")

    result = service.enrich(SUBMISSION_ID, _extracted(address))

    assert result.outcome is EnrichmentOutcome.ENRICHED
    assert result.county_fips == "48201"


def test_unresolved_geocode_signals_needs_review() -> None:
    service = HazardEnrichmentService()
    address = Address(line1="1 Nowhere Rd", city="Smalltown", state="ND")

    result = service.enrich(SUBMISSION_ID, _extracted(address))

    assert result.outcome is EnrichmentOutcome.NEEDS_REVIEW
    assert result.county_fips is None
    assert result.hazards is None
    assert result.review_reason == GEOCODE_FAILED_REASON
    # Even on geocode failure, the geocoder source is recorded as attempted.
    assert any("Census" in s.name for s in result.sources)


def test_missing_address_signals_needs_review() -> None:
    service = HazardEnrichmentService()

    result = service.enrich(SUBMISSION_ID, _extracted(None))

    assert result.outcome is EnrichmentOutcome.NEEDS_REVIEW
    assert result.county_fips is None
    assert result.hazards is None


def test_resolved_fips_with_no_hazard_row_signals_needs_review() -> None:
    # A geocoder that resolves a FIPS the hazard repo has no row for.
    class StubGeocoder:
        def resolve_county_fips(self, address: Address) -> str | None:
            return "99999"

    service = HazardEnrichmentService(geocoder=StubGeocoder())  # type: ignore[arg-type]
    address = Address(line1="1 Edge Case Way", city="Edge", state="XX")

    result = service.enrich(SUBMISSION_ID, _extracted(address))

    assert result.outcome is EnrichmentOutcome.NEEDS_REVIEW
    assert result.county_fips == "99999"
    assert result.hazards is None
    assert result.review_reason is not None
    assert "99999" in result.review_reason


def test_fixture_geocoder_returns_none_for_unknown_address() -> None:
    geocoder = FixtureGeocodeService()
    assert geocoder.resolve_county_fips(Address(city="Nowhere", state="ZZ")) is None

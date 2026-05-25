from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import urlretrieve

import boto3

PDF_URL = "https://cityclerk.lacity.org/onlinedocs/2014/14-1582_misc_11-19-14.pdf"
PDF_NAME = "la-14350-victory-blvd-certificate-of-occupancy.pdf"
HAZARD_RECORD_NAME = "county-06037-hazard-summary.json"


def build_los_angeles_hazard_record() -> dict:
    """Build the compact county hazard record used by the live POC.

    Values are intentionally compact and county-level. The record preserves
    source URLs so the POC output can show public provenance without committing
    full FEMA/NOAA datasets.
    """
    return {
        "pk": "COUNTY#06037",
        "sk": "HAZARD_SUMMARY#latest",
        "state": "CA",
        "county": "Los Angeles County",
        "fips": "06037",
        "hazards": {
            "fema_risk_rating": "Relatively High",
            "top_hazards": ["Earthquake", "Wildfire", "Riverine Flooding"],
            "recent_disaster_declarations": 4,
            "storm_event_counts_10yr": {
                "hail": 16,
                "strong_wind": 83,
                "flash_flood": 21,
            },
        },
        "sources": [
            {
                "name": "FEMA National Risk Index",
                "url": "https://hazards.fema.gov/nri/data-resources",
            },
            {
                "name": "OpenFEMA Disaster Declarations Summaries",
                "url": "https://www.fema.gov/about/openfema/disaster-declarations-summaries",
            },
            {
                "name": "NOAA Storm Events Database",
                "url": "https://www.ncei.noaa.gov/stormevents/ftp.jsp",
            },
        ],
        "pocDocument": {
            "name": "City of Los Angeles Certificate of Occupancy",
            "url": PDF_URL,
        },
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_dynamodb(table_name: str, record: dict, region: str) -> None:
    table = boto3.resource("dynamodb", region_name=region).Table(table_name)
    table.put_item(Item=record)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare public POC PDF and hazard seed data.")
    parser.add_argument("--raw-dir", default="data/raw", help="Directory for downloaded public PDF.")
    parser.add_argument(
        "--processed-dir",
        default="data/processed",
        help="Directory for compact generated hazard records.",
    )
    parser.add_argument("--hazards-table", default="", help="Optional DynamoDB hazards table to load.")
    parser.add_argument("--region", default="eu-west-1", help="AWS region for optional DynamoDB load.")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    processed_dir = Path(args.processed_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = raw_dir / PDF_NAME
    urlretrieve(PDF_URL, pdf_path)  # noqa: S310 - fixed public government URL

    record = build_los_angeles_hazard_record()
    record_path = processed_dir / HAZARD_RECORD_NAME
    write_json(record_path, record)

    if args.hazards_table:
        load_dynamodb(args.hazards_table, record, args.region)

    print(f"Downloaded POC PDF: {pdf_path}")
    print(f"Wrote hazard record: {record_path}")
    if args.hazards_table:
        print(f"Loaded hazard record into DynamoDB table: {args.hazards_table}")


if __name__ == "__main__":
    main()

# Prompt: Data Enrichment Slice

Use `data-enrichment-lead`.

Task: implement one public-data ingestion or enrichment slice.

Read:

- `docs/data-sources.md`
- `docs/api-contract.md`

Constraints:

- Public data only.
- No large raw datasets committed.
- County FIPS is the MVP join key.
- Preserve source provenance.
- Durable enrichment storage belongs in the Terraform-managed `mrisk` stack.
- Missing/ambiguous data returns reviewable status, not invented data.

Use tiny fixtures for tests.

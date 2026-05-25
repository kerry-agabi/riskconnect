# Prompt: Data Enrichment Slice

Use `data-enrichment-lead`.

Task: implement one public-data ingestion or enrichment slice.

Read:

- `docs/data-sources.md`
- `docs/api-contract.md`
- `docs/poc-e2e-implementation-prompts.md`

Constraints:

- Public data only.
- No large raw datasets committed.
- County FIPS is the MVP join key.
- Preserve source provenance.
- Durable enrichment storage belongs in the Terraform-managed `mrisk` stack.
- Use `backend/scripts/prepare_poc_data.py` for the small public PDF and LA County hazard seed path.
- Missing/ambiguous data returns reviewable status, not invented data.

Use tiny fixtures for tests.

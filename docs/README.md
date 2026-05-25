# RiskLens Product Overview

## Product Goal

RiskLens is a senior GenAI application developer practice project for an insurance and risk advisory environment. The MVP demonstrates an end-to-end AWS microservices pattern that is relevant to commercial insurance broking:

1. A broker uploads a property submission pack.
2. The system extracts location and exposure details.
3. The backend enriches the location with public US hazard data.
4. A Bedrock model generates a concise underwriting triage brief.
5. The broker reviews the brief, extracted fields, and data provenance.

## Document Index

- [Architecture](architecture.md)
- [API Contract](api-contract.md)
- [Public Data Sources](data-sources.md)
- [GenAI Design](genai-design.md)
- [AWS Infrastructure](aws-infrastructure.md)
- [DevOps](devops.md)
- [AWS CLI Setup In VS Code](aws-cli-vscode-setup.md)
- [GitHub CI/CD Setup](github-cicd-setup.md)
- [Claude Code Implementation Prompts](claude-code-implementation-prompts.md)
- [POC E2E Implementation Prompts](poc-e2e-implementation-prompts.md)
- [Security and Governance](security-governance.md)
- [Cost Plan](cost-plan.md)
- [Low-Budget AWS Notes](aws-free-tier-low-budget-notes.md)
- [Delivery Tasks](delivery-tasks.md)

## Target Users

- Commercial insurance brokers preparing market submissions.
- Underwriting assistants reviewing inbound submissions.
- Innovation teams demonstrating practical GenAI workflow automation.

## Demo Scenario

Use a synthetic property submission PDF for a US business location. The broker uploads the document and sees an immediate confirmation. Backend processing runs asynchronously and updates status from `QUEUED` to `READY`. The final screen shows:

- Extracted insured name, address, industry, property details, and limits.
- FEMA/NOAA/OpenFEMA hazard context for the county.
- AI-generated risk summary with red flags and missing information.
- Source links and confidence notes.

## MVP Success Criteria

- Upload starts in under 1 second from the frontend perspective.
- Backend can process a small PDF submission without blocking the UI.
- Risk enrichment works for a US address that resolves to county/FIPS.
- GenAI summary is structured, reviewable, and cites internal evidence fields.
- Infrastructure can deploy within a low AWS credit budget.
- CI validates frontend, backend, Docker, Lambda packaging, and Terraform configuration for the `mrisk` stack.

## What This MVP Is Not

- It is not a production Marsh or Marsh McLennan system.
- It must not process confidential client data.
- It is not a rating engine or bindable underwriting decision system.
- It is a proof of concept for triage, summarisation, and workflow automation.

#!/usr/bin/env python3
import aws_cdk as cdk


app = cdk.App()

# Stacks will be added during implementation:
# RiskLensWebStack(app, "RiskLensWebStack")
# RiskLensApiStack(app, "RiskLensApiStack")
# RiskLensProcessingStack(app, "RiskLensProcessingStack")
# RiskLensDataStack(app, "RiskLensDataStack")
# RiskLensObservabilityStack(app, "RiskLensObservabilityStack")

app.synth()


from fastapi import FastAPI

from risklens_api.api.submissions import router as submissions_router
from risklens_api.core.logging import setup_logging

setup_logging()

app = FastAPI(title="RiskLens API", version="0.1.0")
app.include_router(submissions_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

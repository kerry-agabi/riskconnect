FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY . .
RUN python -m pip install --upgrade pip && python -m pip install -e ".[dev]"

EXPOSE 8000
CMD ["uvicorn", "risklens_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

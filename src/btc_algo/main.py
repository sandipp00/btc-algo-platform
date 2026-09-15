from fastapi import FastAPI

from btc_algo.config import Settings

settings = Settings()
app = FastAPI(title="BTC Algo Platform", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": settings.mode.value}


@app.get("/ready")
def ready() -> dict[str, str]:
    settings.validate_live_gate()
    return {"status": "ready", "mode": settings.mode.value}

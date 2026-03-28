from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers import (
    agents,
    funding_orders,
    ledger,
    payment_requests,
    payouts,
    users,
    wallets,
    webhooks,
)
from app.config import get_settings

app = FastAPI(title="Alias Payments API")

_PUBLIC_PATHS = frozenset({"/", "/docs", "/openapi.json", "/redoc"})


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    settings = get_settings()
    if settings.agentpay_api_key is None:
        return await call_next(request)

    path = request.url.path
    if path in _PUBLIC_PATHS or path.startswith("/webhooks"):
        return await call_next(request)

    if request.headers.get("X-API-Key") != settings.agentpay_api_key:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or missing API key"},
        )
    return await call_next(request)


app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
app.include_router(
    funding_orders.router, prefix="/funding-orders", tags=["funding_orders"]
)
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(
    payment_requests.router, prefix="/payment-requests", tags=["payment_requests"]
)
app.include_router(payouts.router, prefix="/payouts", tags=["payouts"])
app.include_router(ledger.router, prefix="/ledger", tags=["ledger"])


@app.get("/")
def root():
    return {"message": "Hello World"}

from fastapi import FastAPI

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

app = FastAPI(title="Alias Payments API")

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

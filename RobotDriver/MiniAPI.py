from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from time import perf_counter
import os
from RobotDriver.Core.Session import BrowserSession
from RobotDriver.Service.Login import AuthService
from RobotDriver.Service.ProductPrice import CatalogService
from RobotDriver.Site.AutomationExercise import AutomationExerciseAdapter
from fastapi import Query
app = FastAPI(title="RobotDriver Mini API", version="1.0.0")

"""
FastAPI wrapper for the core automation.
"""

"""
Request for price.
"""
class PriceReq(BaseModel):
    email: str
    password: str
    product: str = Field(default="Blue Top")
    headless: bool = True
    auto_signup: bool = False

"""
Response schema for /price and /price/quick.
"""
class PriceResp(BaseModel):
    ok: bool
    product: str
    price: str | None = None
    found: bool
    login: bool
    elapsed_ms: float
    error: str | None = None

"""
Simple liveness probe used by local tests or container orchestration.
"""
@app.get("/health")
def health():
    return {"ok": True}

"""
Run the full flow: login → search → price extraction.
Raises HTTPException(500): For unexpected/unhandled exceptions.
"""
@app.post("/price", response_model=PriceResp)
def price(req: PriceReq):
    t0 = perf_counter()
    adapter = AutomationExerciseAdapter()
    try:
        with BrowserSession(headless=req.headless) as s:
            adapter.goto_home(s.page)
            login_ok = AuthService(adapter, s.page).login(
                req.email, req.password, auto_signup=req.auto_signup
            )
            if not login_ok:
                return PriceResp(
                    ok=False, product=req.product, price=None,
                    found=False, login=False, elapsed_ms=(perf_counter()-t0)*1000,
                    error="login_failed"
                )
            found, price = CatalogService(adapter, s.page).price_for(req.product)
            return PriceResp(
                ok=bool(found and price),
                product=req.product, price=price,
                found=found, login=True,
                elapsed_ms=(perf_counter()-t0)*1000,
                error=None if found and price else ("price_not_found" if found else "product_not_found")
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



"""
Convenience endpoint for demo/review.
"""
@app.get("/price/quick", response_model=PriceResp)
def price_quick(product: str = Query(..., description="Product name")):
    email = os.getenv("AE_EMAIL")
    password = os.getenv("AE_PASSWORD")
    if not email or not password:
        raise HTTPException(400, "Set AE_EMAIL and AE_PASSWORD env vars for quick endpoint.")
    # Reuse the main handler to keep the logic in one place
    return price(PriceReq(email=email, password=password, product=product, headless=True, auto_signup=False))
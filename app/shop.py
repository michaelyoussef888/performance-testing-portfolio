# ShopLite demo API: a small e-commerce backend used as the system under test.
import asyncio, random, hashlib, os
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI(title="ShopLite demo API")
TUNED = os.environ.get("TUNED") == "1"
POOL = asyncio.Semaphore(24 if TUNED else 3)      # simulated DB connection pool
PRODUCTS = [{"id": i, "name": f"Product {i}", "price": round(random.uniform(5, 500), 2)} for i in range(1, 2001)]
CACHE = {}
class CartItem(BaseModel):
    product_id: int
    qty: int = 1
from fastapi import HTTPException
async def db(ms):
    try:
        await asyncio.wait_for(POOL.acquire(), timeout=3.0)
    except asyncio.TimeoutError:
        raise HTTPException(503, "DB connection pool timeout")
    try:
        await asyncio.sleep(ms / 1000)
    finally:
        POOL.release()
@app.post("/api/login")
async def login():
    await db(random.uniform(8, 15)); return {"token": hashlib.md5(os.urandom(8)).hexdigest()}
@app.get("/api/products")
async def products(page: int = 1):
    await db(random.uniform(10, 25)); s = (page - 1) * 20; return PRODUCTS[s:s+20]
@app.get("/api/products/{pid}")
async def product(pid: int):
    if TUNED and pid in CACHE: return CACHE[pid]
    await db(random.uniform(5, 12)); CACHE[pid] = PRODUCTS[(pid - 1) % 2000]; return CACHE[pid]
@app.get("/api/search")
async def search(q: str = "1"):
    # unindexed scan: CPU work that blocks the event loop
    n = 20000 if not TUNED else 2000
    h = q.encode()
    for _ in range(n): h = hashlib.sha1(h).digest()
    await db(random.uniform(10, 20))
    return [p for p in PRODUCTS if q in p["name"]][:20]
@app.post("/api/cart")
async def cart(item: CartItem):
    await db(random.uniform(10, 20)); return {"ok": True}
@app.post("/api/checkout")
async def checkout():
    await db(random.uniform(60, 120) if not TUNED else random.uniform(30, 50))
    return {"order": random.randint(10**6, 10**7)}

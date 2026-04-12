from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, analytics, transactions, budgets, savings
import httpx

app = FastAPI(title="Finance Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Reporting & Analytics"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["Budgets"])
app.include_router(savings.router, prefix="/api/savings", tags=["Savings Goals"])

@app.post("/api/ai/ask")
async def ask_ai(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json"
            },
            json=body,
            timeout=30
        )
        return response.json()

@app.get("/")
def health_check():
    return {"status": "Operational", "service": "Finance API Engine"}
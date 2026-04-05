from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, analytics

app = FastAPI(title="Finance Tracker API", version="1.0.0")

# Configure CORS for Frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Reporting & Analytics"])
# Add other routers (transactions, budgets) here...

@app.get("/")
def health_check():
    return {"status": "Operational", "service": "Finance API Engine"}
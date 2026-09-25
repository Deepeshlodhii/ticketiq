from fastapi import FastAPI

from app.api.feedback import router as feedback_router
from app.api.status import router as status_router
from app.api.tickets import router as ticket_router
from app.storage import init_db

app = FastAPI(
    title="TicketIQ",
    description="Self-Optimizing Support Triage Agent",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(ticket_router)
app.include_router(feedback_router)
app.include_router(status_router)


@app.get("/")
def root():
    return {
        "service": "TicketIQ",
        "status": "running",
    }

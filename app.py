
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment configuration before importing the backend.
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from backend import run_travel_agent


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="KK Travel Planner",
    description="Multi-agent travel planning with LangGraph",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class TravelRequest(BaseModel):
    query: str = Field(min_length=5, max_length=2000)
    thread_id: str | None = None


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "KK Travel Planner"},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "KK Travel Planner"}


@app.post("/api/plan")
async def plan_trip(payload: TravelRequest):
    try:
        result = run_travel_agent(
            user_input=payload.query.strip(),
            thread_id=payload.thread_id,
        )
        return {
            "thread_id": result.get("thread_id"),
            "answer": result.get("answer", ""),
            "flight_results": result.get("flight_results", ""),
            "hotel_results": result.get("hotel_results", ""),
            "itinerary": result.get("itinerary", ""),
            "llm_calls": result.get("llm_calls", 0),
        }
    except Exception:
        # Keep internal errors and credentials out of the API response.
        raise HTTPException(
            status_code=500,
            detail="Unable to generate the travel plan. Check the server logs.",
        )

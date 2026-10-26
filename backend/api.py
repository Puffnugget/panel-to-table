import os
from typing import Literal, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from food import FoodLookupError, lookup_food
from parse_pdf import parse_pdf_bytes
from rules import analyze_payload
from spoonacular import SpoonacularError, generate_day

app = FastAPI(title="Panel to Table")

origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MarkerIn(BaseModel):
    id: str
    value: float
    unit: str
    lab_low: Optional[float] = None
    lab_high: Optional[float] = None


class FoodIn(BaseModel):
    barcode: Optional[str] = None
    query: Optional[str] = None


class MealPlanIn(BaseModel):
    age: int = Field(ge=1, le=120)
    sex: Literal["female", "male"]
    test_date: str
    fasting: bool
    markers: list[MarkerIn] = Field(min_length=1, max_length=8)
    diet: Optional[str] = None
    intolerances: list[str] = Field(default_factory=list)

    @field_validator("test_date")
    @classmethod
    def real_meal_date(cls, value: str) -> str:
        from datetime import date

        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("test_date must be YYYY-MM-DD") from exc
        return value


class AnalyzeIn(BaseModel):
    age: int = Field(ge=1, le=120)
    sex: Literal["female", "male"]
    test_date: str
    fasting: bool
    markers: list[MarkerIn] = Field(min_length=1, max_length=8)

    @field_validator("test_date")
    @classmethod
    def real_date(cls, value: str) -> str:
        from datetime import date

        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("test_date must be YYYY-MM-DD") from exc
        return value


@app.get("/")
async def root():
    return {"message": "Panel to Table reads blood test numbers and suggests food and activity ideas."}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/food")
async def food(body: FoodIn):
    # The barcode or name is forwarded to Open Food Facts and is not logged or stored.
    try:
        return await lookup_food(body.barcode, body.query)
    except FoodLookupError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.post("/meal-plan")
async def meal_plan(body: MealPlanIn):
    # The test and the diet boxes are forwarded to Spoonacular and are not logged or stored.
    try:
        analyzed = analyze_payload(body.model_dump())
        meals = await generate_day(analyzed["results"], body.diet, body.intolerances)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except SpoonacularError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return {"meals": meals}


@app.post("/analyze")
def analyze(body: AnalyzeIn):
    # Request bodies are not logged. History stays in the browser.
    try:
        return analyze_payload(body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/parse-report")
async def parse_report(file: UploadFile = File(...)):
    # The file is read in memory and discarded. It is not stored or logged.
    filename = (file.filename or "").lower()
    if not filename.endswith(".pdf"):
        return {
            "ok": False,
            "message": "We couldn't read this one; enter the values by hand.",
            "candidates": [],
            "missing": [],
        }
    data = await file.read()
    if len(data) > 8 * 1024 * 1024:
        return {
            "ok": False,
            "message": "We couldn't read this one; enter the values by hand.",
            "candidates": [],
            "missing": [],
        }
    return parse_pdf_bytes(data)

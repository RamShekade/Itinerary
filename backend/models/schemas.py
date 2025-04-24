# models/schemas.py

from pydantic import BaseModel
from typing import List

class ItineraryRequest(BaseModel):
    timeAvailable: int
    budget: int
    preferredPlaces: List[str]

class ItineraryItem(BaseModel):
    day: str
    place: str
    timeSpent: str
    entryFee: str
    cabCost: str
    notes: str

class ItinerarySummary(BaseModel):
    totalCabCost: str
    totalEntryFee: str
    totalEstimatedCost: str

class ItineraryResponse(BaseModel):
    itinerary: List[ItineraryItem]
    summary: ItinerarySummary

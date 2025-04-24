from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import random
from datetime import datetime, timedelta

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---- Models ----

class ItineraryRequest(BaseModel):
    timeAvailable: int
    budget: int
    preferredPlaces: List[str]

class Activity(BaseModel):
    time: str
    activity: str
    location: str
    isEcoFriendly: bool

class ItineraryDay(BaseModel):
    day: int
    activities: List[Activity]

class ItineraryResponse(BaseModel):
    itinerary: List[ItineraryDay]
    totalCabCost: str
    totalEntryFee: str
    totalEstimatedCost: str

# ---- Mock Activity Data ----

place_activities = {
    "Amber Fort": [
        {"activity": "Visit the Amber Fort", "location": "Amber Fort, Jaipur", "eco": True}
    ],
    "City Palace": [
        {"activity": "Explore City Palace", "location": "City Palace, Pink City", "eco": True}
    ],
    "Chokhi Dhani": [
        {"activity": "Dinner at traditional Rajasthani restaurant", "location": "Chokhi Dhani", "eco": False}
    ],
    "Nahargarh Fort": [
        {"activity": "Sunset at Nahargarh Fort", "location": "Nahargarh Fort", "eco": True},
        {"activity": "Cultural show and dinner", "location": "Nahargarh Fort", "eco": False}
    ],
    "Anokhi Cafe": [
        {"activity": "Lunch at organic cafe", "location": "Anokhi Cafe", "eco": True}
    ],
    "Sanganer Village": [
        {"activity": "Textile workshop with local artisans", "location": "Sanganer village", "eco": True},
        {"activity": "Pottery workshop", "location": "Sanganer crafts village", "eco": True}
    ],
    "Galtaji Temple": [
        {"activity": "Visit Galtaji Temple (Monkey Temple)", "location": "Galtaji, Jaipur", "eco": True}
    ],
    "Jantar Mantar": [
        {"activity": "Visit Jantar Mantar", "location": "Jantar Mantar, Pink City", "eco": True}
    ],
    "Spice Court": [
        {"activity": "Lunch at Spice Court", "location": "Spice Court, Civil Lines", "eco": True}
    ],
    "Johari Bazaar": [
        {"activity": "Shop at local artisan market", "location": "Johari Bazaar", "eco": True}
    ],
    "Jal Mahal": [
        {"activity": "Morning yoga session", "location": "Jal Mahal garden", "eco": True}
    ],
    "Peacock Rooftop Restaurant": [
        {"activity": "Farewell dinner at rooftop restaurant", "location": "Peacock Rooftop Restaurant", "eco": False}
    ]
}

entry_fees = {
    "Amber Fort": 25,
    "City Palace": 30,
    "Chokhi Dhani": 100,
    "Nahargarh Fort": 50,
    "Anokhi Cafe": 0,
    "Sanganer Village": 0,
    "Galtaji Temple": 10,
    "Jantar Mantar": 20,
    "Spice Court": 0,
    "Johari Bazaar": 0,
    "Jal Mahal": 0,
    "Peacock Rooftop Restaurant": 0
}

# ---- Helper ----

def generate_daily_activities(selected_places, days):
    itinerary = []
    start_time = datetime.strptime("09:00", "%H:%M")
    activities_per_day = max(3, len(selected_places) // days + 1)

    flat_activities = []
    for place in selected_places:
        if place in place_activities:
            flat_activities.extend(place_activities[place])

    random.shuffle(flat_activities)

    idx = 0
    for day in range(1, days + 1):
        day_activities = []
        time_cursor = start_time

        for _ in range(min(activities_per_day, len(flat_activities) - idx)):
            act = flat_activities[idx]
            formatted_time = time_cursor.strftime("%I:%M %p")
            day_activities.append(Activity(
                time=formatted_time,
                activity=act["activity"],
                location=act["location"],
                isEcoFriendly=act["eco"]
            ))
            time_cursor += timedelta(hours=2)
            idx += 1

        itinerary.append(ItineraryDay(day=day, activities=day_activities))

        if idx >= len(flat_activities):
            break

    return itinerary

# ---- Main Endpoint ----
@app.post("/generate-itinerary", response_model=ItineraryResponse)
def generate_itinerary(data: ItineraryRequest):
    if not data.timeAvailable or not data.budget or not data.preferredPlaces:
        raise HTTPException(status_code=400, detail="Missing fields.")

    num_days = max(1, data.timeAvailable // 8)
    selected_places = data.preferredPlaces

    # Collect all activities for the given preferred places
    flat_activities = []
    for place in selected_places:
        activities = place_activities.get(place, [])
        flat_activities.extend(activities)

    # If no activities found from preferred places, use all places
    if not flat_activities:
        for activities in place_activities.values():
            flat_activities.extend(activities)

    # Shuffle to keep variety
    random.shuffle(flat_activities)

    # Now build the itinerary by distributing activities per day
    itinerary = []
    start_time = datetime.strptime("09:00", "%H:%M")
    idx = 0
    per_day = max(4, len(flat_activities) // num_days)

    for day in range(1, num_days + 1):
        activities = []
        time_cursor = start_time

        for _ in range(per_day):
            if idx >= len(flat_activities):
                break

            act = flat_activities[idx]
            activities.append(Activity(
                time=time_cursor.strftime("%I:%M %p"),
                activity=act["activity"],
                location=act["location"],
                isEcoFriendly=act["eco"]
            ))
            time_cursor += timedelta(hours=2)
            idx += 1

        itinerary.append(ItineraryDay(day=day, activities=activities))

    # Calculate dummy costs
    total_entry = sum(entry_fees.get(place, 0) for place in selected_places)
    total_cab = len(itinerary) * 300

    return ItineraryResponse(
        itinerary=itinerary,
        totalCabCost=f"₹{total_cab}",
        totalEntryFee=f"₹{total_entry}",
        totalEstimatedCost=f"₹{total_cab + total_entry}"
    )

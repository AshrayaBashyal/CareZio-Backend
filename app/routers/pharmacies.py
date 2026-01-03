from fastapi import APIRouter, Query
from typing import List
from app.schemas import Pharmacy  # make sure you have a Pharmacy Pydantic model like Hospital

router = APIRouter(
    prefix="/pharmacies",
    tags=["Pharmacies"]
)

# Predefined dataset (example)
pharmacy_data = [
    {
        "name": "Health Plus Pharmacy",
        "address": "Kathmandu, Nepal",
        "phone": ["+9779800000001", "+9779800000002"],
        "pharmacists": ["Pharmacist Sita", "Pharmacist Ram"],
        "open_hours": "08:00 - 21:00",
        "image_url": "https://example.com/health_plus.jpg"
    },
    {
        "name": "MediCare Pharmacy",
        "address": "Lalitpur, Nepal",
        "phone": ["+9779800000010"],
        "pharmacists": ["Pharmacist Anil", "Pharmacist Sunita"],
        "open_hours": "09:00 - 20:00",
        "image_url": "https://example.com/medicare.jpg"
    },
    {
        "name": "City Care Pharmacy",
        "address": "Bhaktapur, Nepal",
        "phone": ["+9779800000020"],
        "pharmacists": ["Pharmacist Suman"],
        "open_hours": "07:00 - 19:00",
        "image_url": "https://example.com/citycare.jpg"
    },
    {
        "name": "LifeLine Pharmacy",
        "address": "Pokhara, Nepal",
        "phone": ["+9779800000030", "+9779800000031"],
        "pharmacists": ["Pharmacist Rajesh", "Pharmacist Meena"],
        "open_hours": "08:30 - 22:00",
        "image_url": "https://example.com/lifeline.jpg"
    },
    {
        "name": "Sunrise Pharmacy",
        "address": "Biratnagar, Nepal",
        "phone": ["+9779800000040"],
        "pharmacists": ["Pharmacist Anil", "Pharmacist Laxmi"],
        "open_hours": "09:00 - 21:00",
        "image_url": "https://example.com/sunrise.jpg"
    },
    {
        "name": "HealthCare Plus",
        "address": "Janakpur, Nepal",
        "phone": ["+9779800000050", "+9779800000051"],
        "pharmacists": ["Pharmacist Ramesh", "Pharmacist Sita"],
        "open_hours": "08:00 - 20:00",
        "image_url": "https://example.com/healthcare_plus.jpg"
    },
    {
        "name": "City Pharmacy",
        "address": "Dharan, Nepal",
        "phone": ["+9779800000060"],
        "pharmacists": ["Pharmacist Sunil", "Pharmacist Rekha"],
        "open_hours": "07:00 - 19:00",
        "image_url": "https://example.com/city_pharmacy.jpg"
    },
    {
        "name": "Golden Care Pharmacy",
        "address": "Hetauda, Nepal",
        "phone": ["+9779800000070", "+9779800000071"],
        "pharmacists": ["Pharmacist Prativa", "Pharmacist Suman"],
        "open_hours": "09:00 - 21:00",
        "image_url": "https://example.com/golden_care.jpg"
    },
]

@router.get("/", response_model=List[Pharmacy])
def get_pharmacies(
    query: str = Query(None, description="Search by pharmacy name or address")
):
    """
    Get list of pharmacies. Optionally filter by a search query (case-insensitive).
    """
    if not query:
        return pharmacy_data

    query_lower = query.lower()
    results = [
        p for p in pharmacy_data
        if query_lower in p["name"].lower() or query_lower in p["address"].lower()
    ]
    return results

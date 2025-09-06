from fastapi import APIRouter, Query
from app.schemas import Hospital
from typing import List

router = APIRouter(
    prefix="/hospitals",
    tags=["Hospitals"]
)


@router.get("/", response_model=List[Hospital])
def get_hospitals(query: str = Query(None, description="Search by hospital name or address")):
    """
    Get list of hospitals. Optionally filter by a search query (case-insensitive).
    """
    if not query:
        return hospital_data
    query_lower = query.lower()
    results = [
        h for h in hospital_data
        if query_lower in h["name"].lower() or query_lower in h["address"].lower()
    ]
    return results


hospital_data = [
    {
        "name": "Lumbini Provincial Hospital",
        "address": "Butwal, Rupandehi",
        "phone": ["+977071123456", "+977071123457"],
        "ambulances": 5,
        "doctors": ["Dr. Sudarshan Thapa", "Dr. Ramesh Koirala"],
        "nurses": ["Nurse Maya", "Nurse Rekha"],
        "ambulance_driver_phone": ["+9779812340001", "+9779812340002"],
        "ambulance_driver_address": ["Butwal, Rupandehi", "Butwal, Rupandehi"],
        "image_url": "https://www.lphospital.gov.np/public/uploads/sliders/mnMz5lEdPHQJ9qHU.jpg"
    },
    {
        "name": "Palpa Hospital",
        "address": "Silikhantole, Tansen Municipality, Palpa",
        "phone": ["+977075123456", "+977075123457"],
        "ambulances": 3,
        "doctors": ["Dr. Sunil Lama", "Dr. Prativa Thapa"],
        "nurses": ["Nurse Sita", "Nurse Binita"],
        "ambulance_driver_phone": ["+9779812340010"],
        "ambulance_driver_address": ["Tansen, Palpa"],
        "image_url": "https://palpahospital.gov.np/images/hospital.jpg"
    },
    {
        "name": "Rapti Provincial Hospital",
        "address": "Tulsipur Sub-Metropolitan, Dang",
        "phone": ["+977082123456", "+977082123457"],
        "ambulances": 4,
        "doctors": ["Dr. Anil Gurung", "Dr. Ritu Adhikari"],
        "nurses": ["Nurse Shristi", "Nurse Bipana"],
        "ambulance_driver_phone": ["+9779812340020", "+9779812340021"],
        "ambulance_driver_address": ["Dang, Tulsipur", "Dang, Tulsipur"],
        "image_url": "https://rph.lumbini.gov.np/images/hospital.jpg"
    },
    {
        "name": "Siddharthanagar City Hospital",
        "address": "Siddharthanagar, Rupandehi",
        "phone": ["+977071223344", "+977071223345"],
        "ambulances": 2,
        "doctors": ["Dr. Rajesh KC", "Dr. Meena Shrestha"],
        "nurses": ["Nurse Tara", "Nurse Laxmi"],
        "ambulance_driver_phone": ["+9779812340030"],
        "ambulance_driver_address": ["Siddharthanagar, Rupandehi"],
        "image_url": "https://cityhospital.com.np/images/hospital.jpg"
    },
    {
        "name": "Lumbini Medical College & Teaching Hospital",
        "address": "Lumbini Medical College Campus, Palpa",
        "phone": ["+977075223344", "+977075223345"],
        "ambulances": 3,
        "doctors": ["Dr. Suman Adhikari", "Dr. Rekha Rana"],
        "nurses": ["Nurse Anita", "Nurse Sushma"],
        "ambulance_driver_phone": ["+9779812340040"],
        "ambulance_driver_address": ["Palpa, Tansen"],
        "image_url": "https://www.lmc.edu.np/images/hospital.jpg"
    },
    {
        "name": "B.P. Koirala Institute of Health Sciences",
        "address": "Dharan, Sunsari",
        "phone": ["+977025123456", "+977025123457"],
        "ambulances": 10,
        "doctors": ["Dr. Ramesh Koirala", "Dr. Sita Koirala"],
        "nurses": ["Nurse Maya", "Nurse Rekha"],
        "ambulance_driver_phone": ["+9779812340001", "+9779812340002"],
        "ambulance_driver_address": ["Dharan, Sunsari", "Dharan, Sunsari"],
        "image_url": "https://www.bpkihs.edu/images/hospital.jpg"
    },
    {
        "name": "Golden Hospital Pvt. Ltd",
        "address": "Biratnagar, Morang",
        "phone": ["+977021123456", "+977021123457"],
        "ambulances": 5,
        "doctors": ["Dr. Sunil Lama", "Dr. Prativa Thapa"],
        "nurses": ["Nurse Sita", "Nurse Binita"],
        "ambulance_driver_phone": ["+9779812340010"],
        "ambulance_driver_address": ["Biratnagar, Morang"],
        "image_url": "https://www.goldenhospital.com.np/images/hospital.jpg"
    },
    {
        "name": "Nobel Medical College Teaching Hospital",
        "address": "Biratnagar, Morang",
        "phone": ["+977021223344", "+977021223345"],
        "ambulances": 6,
        "doctors": ["Dr. Anil Gurung", "Dr. Ritu Adhikari"],
        "nurses": ["Nurse Shristi", "Nurse Bipana"],
        "ambulance_driver_phone": ["+9779812340020", "+9779812340021"],
        "ambulance_driver_address": ["Biratnagar, Morang", "Biratnagar, Morang"],
        "image_url": "https://www.nobelmedicalcollege.edu.np/images/hospital.jpg"
    },
    {
        "name": "United Mission Hospital Tansen",
        "address": "Tansen, Palpa",
        "phone": ["+977075323344", "+977075323345"],
        "ambulances": 4,
        "doctors": ["Dr. Rajesh KC", "Dr. Meena Shrestha"],
        "nurses": ["Nurse Tara", "Nurse Laxmi"],
        "ambulance_driver_phone": ["+9779812340030"],
        "ambulance_driver_address": ["Tansen, Palpa"],
        "image_url": "https://www.umn.org.np/umht/images/hospital.jpg"
    },
    {
        "name": "B & C Medical College Teaching Hospital",
        "address": "Birtamode, Jhapa",
        "phone": ["+977023123456", "+977023123457"],
        "ambulances": 3,
        "doctors": ["Dr. Suman Adhikari", "Dr. Rekha Rana"],
        "nurses": ["Nurse Anita", "Nurse Sushma"],
        "ambulance_driver_phone": ["+9779812340040"],
        "ambulance_driver_address": ["Birtamode, Jhapa"],
        "image_url": "https://www.bcmc.edu.np/images/hospital.jpg"
    },
    {
        "name": "Janakpur Provincial Hospital",
        "address": "Janakpur, Dhanusha",
        "phone": ["+977041123456", "+977041123457"],
        "ambulances": 5,
        "doctors": ["Dr. Ramesh Koirala", "Dr. Sita Koirala"],
        "nurses": ["Nurse Maya", "Nurse Rekha"],
        "ambulance_driver_phone": ["+9779812340001", "+9779812340002"],
        "ambulance_driver_address": ["Janakpur, Dhanusha", "Janakpur, Dhanusha"],
        "image_url": "https://www.janakpurdhamhospital.gov.np/images/hospital.jpg"
    },
    {
        "name": "Narayani Hospital",
        "address": "Birgunj, Parsa",
        "phone": ["+977051123456", "+977051123457"],
        "ambulances": 6,
        "doctors": ["Dr. Sunil Lama", "Dr. Prativa Thapa"],
        "nurses": ["Nurse Sita", "Nurse Binita"],
        "ambulance_driver_phone": ["+9779812340010"],
        "ambulance_driver_address": ["Birgunj, Parsa"],
        "image_url": "https://www.narayanihospital.gov.np/images/hospital.jpg"
    },
    {
        "name": "Gajendra Narayan Singh Hospital",
        "address": "Rajbiraj, Saptari",
        "phone": ["+977031123456", "+977031123457"],
        "ambulances": 4,
        "doctors": ["Dr. Anil Gurung", "Dr. Ritu Adhikari"],
        "nurses": ["Nurse Shristi", "Nurse Bipana"],
        "ambulance_driver_phone": ["+9779812340020", "+9779812340021"],
        "ambulance_driver_address": ["Rajbiraj, Saptari", "Rajbiraj, Saptari"],
        "image_url": "https://www.gnsghospital.gov.np/images/hospital.jpg"
    },
    {
        "name": "Bhardaha Hospital",
        "address": "Bhardaha, Saptari",
        "phone": ["+977031223344", "+977031223345"],
        "ambulances": 3,
        "doctors": ["Dr. Rajesh KC", "Dr. Meena Shrestha"],
        "nurses": ["Nurse Tara", "Nurse Laxmi"],
        "ambulance_driver_phone": ["+9779812340030"],
        "ambulance_driver_address": ["Bhardaha, Saptari"],
        "image_url": "https://www.bhardahahospital.gov.np/images/hospital.jpg"
    },
    {
        "name": "Pokhariya Hospital",
        "address": "Pokhariya, Parsa",
        "phone": ["+977051223344", "+977051223345"],
        "ambulances": 2,
        "doctors": ["Dr. Suman Adhikari", "Dr. Rekha Rana"],
        "nurses": ["Nurse Anita", "Nurse Sushma"],
        "ambulance_driver_phone": ["+9779812340040"],
        "ambulance_driver_address": ["Pokhariya, Parsa"],
        "image_url": "https://www.pokhariyahospital.gov.np/images/hospital.jpg"
    }
]
from fastapi import APIRouter, Query
from app.schemas import Hospital
from typing import List

router = APIRouter(
    prefix="/hospitals",
    tags=["Hospitals"]
)


hospital_data= [
  {
    "name": "Lumbini Provincial Hospital",
    "address": "Butwal, Rupandehi",
    "ambulances": 5,
    "doctors": ["Dr. Sudarshan Thapa", "Dr. Ramesh Koirala"],
    "nurses": ["Nurse Maya", "Nurse Rekha"],
    "ambulance_driver_phone": ["+9779812340001", "+9779812340002"],
    "image_url": "https://www.lphospital.gov.np/public/uploads/sliders/mnMz5lEdPHQJ9qHU.jpg"
  },
  {
    "name": "Palpa Hospital",
    "address": "Silikhantole, Tansen Municipality, Palpa",
    "ambulances": 3,
    "doctors": ["Dr. Sunil Lama", "Dr. Prativa Thapa"],
    "nurses": ["Nurse Sita", "Nurse Binita"],
    "ambulance_driver_phone": ["+9779812340010"],
    "image_url": "https://palpahospital.gov.np/images/hospital.jpg"
  },
  {
    "name": "Rapti Provincial Hospital",
    "address": "Tulsipur Sub-Metropolitan, Dang",
    "ambulances": 4,
    "doctors": ["Dr. Anil Gurung", "Dr. Ritu Adhikari"],
    "nurses": ["Nurse Shristi", "Nurse Bipana"],
    "ambulance_driver_phone": ["+9779812340020", "+9779812340021"],
    "image_url": "https://rph.lumbini.gov.np/images/hospital.jpg"
  },
  {
    "name": "Siddharthanagar City Hospital",
    "address": "Siddharthanagar, Rupandehi",
    "ambulances": 2,
    "doctors": ["Dr. Rajesh KC", "Dr. Meena Shrestha"],
    "nurses": ["Nurse Tara", "Nurse Laxmi"],
    "ambulance_driver_phone": ["+9779812340030"],
    "image_url": "https://cityhospital.com.np/images/hospital.jpg"
  },
  {
    "name": "Lumbini Medical College & Teaching Hospital",
    "address": "Lumbini Medical College Campus, Palpa",
    "ambulances": 3,
    "doctors": ["Dr. Suman Adhikari", "Dr. Rekha Rana"],
    "nurses": ["Nurse Anita", "Nurse Sushma"],
    "ambulance_driver_phone": ["+9779812340040"],
    "image_url": "https://www.lmc.edu.np/images/hospital.jpg"
  },
  {
    "name": "B.P. Koirala Institute of Health Sciences",
    "address": "Dharan, Sunsari",
    "ambulances": 10,
    "doctors": ["Dr. Ramesh Koirala", "Dr. Sita Koirala"],
    "nurses": ["Nurse Maya", "Nurse Rekha"],
    "ambulance_driver_phone": ["+9779812340001", "+9779812340002"],
    "image_url": "https://www.bpkihs.edu/images/hospital.jpg"
  },
  {
    "name": "Golden Hospital Pvt. Ltd",
    "address": "Biratnagar, Morang",
    "ambulances": 5,
    "doctors": ["Dr. Sunil Lama", "Dr. Prativa Thapa"],
    "nurses": ["Nurse Sita", "Nurse Binita"],
    "ambulance_driver_phone": ["+9779812340010"],
    "image_url": "https://www.goldenhospital.com.np/images/hospital.jpg"
  },
  {
    "name": "Nobel Medical College Teaching Hospital",
    "address": "Biratnagar, Morang",
    "ambulances": 6,
    "doctors": ["Dr. Anil Gurung", "Dr. Ritu Adhikari"],
    "nurses": ["Nurse Shristi", "Nurse Bipana"],
    "ambulance_driver_phone": ["+9779812340020", "+9779812340021"],
    "image_url": "https://www.nobelmedicalcollege.edu.np/images/hospital.jpg"
  },
  {
    "name": "United Mission Hospital Tansen",
    "address": "Tansen, Palpa",
    "ambulances": 4,
    "doctors": ["Dr. Rajesh KC", "Dr. Meena Shrestha"],
    "nurses": ["Nurse Tara", "Nurse Laxmi"],
    "ambulance_driver_phone": ["+9779812340030"],
    "image_url": "https://www.umn.org.np/umht/images/hospital.jpg"
  },
  {
    "name": "B & C Medical College Teaching Hospital",
    "address": "Birtamode, Jhapa",
    "ambulances": 3,
    "doctors": ["Dr. Suman Adhikari", "Dr. Rekha Rana"],
    "nurses": ["Nurse Anita", "Nurse Sushma"],
    "ambulance_driver_phone": ["+9779812340040"],
    "image_url": "https://www.bcmc.edu.np/images/hospital.jpg"
  },
  {
    "name": "Janakpur Provincial Hospital",
    "address": "Janakpur, Dhanusha",
    "ambulances": 5,
    "doctors": ["Dr. Ramesh Koirala", "Dr. Sita Koirala"],
    "nurses": ["Nurse Maya", "Nurse Rekha"],
    "ambulance_driver_phone": ["+9779812340001", "+9779812340002"],
    "image_url": "https://www.janakpurdhamhospital.gov.np/images/hospital.jpg"
  },
  {
    "name": "Narayani Hospital",
    "address": "Birgunj, Parsa",
    "ambulances": 6,
    "doctors": ["Dr. Sunil Lama", "Dr. Prativa Thapa"],
    "nurses": ["Nurse Sita", "Nurse Binita"],
    "ambulance_driver_phone": ["+9779812340010"],
    "image_url": "https://www.narayanihospital.gov.np/images/hospital.jpg"
  },
  {
    "name": "Gajendra Narayan Singh Hospital",
    "address": "Rajbiraj, Saptari",
    "ambulances": 4,
    "doctors": ["Dr. Anil Gurung", "Dr. Ritu Adhikari"],
    "nurses": ["Nurse Shristi", "Nurse Bipana"],
    "ambulance_driver_phone": ["+9779812340020", "+9779812340021"],
    "image_url": "https://www.gnsghospital.gov.np/images/hospital.jpg"
  },
  {
    "name": "Bhardaha Hospital",
    "address": "Bhardaha, Saptari",
    "ambulances": 3,
    "doctors": ["Dr. Rajesh KC", "Dr. Meena Shrestha"],
    "nurses": ["Nurse Tara", "Nurse Laxmi"],
    "ambulance_driver_phone": ["+9779812340030"],
    "image_url": "https://www.bhardahahospital.gov.np/images/hospital.jpg"
  },
  {
    "name": "Pokhariya Hospital",
    "address": "Pokhariya, Parsa",
    "ambulances": 2,
    "doctors": ["Dr. Suman Adhikari", "Dr. Rekha Rana"],
    "nurses": ["Nurse Anita", "Nurse Sushma"],
    "ambulance_driver_phone": ["+9779812340040"],
    "image_url": "https://www.pokhariyahospital.gov.np/images/hospital.jpg"
  }
]









@router.get("/hospitals", response_model=List[Hospital])
def get_hospitals(query: str = Query(None, description="Search by hospital name or address")):
    if not query:
        return hospital_data
    query_lower = query.lower()
    results = [
        h for h in hospital_data
        if query_lower in h["name"].lower() or query_lower in h["address"].lower()
    ]
    return results
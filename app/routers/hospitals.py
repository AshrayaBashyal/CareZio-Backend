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
        "image_url": "https://lh3.googleusercontent.com/gps-cs-s/AC9h4npho-zKE8MZUI-uBbXN2-x5VFl8m6wGsVW3EwDiViGm0eASOL7TkmT4W6xdOx31Nq_Ex_fJJqymkAmID46NGlgfW62UeRQjqDhP21XK_9bsf0e-7mq7oPdN9fR1_9C20US3-5A=s1360-w1360-h1020-rw"
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
        "image_url": "https://lh3.googleusercontent.com/gps-cs-s/AC9h4nqzXSm8TTH3pnYFOmJ_8fbeF9f9mI5_1Y7tO57m249ywzqZL3vRoIWktfdvxGl_ClCdKbP48nQ2CKuciDBr7x398Is-vE4eCx9T7dfojjU-ZlkDHs6QAr5CMO1sdCePL9LidR4=s1360-w1360-h1020-rw"
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
        "image_url": "https://cityhospital.com.np/public/storage/settings/January2022/D0BsQs7szdXRtmdTLr0p.jpg"
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
        "image_url": "https://prolineconsultancy.com/wp-content/uploads/2019/05/IMG_20170606_224657-696x414.jpg"
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
        "image_url": "https://bpkihs.edu/assets/images/BPKIHS520X320.jpg"
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
        "image_url": "https://lh3.googleusercontent.com/gps-cs-s/AC9h4nr3wEPy7pr5O6WoEV1Y8Dc8azQC_KsKArnD7gsuC8GOcz5jxuh1VJNxLOqwAIN3p-SUp71UmdQbNGUA4W67rhU5RCDSegb1ZiZjPYTD5qoN-vHXZlUlqrYztcJAfWtFo6XjtjLt=s1360-w1360-h1020-rw"
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
        "image_url": "https://www.nobelmedicalcollege.com.np/uploads/slider/Z8csoGqZHYyTOGxoV3ZOSUBTp2cWK2gYnX3VV8Eo.webp"
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
        "image_url": "https://i0.wp.com/www.umn.org.np/wp-content/uploads/2023/03/tansenhosp-500x320.jpg"
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
        "image_url": "https://bnchospital.edu.np/images/bnc_about.jpg"
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
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Provincial_Hospital%2C_Janakpur.jpg/500px-Provincial_Hospital%2C_Janakpur.jpg"
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
        "image_url": "https://giwmscdntwo.gov.np/media/carousels/Hospital%20Image%203_htkf32a.jpeg"
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
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTr-JRqaI7ylAoKeg2Z4zHfXBohMGv9RqWcKw&s"
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
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRUQLiXD68Kk-A2gs_a5enRaS6kU-_7_MFSmg&s"
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
        "image_url": "https://thehimalayantimes.com/thehimalayantimes/uploads/images/2024/11/22/36077.jpg"
    }
]
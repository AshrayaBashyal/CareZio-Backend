import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_medical_file(file):
    result = cloudinary.uploader.upload(
        file,
        folder="carezio/medical_records",
        resource_type="auto"
    )
    return result["secure_url"], result["format"]

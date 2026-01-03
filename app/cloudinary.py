import cloudinary
import cloudinary.uploader
import os

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
API_KEY = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if CLOUD_NAME and API_KEY and API_SECRET:
    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=API_KEY,
        api_secret=API_SECRET,
        secure=True
    )

def upload_medical_file(file):
    if not CLOUD_NAME or not API_KEY or not API_SECRET:
        # dummy response for development
        return "https://dummy.cloudinary.com/file.pdf", "pdf"

    result = cloudinary.uploader.upload(
        file,
        folder="carezio/medical_records",
        resource_type="auto"
    )
    return result["secure_url"], result["format"]

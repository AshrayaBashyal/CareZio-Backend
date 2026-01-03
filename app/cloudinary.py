import cloudinary
import cloudinary.uploader
from app.config import settings

# Configure Cloudinary if keys exist
if all([settings.cloudinary_cloud_name, settings.cloudinary_api_key, settings.cloudinary_api_secret]):
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

def upload_medical_file(file):
    """
    Upload a file to Cloudinary and return its URL and type.
    Returns a dummy URL if keys are missing (development fallback).
    """
    if not all([settings.cloudinary_cloud_name, settings.cloudinary_api_key, settings.cloudinary_api_secret]):
        return "https://dummy.cloudinary.com/file.pdf", "pdf"

    result = cloudinary.uploader.upload(
        file,
        folder="carezio/medical_records",
        resource_type="auto"
    )

    return result.get("secure_url"), result.get("format", "unknown")


def delete_medical_file(file_url):
    """
    Delete a file from Cloudinary using its URL.
    Returns True if deletion succeeded, False otherwise.
    """
    if not all([settings.cloudinary_cloud_name, settings.cloudinary_api_key, settings.cloudinary_api_secret]):
        # Nothing to delete in dev mode
        return True

    try:
        # Extract public_id from URL
        # Assumes URL structure: https://res.cloudinary.com/<cloud_name>/.../carezio/medical_records/<filename>.<ext>
        parts = file_url.split("/")
        filename_with_ext = parts[-1]
        folder_path = "/".join(parts[-2:-1])  # "carezio/medical_records" or adjust if needed
        public_id = f"carezio/medical_records/{filename_with_ext.split('.')[0]}"

        cloudinary.uploader.destroy(public_id, resource_type="auto", type="authenticated")
        return True
    except Exception:
        return False
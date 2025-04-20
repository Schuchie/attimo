from pathlib import Path
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS
from PIL.TiffImagePlugin import IFDRational
import os
import json
import uuid
from datetime import datetime

class ImageProvider:
    
    def __init__(self,  root_dir: Path = None , config_provider=None):
        self.config_provider = config_provider
        self.upload_folder = Path.joinpath(root_dir, "static", "uploads")
        self.raw_folder = self.upload_folder / "raw"
        self.preview_folder = self.upload_folder / "preview"
        self.image_data_file = self.upload_folder / "image_metadata.json"
        self.load()

    def load(self):
        # Load images from JSON file
        if self.image_data_file.exists():
            with open(self.image_data_file, "r") as f:
                try:
                    self.images = json.load(f)
                    print(f"[ImageProvider] Loaded {len(self.images['images'])} images from {self.image_data_file}")
                except json.JSONDecodeError as e:
                    print(f"[ImageProvider] Failed to load image data: {e}")
                    self.images = {}
        else:
            print(f"[ImageProvider] No image data file found at {self.image_data_file}")
            self.images = {
                "images": {},
            }
    
    def save(self):
        # Save images to JSON file
        with open(self.image_data_file, "w") as f:
            json.dump(self.images, f, indent=2)
            print(f"[ImageProvider] Saved {len(self.images)} image-metadata to {self.image_data_file}")

    def get_images(self):
        return self.images.get("images", {})

    def save_image(self, file):
        print(f"[ImageProvider] Saving image to {self.raw_folder}")

        original_filename = file.filename
        ext = os.path.splitext(original_filename)[1].lower()  # Preserve file extension
        uuid_filename = f"{uuid.uuid4().hex}{ext}"

        rawpath = os.path.join(self.raw_folder, uuid_filename)
        file.save(rawpath)

        readable_exif = {}

        # Create low-res preview
        os.makedirs(self.preview_folder, exist_ok=True)
        preview_path = os.path.join(self.preview_folder, uuid_filename)

        try:
            with Image.open(rawpath) as img:
                raw_exif = img.getexif()
                readable_exif = self.clean_exif_for_json(raw_exif)
                img = ImageOps.exif_transpose(img)
                img.thumbnail((600, 800))
                img.save(preview_path, optimize=True, quality=70)
                print(f"[ImageProvider] Created preview for {uuid_filename} at {preview_path}")
        except Exception as e:
            print(f"[ImageProvider] Failed to create preview for {uuid_filename}: {e}")
            raise e
        
        self.images["images"][uuid_filename] = {
            "raw": rawpath,
            "preview": preview_path,
            "attribute": self.extract_attribute_data(readable_exif, original_filename),
        }
        self.save()
        print(f"[ImageProvider] Image {original_filename} as {uuid_filename} saved successfully.")

    
    def clean_exif_for_json(self, exif_data):
        clean = {}

        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)

            try:
                # Convert IFDRational types to float
                if isinstance(value, IFDRational):
                    clean[tag_name] = float(value)

                # GPSInfo is a nested dict — you can optionally flatten/convert it
                elif isinstance(value, dict):
                    clean[tag_name] = self.clean_exif_for_json(value)

                # Convert all other unsupported types via str fallback
                elif isinstance(value, (bytes, bytearray)):
                    clean[tag_name] = value.decode(errors="ignore")
                else:
                    clean[tag_name] = value
            except Exception as e:
                clean[tag_name] = str(value)  # Fallback just in case

        return clean
    
    def extract_attribute_data(self, exif_data, original_filename):
        attributes = {
            "image": original_filename,
            "location": {},
            "created_datetime": None,
            "added_datetime": datetime.now().isoformat(),
            "raw_exif": exif_data
        }

        print(exif_data)
        exif_string = exif_data.get("DateTimeOriginal") or exif_data.get("DateTime")
    
        if exif_string and isinstance(exif_string, str):
            try:
                attributes["created_datetime"] = datetime.strptime(exif_string, "%Y:%m:%d %H:%M:%S").isoformat()
            except ValueError as e:
                print(f"[ImageProvider] Failed to parse EXIF datetime: {e}")
        
        return attributes
    
    def delete_image(self, filename):
        
        if filename in self.images["images"]:
            del self.images["images"][filename]
        filepath = os.path.join(self.raw_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        filepath = os.path.join(self.preview_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        self.save()
        print(f"[ImageProvider] Deleted image {filename} and its data.")
        


    
    
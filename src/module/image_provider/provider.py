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
        self.eink_folder = self.upload_folder / "eink"
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
        img_uuid = uuid.uuid4().hex
        uuid_filename = f"{img_uuid}.jpeg"

        rawpath = os.path.join(self.raw_folder, uuid_filename)
        os.makedirs(self.raw_folder, exist_ok=True)

        readable_exif = {}

        # Pfade für Vorschau und E-Ink
        os.makedirs(self.preview_folder, exist_ok=True)
        preview_path = os.path.join(self.preview_folder, uuid_filename)

        os.makedirs(self.eink_folder, exist_ok=True)
        eink_path = os.path.join(self.eink_folder, uuid_filename)

        try:
            with Image.open(file.stream) as img:
                # EXIF sichern (für JSON)
                raw_exif = img.getexif()
                readable_exif = self.clean_exif_for_json(raw_exif)

                # EXIF-bereinigtes Bild erzeugen
                img = ImageOps.exif_transpose(img).convert("RGB")

                # Vorschau speichern
                preview_img = img.copy()
                preview_img.thumbnail((400, 600))
                preview_img.save(preview_path, format="JPEG", optimize=True, quality=70)

                # E-Ink speichern
                eink_img = img.copy()
                eink_img.thumbnail((1200, 1600))
                eink_img.save(eink_path, format="JPEG", optimize=True, quality=85)

                # Raw abspeichern – EXIF entfernen
                img.save(rawpath, format="JPEG", optimize=True, quality=90)

                print(f"[ImageProvider] Saved preview and eink image for {uuid_filename}")

        except Exception as e:
            print(f"[ImageProvider] Failed to create preview for {uuid_filename}: {e}")
            raise e

        # Metadaten speichern
        self.images["images"][uuid_filename] = {
            "uuid": img_uuid,
            "raw": rawpath,
            "preview": preview_path,
            "eink": eink_path,
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
            "created_datetime": datetime.now().isoformat(),
            "added_datetime": datetime.now().isoformat(),
            "raw_exif": exif_data
        }
        
        exif_string = exif_data.get("DateTimeOriginal") or exif_data.get("DateTime")
    
        if exif_string and isinstance(exif_string, str):
            try:
                attributes["created_datetime"] = datetime.strptime(exif_string, "%Y:%m:%d %H:%M:%S").isoformat()
            except ValueError as e:
                print(f"[ImageProvider] Failed to parse EXIF datetime: {e}")
        
        return attributes
    
    def crop_image(self, filename: str, x: int, y: int, w: int, h: int, rotation: int = 0):
        uuid = Path(filename).stem
        raw_path = os.path.join(self.raw_folder, filename)
        preview_path = os.path.join(self.preview_folder, f"{uuid}.jpeg")
        eink_path = os.path.join(self.eink_folder, f"{uuid}.jpeg")

        with Image.open(raw_path) as img:
            img = ImageOps.exif_transpose(img).convert("RGB")

            if rotation:
                rotation_for_pillow = (360 - rotation) % 360
                print(f"[ImageProvider] Rotating image by {rotation_for_pillow} degrees (Cropper input: {rotation})")
                img = img.rotate(rotation_for_pillow, expand=True)


            cropped = img.crop((x, y, x + w, y + h))

            preview = cropped.copy()
            preview.thumbnail((400, 600))
            preview.save(preview_path, format="JPEG", optimize=True, quality=70)

            eink = cropped.copy()
            eink.thumbnail((1600, 1200))
            eink.save(eink_path, format="JPEG", optimize=True, quality=85)

        image_data = self.images["images"].get(filename, {})
        image_data.setdefault("attribute", {})["crop_rect"] = {
            "x": x, "y": y, "width": w, "height": h,
            "rotation": rotation
        }
        self.save()





    def get_crop_rect(self, uuid_filename: str):
        image_data = self.images["images"].get(uuid_filename)
        if not image_data:
            return None

        attributes = image_data.get("attribute", {})
        return attributes.get("crop_rect")



    def delete_image(self, file_uuid):
        
        filename = f"{file_uuid}.jpeg"
        if filename in self.images["images"]:
            del self.images["images"][filename]
        
        filepath = os.path.join(self.raw_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        filepath = os.path.join(self.preview_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        filepath = os.path.join(self.eink_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        self.save()
        print(f"[ImageProvider] Deleted image {filename} and its data.")
        


    
    
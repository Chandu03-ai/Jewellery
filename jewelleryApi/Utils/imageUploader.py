import os
from bson import ObjectId
from fastapi import UploadFile
from constants import staticImagesPath, staticOriginalPath
from yensiAuthentication import logger
from PIL import Image
import shutil
from PIL.Image import Resampling

staticOriginalPath = os.getenv("STATIC_ORIGINAL_PATH", staticOriginalPath)
staticImagesPath = os.getenv("STATIC_IMAGES_PATH", staticImagesPath)

os.makedirs(staticOriginalPath, exist_ok=True)
os.makedirs(staticImagesPath, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"jpg", "jpeg", "png","gif"}
MAX_WIDTH=1024

async def saveFile(file: UploadFile) -> str:
    uniqueId = str(ObjectId())
    originalExtension = file.filename.split('.')[-1].lower()
    fileExtension = "jpeg" if originalExtension in ALLOWED_IMAGE_TYPES else originalExtension
    fileName = f"{uniqueId}.{fileExtension}"
    originalFileLocation = os.path.join(staticOriginalPath, fileName)
    finalFileLocation = os.path.join(staticImagesPath, fileName)

    try:
        with open(originalFileLocation, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Original file saved successfully: {fileName}")

        if fileExtension in ALLOWED_IMAGE_TYPES:
            compressFile(originalFileLocation, finalFileLocation)
        else:
            shutil.copy(originalFileLocation, finalFileLocation)
            logger.info(f"Non-image file saved as is: {fileName}")

        return str(fileName)
    except Exception as e:
        logger.error(f"Error saving or compressing file {fileName}: {str(e)}")
        return None


def compressFile(filePath: str, finalFileLocation: str) -> str:
    try:
        with Image.open(filePath) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            # Resize the image while maintaining aspect ratio
            width_percent = (MAX_WIDTH / float(img.size[0]))
            height_size = int((float(img.size[1]) * float(width_percent)))
            img = img.resize((MAX_WIDTH, height_size), Resampling.LANCZOS)
            img.save(finalFileLocation, "JPEG", quality=95)
        logger.info(f"Compressed file saved at {finalFileLocation}")
    except Exception as e:
        logger.error(f"Error compressing file {filePath}: {str(e)}")
        raise

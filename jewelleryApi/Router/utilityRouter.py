# router/utilityRouter.py

from fastapi import APIRouter, UploadFile, File
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from Utils.imageUploader import saveFile

router = APIRouter(tags=["Utility"])


@router.post("/auth/upload-file")
async def uploadFile(file: UploadFile = File(...)):
    try:
        fileName = await saveFile(file)

        logger.info(f"File uploaded successfully: {fileName}")
        return returnResponse(2011, result=fileName)
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        return returnResponse(2012)

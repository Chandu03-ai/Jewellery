# router/utilityRouter.py
from typing import List
from fastapi import APIRouter, UploadFile, File
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from Utils.imageUploader import saveFile

router = APIRouter(tags=["Utility"])


@router.post("/upload-file")
async def uploadFile(file: UploadFile = File(...)):
    try:
        logger.debug(f"uploadFile function called ")
        fileName = await saveFile(file)
        logger.info(f"File uploaded successfully: {fileName}")
        return returnResponse(2011, result=fileName)
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        return returnResponse(2012)


@router.post("/upload-files")
async def uploadFiles(files: List[UploadFile] = File(...)):
    try:
        logger.debug(f"uploadFiles function called")
        uploadedFiles = []
        for file in files:
            fileName = await saveFile(file)
            if fileName:
                uploadedFiles.append(fileName)
            else:
                logger.warning(f"Skipping file due to processing error: {file.filename}")

        if not uploadedFiles:
            logger.warning("No files were uploaded successfully.")
            return returnResponse(2099)

        logger.info(f"Files uploaded successfully: {uploadedFiles}")
        return returnResponse(2100, result=uploadedFiles)

    except Exception as e:
        logger.error(f"Multiple file upload failed: {str(e)}")
        return returnResponse(2101)

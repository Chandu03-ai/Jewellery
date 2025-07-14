from fastapi import APIRouter, UploadFile, File
from Utils.productUtils import validateImportFile
from Database.productDb import productsCollection, importHistoryCollection
from datetime import datetime
import logging

router = APIRouter(prefix="/api/products", tags=["Products"])
logger = logging.getLogger("yensiProducts")


@router.post("/validate-import")
async def validateImport(file: UploadFile = File(...)):
    logger.info(f"Validating file: {file.filename}")
    result = validateImportFile(file)
    if result["success"]:
        return {"success": True, "message": "File is valid"}
    return {"success": False, "errors": result.get("missingColumns") or result.get("error")}


@router.post("/import")
async def importProducts(file: UploadFile = File(...)):
    logger.info(f"Importing products from file: {file.filename}")
    result = validateImportFile(file)

    if not result["success"]:
        return {"success": False, "errors": result.get("missingColumns") or result.get("error")}

    df = result["data"]
    importedCount = 0
    failedCount = 0

    for index, row in df.iterrows():
        try:
            product = {
                "name": row["name"],
                "category": row["category"],
                "description": row["description"],
                "price": float(row["price"]),
                "images": row["images"].split(","),
                "preorderAvailable": bool(row["preorderAvailable"]),
                "inStock": bool(row["inStock"]),
                "specifications": {"material": row["material"], "weight": row["weight"], "dimensions": row["dimensions"], "gemstone": row["gemstone"]},
                "rating": float(row.get("rating", 0)),
                "reviews": int(row.get("reviews", 0)),
                "featured": bool(row.get("featured", False)),
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }
            productsCollection.insert_one(product)
            importedCount += 1
        except Exception as e:
            logger.error(f"Failed to import row {index}: {e}")
            failedCount += 1

    importHistoryCollection.insert_one({"fileName": file.filename, "timestamp": datetime.utcnow(), "total": len(df), "imported": importedCount, "failed": failedCount})

    return {"success": True, "message": "Import completed", "imported": importedCount, "failed": failedCount}


@router.get("/import-history")
async def getImportHistory():
    history = list(importHistoryCollection.find({}, {"_id": 0}).sort("timestamp", -1))
    return {"success": True, "history": history}

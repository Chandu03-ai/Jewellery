import pandas as pd


REQUIRED_COLUMNS = [
    'name', 'category', 'description', 'price', 'images',
    'preorderAvailable', 'inStock', 'material', 'weight',
    'dimensions', 'gemstone', 'rating', 'reviews', 'featured'
]

def validateImportFile(file) -> dict:
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file)
        else:
            return {"success": False, "error": "Unsupported file format"}

        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            return {"success": False, "missingColumns": missing}
        return {"success": True, "data": df}
    except Exception as e:
        return {"success": False, "error": str(e)}

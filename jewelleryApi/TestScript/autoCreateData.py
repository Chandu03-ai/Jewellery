import os
import asyncio
from bson import ObjectId
import httpx
from testConfig import loginUrl, adminEmail, adminPassword, CATEGORY_URL, PRODUCT_URL, UPLOAD_URL

categories = [
    {"name": "Necklaces", "slug": "necklaces"},
    {"name": "Earrings", "slug": "earrings"},
    {"name": "Bracelets", "slug": "bracelets"},
    {"name": "Rings", "slug": "rings"},
]


def getImageFiles(limit=10):
    folder = "images"
    files = sorted(os.listdir(folder))
    imagePaths = [os.path.join(folder, file) for file in files if file.lower().endswith((".jpg", ".jpeg", ".png"))]
    return imagePaths[:limit] if len(imagePaths) >= limit else imagePaths * (limit // len(imagePaths) + 1)


async def login():
    loginData = {"username": adminEmail, "password": adminPassword}
    async with httpx.AsyncClient(follow_redirects=True) as client:
        res = await client.post(loginUrl, json=loginData)
        resJson = res.json()
        if resJson.get("code") == 1003:
            token = res.cookies.get("access_token")
            if not token:
                raise RuntimeError("Access token missing. Stopping execution.")
            print(f"✅ Login successful for {adminEmail}")
            return token
        else:
            print(f"❌ Login failed: {resJson.get('message')}")
            return None


async def uploadImages(client, cookies, imagePaths):
    uploadedNames = []
    for path in imagePaths:
        try:
            with open(path, "rb") as f:
                fileTuple = {"file": (os.path.basename(path), f, "image/jpeg")}
                res = await client.post(UPLOAD_URL, files=fileTuple, cookies=cookies)
                data = res.json()
                if data.get("code") == 2011:
                    uploadedNames.append(data["result"])
                    print(f"📤 Uploaded {path} → {data['result']}")
                else:
                    print(f"⚠️ Failed to upload {path}: {data.get('message')}")
        except Exception as e:
            print(f"🔥 Error uploading image {path}: {e}")
    return uploadedNames


async def createCategories(client, cookies, uploadedImages):
    created = []
    for idx, cat in enumerate(categories):
        imageName = uploadedImages[idx % len(uploadedImages)]
        payload = {"name": cat["name"], "slug": cat["slug"], "image": imageName, "parentId": str(ObjectId()), "isParent": True}
        try:
            res = await client.post(CATEGORY_URL, cookies=cookies, json=payload)
            data = res.json()
            if data.get("code") in [2020, 2023]:
                print(f"✔️ Category created/existing: {cat['name']}")
                created.append(data["result"]["slug"])
            else:
                print(f"❌ Category create failed: {cat['name']} → {data.get('message')}")
        except Exception as e:
            print(f"🔥 Exception in createCategories: {e}")
    return created


async def createProducts(client, cookies, categorySlugs, uploadedImages):
    for i in range(2):
        product = {
            "name": f"Product {i+1}",
            "slug": f"product-{i+1}",
            "category": categorySlugs[i % len(categorySlugs)],
            "description": f"Elegant handcrafted item {i+1}.",
            "initialPrice": 1000 + i * 100,
            "price": 1200 + i * 100,
            "comparePrice": 1500 + i * 100,
            "images": [uploadedImages[i % len(uploadedImages)]],
            "stock": True,
        }
        try:
            res = await client.post(PRODUCT_URL, cookies=cookies, json=product)
            data = res.json()
            if data.get("code") == 2001:
                print(f"🛒 Product created: {product['name']}")
            else:
                print(f"❌ Product failed: {product['name']} → {data.get('message')}")
        except Exception as e:
            print(f"🔥 Exception in createProducts: {e}")


async def main():
    accessToken = await login()
    if not accessToken:
        print("🔒 Invalid access token. Exiting.")
        return

    cookies = {"access_token": accessToken}
    imagePaths = getImageFiles()

    async with httpx.AsyncClient() as client:
        uploadedFileNames = await uploadImages(client, cookies, imagePaths)
        if not uploadedFileNames:
            print("⚠️ No images uploaded. Skipping creation.")
            return

        categorySlugs = await createCategories(client, cookies, uploadedFileNames)
        if categorySlugs:
            await createProducts(client, cookies, categorySlugs, uploadedFileNames)
        else:
            print("⚠️ No categories created. Exiting.")


if __name__ == "__main__":
    asyncio.run(main())

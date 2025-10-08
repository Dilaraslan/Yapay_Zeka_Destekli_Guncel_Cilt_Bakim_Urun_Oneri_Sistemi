#API kodu
#main.py
from fastapi import FastAPI, HTTPException, File, UploadFile, Query, Path
from pydantic import BaseModel
from typing import List, Optional, Dict
from dotenv import load_dotenv
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import requests
import logging
import os
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import io

#uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Import from our modules
from scrapers.trendyol import extract_trendyol_data, is_product_page, search_products

from data.skin_issues import (
    LABELS, THRESHOLDS, PRODUCT_KEYWORDS, PRODUCT_TYPES,
    SKIN_ISSUE_INFO, SkinIssueInfo, ProductResponse, SkinAnalysisResponse,
    AnalysisAndRecommendationResponse, SkinIssueWithProductsResponse
)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables (.env file)
load_dotenv("keys.env")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
if not SEARCH_API_KEY or not SEARCH_ENGINE_ID:
    raise RuntimeError("❌ API Keys not found.")

# FastAPI Application
app = FastAPI(title="Skincare AI API", description="AI-powered skin analysis and product recommendation API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mobil cihazdan test için tüm domainlere izin verir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model definition
MODEL_PATH = "75epoch-convnextbase.pth"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = models.convnext_base(weights=None)
model.classifier[2] = nn.Linear(model.classifier[2].in_features, len(LABELS))
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()

# Image transformation
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),  # Eğitimde böyleydi
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])


def extract_face_region(image_bytes: bytes) -> Optional[Image.Image]:
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            logging.error("Invalid image format")
            return None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        faces = face_cascade.detectMultiScale(
            image=gray,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(faces) == 0:
            logging.warning("No face detected.")
            return None

        # İlk yüzü kırp
        x, y, w, h = faces[0]
        face_crop = img[y:y + h, x:x + w]
        face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
        pil_face = Image.fromarray(face_rgb).convert("RGB")
        return pil_face

    except Exception as e:
        logging.error(f"Face extraction error: {str(e)}")
        return None


# Skin Analysis Function
async def analyze_skin(file: UploadFile) -> List[str]:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Lütfen bir resim dosyası yükleyin.")

    try:
        # Görseli oku
        image_bytes = await file.read()

        # Yüzü kırp
        face_image = extract_face_region(image_bytes)

        if face_image is None:
            raise HTTPException(status_code=400, detail="Fotoğrafta insan yüzü algılanamadı.")

        # Kırpılmış yüzü modele uygun hale getir
        image_tensor = transform(face_image).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(image_tensor)
            probs = torch.sigmoid(outputs).squeeze().cpu().numpy()
            logging.info(f"Tüm olasılıklar (sigmoid sonrası): {probs}")
            for i, p in enumerate(probs):
                logging.info(f"{LABELS[i]} olasılığı: {p:.4f}")

        # Eşiklere göre etiket belirleme
        detected = []
        for i, p in enumerate(probs):
            label = LABELS[i]
            threshold = THRESHOLDS.get(label, 0.5)
            if p > threshold:
                detected.append(label)

        return detected if detected else ["no_skin_issue_detected"]

    except Exception as e:
        logging.error(f"Model error: {e}")
        raise HTTPException(status_code=500, detail=f"Model hatası: {e}")


# Get product recommendations based on skin issues
async def get_recommendations(skin_issues, product_count=3, min_rating=None):
    recommendations = {}

    for issue in skin_issues:
        if issue in PRODUCT_KEYWORDS:
            # Get product types for this skin issue
            product_types = PRODUCT_TYPES.get(issue, [])

            # Get search keywords for this skin issue
            keywords = PRODUCT_KEYWORDS.get(issue, [])

            # Combine issue with product types for better search results
            if product_types:
                search_queries = [f"{keyword} {product_type}" for keyword in keywords[:2] for product_type in
                                  product_types[:2]]
                # Use the first few queries
                query = " OR ".join(search_queries[:6])  # veya [:8]

            else:
                # Just use keywords if no product types
                query = " OR ".join(keywords[:6])  # veya [:8]

            # Search for products
            products = search_products(query, count=product_count, min_rating=min_rating,
                                       search_api_key=SEARCH_API_KEY, search_engine_id=SEARCH_ENGINE_ID)
            recommendations[issue] = products

    return recommendations

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome! Visit /docs for API documentation."}

@app.post("/analyze", response_model=SkinAnalysisResponse)
async def analyze_endpoint(file: UploadFile = File(...)):
    detected = await analyze_skin(file)
    return SkinAnalysisResponse(detected_skin_issues=detected)

@app.get("/recommend", response_model=Dict[str, List[ProductResponse]])
async def recommend_products(
        skin_issue: str = Query(..., description="Skin issue type (acne, stain, wrinkle, black_circle, pockmark)"),
        product_count: int = Query(3, description="Number of products to recommend"),
        min_rating: Optional[float] = Query(None, description="Minimum product rating (0-5)")
):
    """
    Get product recommendations for a specific skin issue without requiring image analysis.
    This endpoint will be used when user clicks on a specific skin concern in the app.
    """
    # Validate the skin issue input
    if skin_issue not in LABELS and skin_issue != "no_skin_issue_detected":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid skin issue. Must be one of: {LABELS}"
        )

    # Get recommendations for the specific issue
    recommendations = await get_recommendations(
        [skin_issue],
        product_count=product_count,
        min_rating=min_rating
    )

    return recommendations

@app.post("/analyze-and-recommend", response_model=AnalysisAndRecommendationResponse)
async def analyze_and_recommend(
        file: UploadFile = File(...),
        product_count: int = Query(3, description="Number of products to recommend per skin issue"),
        min_rating: Optional[float] = Query(None, description="Minimum product rating (0-5)")
):
    # Analyze skin
    detected_issues = await analyze_skin(file)

    # Get product recommendations
    recommendations = await get_recommendations(
        detected_issues,
        product_count=product_count,
        min_rating=min_rating
    )

    return AnalysisAndRecommendationResponse(
        detected_skin_issues=detected_issues,
        recommended_products=recommendations
    )
from fastapi.responses import JSONResponse
import time

CACHE = {}
TTL_SECONDS = 3600  # Cache süresi: 1 saat

def is_cache_valid(timestamp):
    return (time.time() - timestamp) < TTL_SECONDS

@app.get("/skin-issue/products/{issue_type}", response_model=List[ProductResponse])
async def get_skin_issue_products_only(
    issue_type: str = Path(..., description="Cilt sorunu tipi"),
    product_count: int = Query(3, description="Önerilecek ürün sayısı"),
    min_rating: Optional[float] = Query(None, description="Minimum ürün puanı (0-5)")
):
    if issue_type not in LABELS:
        raise HTTPException(status_code=400, detail=f"Geçersiz cilt sorunu. Seçenekler: {LABELS}")

    rating_key = str(min_rating) if min_rating is not None else "default"
    cache_key = f"{issue_type}{product_count}{rating_key}"

    if cache_key in CACHE:
        products, timestamp = CACHE[cache_key]
        if is_cache_valid(timestamp):
            logging.info(f"[CACHE HIT] {cache_key}")
            return products
        else:
            logging.info(f"[CACHE EXPIRED] {cache_key}")

    # Yeni veri çek
    logging.info(f"[CACHE MISS] {cache_key} — Yeni veri çekiliyor...")
    recommendations = await get_recommendations(
        [issue_type],
        product_count=product_count,
        min_rating=min_rating
    )

    products = recommendations.get(issue_type, [])
    CACHE[cache_key] = (products, time.time())

    return products


@app.get("/skin-issue/info/{issue_type}", response_model=SkinIssueInfo)
async def get_skin_issue_info_only(issue_type: str = Path(..., description="Cilt sorunu tipi")):
    """
    Belirli bir cilt sorunu hakkında sadece bilgi (ürünsüz) döner.
    Bu endpoint mobil uygulamada detay sayfası için kullanılacak.
    """
    if issue_type not in SKIN_ISSUE_INFO:
        raise HTTPException(status_code=404, detail=f"{issue_type} için bilgi bulunamadı")

    return SKIN_ISSUE_INFO[issue_type]


# Skin issue info ve ürünler için endpoint
@app.get("/skin-issue/{issue_type}", response_model=SkinIssueWithProductsResponse)
async def get_skin_issue_info(
        issue_type: str = Path(..., description="Cilt sorunu tipi (acne, stain, wrinkle, black_circle, pockmark)"),
        product_count: int = Query(5, description="Önerilecek ürün sayısı"),
        min_rating: Optional[float] = Query(None, description="Minimum ürün puanı (0-5)")
):
    """
    Belirli bir cilt sorunu hakkında detaylı bilgi ve önerilen ürünleri getirir.
    Bu endpoint, kullanıcı ana ekranda bir cilt sorunu ikonuna tıkladığında kullanılacak.
    """
    # Cilt sorunu geçerliliğini kontrol et
    if issue_type not in LABELS:
        raise HTTPException(
            status_code=400,
            detail=f"Geçersiz cilt sorunu. Seçenekler: {LABELS}"
        )

    # Cilt sorunu bilgisini al
    if issue_type not in SKIN_ISSUE_INFO:
        raise HTTPException(
            status_code=404,
            detail=f"{issue_type} için bilgi bulunamadı"
        )

    # Bu sorun için ürün önerilerini al
    recommendations = await get_recommendations(
        [issue_type],
        product_count=product_count,
        min_rating=min_rating
    )

    products = recommendations.get(issue_type, [])

    return SkinIssueWithProductsResponse(
        info=SKIN_ISSUE_INFO[issue_type],
        products=products
    )

if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
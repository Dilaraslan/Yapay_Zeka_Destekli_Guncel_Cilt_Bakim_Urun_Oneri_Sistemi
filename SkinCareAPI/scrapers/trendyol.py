#trendyol.py
from pydantic import BaseModel
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import re
import json
import logging
import random


# Trendyol Scraper
def extract_trendyol_data(url):
    product = {
        "name": None,
        "purchase_link": url,
        "price": None,
        "rating": None,
        "image_url": None,
        "brand": None  # Marka bilgisini ekliyoruz
    }
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            logging.error(f"Could not access URL: {url}, Status code: {response.status_code}")
            return product

        soup = BeautifulSoup(response.text, "html.parser")

        # Product name
        for selector in [
            ".pr-new-br", ".prdct-desc-cntnr-name", "h1.pr-new-br",
            ".product-name", ".product-detail-name"
        ]:
            name_elem = soup.select_one(selector)
            if name_elem:
                product["name"] = name_elem.get_text(strip=True)
                break

        # Price
        for selector in [
            ".prc-dsc", ".product-price", ".price-container",
            ".pr-bx-w .prc-dsc", ".pr-bx-nm .prc-dsc",
            ".pr-bx-w .prc-org", "[data-testid='price-current-price']",
            ".product-price-container .prc-dsc"
        ]:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = re.sub(r'[^\d,.]', '', price_elem.get_text(strip=True))
                product["price"] = price_text
                break

        # Rating
        for selector in [
            ".tltp-avg", ".rating-score", ".star-w .rt",
            "[data-testid='rating-score']"
        ]:
            rating_elem = soup.select_one(selector)
            if rating_elem:
                try:
                    rating_text = rating_elem.get_text(strip=True).replace(',', '.')
                    match = re.search(r'\d+\.\d+|\d+', rating_text)
                    if match:
                        product["rating"] = float(match.group())
                        break
                except:
                    pass

        # Image
        for selector in [
            ".product-slide img", ".gallery-modal-content img",
            ".base-product-image", ".product-img",
            "[data-testid='product-image']", ".ph-gl-img"
        ]:
            img_elem = soup.select_one(selector)
            if img_elem and img_elem.has_attr("src"):
                img_url = img_elem["src"]
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                product["image_url"] = img_url
                break

        # Brand - Marka bilgisini çıkarmak için eklendi
        for selector in [
            ".pr-new-br", ".prdct-desc-cntnr-ttl",
            ".product-brand", ".brand-name"
        ]:
            brand_elem = soup.select_one(selector)
            if brand_elem:
                product["brand"] = brand_elem.get_text(strip=True)
                break

        # Marka bilgisini ürün adından çıkarmayı dene
        if not product["brand"] and product["name"]:
            first_word = product["name"].split()[0]
            # Genellikle ilk kelime markadır
            if len(first_word) > 2:  # Çok kısa değilse
                product["brand"] = first_word

        # JSON-LD
        json_ld = soup.find("script", {"type": "application/ld+json"})
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if not product["name"] and "name" in data:
                    product["name"] = data["name"]
                if not product["price"] and "offers" in data and "price" in data["offers"]:
                    product["price"] = str(data["offers"]["price"])
                if not product["rating"] and "aggregateRating" in data and "ratingValue" in data["aggregateRating"]:
                    product["rating"] = float(data["aggregateRating"]["ratingValue"])
                if not product["image_url"] and "image" in data:
                    product["image_url"] = data["image"]
                if not product["brand"] and "brand" in data and "name" in data["brand"]:
                    product["brand"] = data["brand"]["name"]
            except Exception as e:
                logging.error(f"JSON-LD parsing error: {e}")

        return product
    except Exception as e:
        logging.error(f"Trendyol data extraction error: {e}")
        return product


def is_product_page(url: str) -> bool:
    # URL'nin gerçek bir ürün sayfası olduğunu anlamak için
    return any(part in url for part in ["/p-", "-p-", "/urun/", "/product/"])


def search_products(query, count=3, min_rating=None, search_api_key=None, search_engine_id=None):
    try:
        # Add 'trendyol' to search query to limit results to Trendyol
        search_query = f"{query} site:trendyol.com"
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            "key": search_api_key,
            "cx": search_engine_id,
            "q": search_query,
            "num": min(count * 5, 10)  # Daha fazla sonuç alacağız
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            logging.error(f"Search API error: {response.status_code}")
            return []

        results = response.json()
        if "items" not in results:
            logging.warning("No search results found")
            # Black-circle için özel sorgular ekleyelim
            if "black_circle" in query.lower() or "göz altı" in query.lower():
                alt_queries = [
                    "göz altı morluk kremi site:trendyol.com",
                    "göz altı halkası kremi site:trendyol.com",
                    "dark circle eye cream site:trendyol.com",
                    "göz çevresi bakım kremi site:trendyol.com"
                ]
                # Rastgele bir alternatif sorgu seç
                alt_query = random.choice(alt_queries)
                alt_params = params.copy()
                alt_params["q"] = alt_query

                alt_response = requests.get(url, params=alt_params)
                if alt_response.status_code == 200 and "items" in alt_response.json():
                    results = alt_response.json()
                else:
                    return []
            else:
                return []

        # Extract only valid product detail URLs
        product_urls = [
            item["link"]
            for item in results["items"]
            if "trendyol.com" in item["link"] and is_product_page(item["link"])
        ]

        # Benzersiz ürün URL'lerini topla
        unique_urls = list(set(product_urls))

        # URL'leri karıştıralım - böylece farklı sıralamalarda ürünler görebiliriz
        random.shuffle(unique_urls)

        # Get product details
        products = []
        seen_names = set()  # Aynı isimli ürünleri engellemek için
        seen_brands = set()  # Farklı markalardan ürün toplamak için

        for url in unique_urls:
            product = extract_trendyol_data(url)
            # Sadece ismi olan ve daha önce aynı isimde ürün eklenmemiş olanları dahil et
            if product["name"] and product["name"] not in seen_names:
                # Eğer bu markanın 2 ürününü zaten eklemişsek, bu markayı atla
                if product["brand"] and product["brand"] in seen_brands and list(seen_brands).count(
                        product["brand"]) >= 2:
                    continue

                if min_rating is None or (product["rating"] is not None and product["rating"] >= min_rating):
                    products.append(product)
                    seen_names.add(product["name"])
                    if product["brand"]:
                        seen_brands.add(product["brand"])
                    if len(products) >= count:
                        break

        # Yeterince ürün bulunamadıysa, alternatif arama sorguları deneyelim
        if len(products) < count:
            # Alternatif arama sorguları - daha geniş terimlerle arama
            alt_queries = []

            # Black-circle için özel sorgular
            if "black_circle" in query.lower() or "göz altı" in query.lower():
                alt_queries = [
                    "göz altı bakım kremi trendyol",
                    "göz çevresi bakım kremi trendyol",
                    "göz altı morluk kremi trendyol"
                ]
            # Akne için özel sorgular
            elif "acne" in query.lower() or "akne" in query.lower():
                alt_queries = [
                    "akne karşıtı krem trendyol",
                    "sivilce kremi trendyol",
                    "akne bakım seti trendyol"
                ]
            # Kırışıklık için özel sorgular
            elif "wrinkle" in query.lower() or "kırışık" in query.lower():
                alt_queries = [
                    "kırışıklık karşıtı krem trendyol",
                    "anti aging krem trendyol",
                    "yaşlanma karşıtı serum trendyol"
                ]
            # Leke için özel sorgular
            elif "stain" in query.lower() or "leke" in query.lower():
                alt_queries = [
                    "leke karşıtı krem trendyol",
                    "cilt lekesi kremi trendyol",
                    "leke giderici serum trendyol"
                ]
            # Gözenek için özel sorgular
            elif "pockmark" in query.lower() or "gözenek" in query.lower():
                alt_queries = [
                    "gözenek sıkılaştırıcı krem trendyol",
                    "gözenek bakım kremi trendyol",
                    "gözenek minimizer trendyol"
                ]
            # Genel sorgu
            else:
                alt_queries = [
                    f"{query.split()[0]} cilt bakım trendyol",
                    f"{query.split()[0]} yüz bakım trendyol",
                    f"{query.split()[0]} dermokozmeti̇k trendyol"
                ]

            # Rastgele bir alternatif sorgu seç
            random.shuffle(alt_queries)

            for alt_query in alt_queries:
                if len(products) >= count:
                    break

                alt_params = params.copy()
                alt_params["q"] = alt_query

                alt_response = requests.get(url, params=alt_params)
                if alt_response.status_code == 200 and "items" in alt_response.json():
                    alt_urls = [
                        item["link"]
                        for item in alt_response.json()["items"]
                        if "trendyol.com" in item["link"] and is_product_page(item["link"])
                           and item["link"] not in unique_urls  # Daha önce bakılmamış URL'ler
                    ]

                    # URL'leri karıştıralım
                    random.shuffle(alt_urls)

                    for alt_url in alt_urls:
                        if len(products) >= count:
                            break

                        product = extract_trendyol_data(alt_url)
                        if product["name"] and product["name"] not in seen_names:
                            # Eğer bu markanın 2 ürününü zaten eklemişsek, bu markayı atla
                            if product["brand"] and product["brand"] in seen_brands and list(seen_brands).count(
                                    product["brand"]) >= 2:
                                continue

                            if min_rating is None or (
                                    product["rating"] is not None and product["rating"] >= min_rating):
                                products.append(product)
                                seen_names.add(product["name"])
                                if product["brand"]:
                                    seen_brands.add(product["brand"])

        return products[:count]  # Return requested number of products
    except Exception as e:
        logging.error(f"Product search error: {e}")
        return []
 #skin_issues.py
from pydantic import BaseModel
from typing import List, Optional, Dict

# Request and Response Models
class ProductResponse(BaseModel):
    name: Optional[str] = None
    purchase_link: str
    price: Optional[str] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None


class ProductsRequest(BaseModel):
    urls: List[str]


class SkinAnalysisResponse(BaseModel):
    detected_skin_issues: List[str]


class RecommendationRequest(BaseModel):
    skin_issues: List[str]
    product_count: int = 3
    min_rating: Optional[float] = None


class AnalysisAndRecommendationResponse(BaseModel):
    detected_skin_issues: List[str]
    recommended_products: Dict[str, List[ProductResponse]]


# Skin issue information model
class SkinIssueInfo(BaseModel):
    title: str
    description: str
    causes: List[str]
    daily_care: List[str]
    tips: List[str]


class SkinIssueWithProductsResponse(BaseModel):
    info: SkinIssueInfo
    products: List[ProductResponse]


# Labels and thresholds for the model
LABELS = ["acne", "pockmark", "stain", "wrinkle", "black_circle","healthy"]

THRESHOLDS = {
    "acne": 0.5,
    "pockmark": 0.5,
    "stain": 0.92,
    "wrinkle": 0.96,
    "black_circle": 0.5
}

# Product recommendation mapping
PRODUCT_KEYWORDS = {
    "acne": ["acne", "sivilce", "akne", "siyah nokta", "cilt lekesi", "blemish"],
    "pockmark": ["çukur", "yara izi", "iz", "scar", "gözenek", "pore", "pockmark"],
    "stain": ["leke", "ton eşitsizliği", "pigment", "stain", "dark spot", "hiperpigmentasyon"],
    "wrinkle": ["kırışıklık", "ince çizgi", "yaşlanma", "anti-aging", "sıkılaştırıcı", "wrinkle"],
    "black_circle": [
        "göz altı morluk kremi", "aydınlatıcı göz kremi", "göz torbası",
        "göz altı serum", "eye brightening cream", "göz çevresi aydınlatıcı"
    ],
    "healthy": ["nemlendirici", "günlük bakım", "hassas cilt", "moisturizer", "hydrating"]
}

# Product recommendation options by skin issue
PRODUCT_TYPES = {
    "acne": ["Akne Serumu", "Salisilik Asit", "Çay Ağacı Yağı", "Akne Temizleyici", "Siyah Nokta Maskesi"],
    "pockmark": ["Retinol", "Vitamin C", "Peptit", "Hyaluronik Asit", "Kolajen"],
    "stain": ["Leke Kremi", "Aydınlatıcı Serum", "Vitamin C", "AHA", "Kojik Asit"],
    "wrinkle": ["Retinol", "Peptit Serum", "Kolajen", "Anti-aging Krem", "Sıkılaştırıcı"],
    "black_circle": ["Göz Kremi", "Kafein İçerikli", "Hyaluronik Asit", "Vitamin K", "Retinol"],
    "healthy": ["Nemlendirici", "Güneş Koruyucu", "Temizleyici", "Tonik", "Serum"]
}

# Skin issue information
SKIN_ISSUE_INFO = {
    "acne": SkinIssueInfo(
        title="Akne",
        description="Akne, kıl foliküllerinin yağ bezleri ile tıkanması sonucu oluşan yaygın bir cilt sorunudur. Sivilceler, siyah noktalar, beyaz noktalar ve daha büyük, kırmızı, ağrılı şişlikler şeklinde görülebilir.",
        causes=[
            "Aşırı yağ üretimi",
            "Ölü deri hücrelerinin birikmesi",
            "Bakteriyel enfeksiyon",
            "Hormonel değişimler",
            "Stres",
            "Genetik faktörler",
        ],
        daily_care=[
            "Salisilik asit içeren temizleyici kullanın",
            "Yağsız nemlendirici tercih edin",
            "Yüzünüzü günde en fazla 2 kez yıkayın",
            "Sivilceleri sıkmaktan kaçının",
        ],
        tips=[
            "Saç ürünlerinin cildinize temas etmesini engelleyin",
            "Yastık kılıflarınızı düzenli olarak değiştirin",
            "Telefonunuzu düzenli temizleyin",
            "Makyaj ürünlerinde 'komedojenik olmayan' etiketini arayın",
        ],
    ),
    "pockmark": SkinIssueInfo(
        title="Gözenek",
        description="Gözenekler, ciltteki yağ bezlerinin çıkışlarıdır. Genişlemiş gözenekler genellikle yağlı cilt tiplerinde daha belirgin olur.",
        causes=[
            "Aşırı yağ üretimi",
            "Genetik faktörler",
            "Yaşlanma",
            "Güneş hasarı",
            "Hormonal değişimler",
            "Düzensiz cilt bakımı",
        ],
        daily_care=[
            "BHA (Salisilik asit) içeren ürünler kullanın",
            "Kil maskeleri uygulayın",
            "Gözenek sıkılaştırıcı tonikler tercih edin",
            "Yağsız nemlendirici kullanın",
        ],
        tips=[
            "Makyaj temizliğine özen gösterin",
            "Komedojenik olmayan ürünler tercih edin",
            "Cildinizi ovmayın, nazikçe yıkayın",
            "Güneş koruyucu kullanımını ihmal etmeyin",
        ],
    ),
    "stain": SkinIssueInfo(
        title="Leke",
        description="Cilt lekeleri, güneş hasarı, hormonel değişimler veya sivilce izleri gibi nedenlerle ciltte oluşan pigment değişimleridir.",
        causes=[
            "Güneş hasarı",
            "Hormonel değişimler",
            "Akne izleri",
            "Yaşlanma",
            "Genetik faktörler",
            "İlaçlar",
        ],
        daily_care=[
            "Aydınlatıcı özellikteki C vitamini serumları kullanın",
            "AHA/BHA içeren ürünlerle ölü deri hücrelerini uzaklaştırın",
            "Her gün SPF 30+ güneş koruyucu kullanın",
            "Gece niasinamid içeren ürünler uygulayın",
        ],
        tips=[
            "Lekelere dokunmaktan kaçının",
            "Limon, sirke gibi ev yapımı çözümlerden uzak durun",
            "İyileşme sürecine zaman tanıyın",
            "Düzenli cilt bakımını ihmal etmeyin",
        ],
    ),
    "wrinkle": SkinIssueInfo(
        title="Kırışıklık",
        description="Kırışıklıklar, yaşlanma, güneş hasarı ve diğer faktörler nedeniyle cildin elastikiyetini kaybetmesi sonucu oluşan çizgilerdir.",
        causes=[
            "Yaşlanma",
            "Ultraviyole ışınlarına maruz kalma",
            "Sigara kullanımı",
            "Tekrarlanan yüz ifadeleri",
            "Yetersiz nem ve beslenme",
            "Genetik faktörler",
        ],
        daily_care=[
            "Retinol içeren ürünler kullanın",
            "Peptitler ve antioksidanlar içeren serumlar uygulayın",
            "Nemlendiriciyle cildinizi besleyin",
            "SPF 30+ güneş koruyucu kullanın",
        ],
        tips=[
            "Yüzünüzü yukarı doğru dairesel hareketlerle masaj yapın",
            "Yeterli su için",
            "Yeterli uyku alın",
            "C vitamini açısından zengin besinler tüketin",
        ],
    ),
    "black_circle": SkinIssueInfo(
        title="Koyu Halka",
        description="Göz altı koyu halkaları, genetik faktörler, yaşlanma, yorgunluk ve kan dolaşımı sorunları nedeniyle oluşabilir.",
        causes=[
            "Genetik yatkınlık",
            "Yetersiz uyku",
            "Yaşlanma",
            "Alerjiler ve göz yorgunluğu",
            "Kan dolaşımı sorunları",
            "Güneş hasarı",
        ],
        daily_care=[
            "Kafein içeren göz kremleri kullanın",
            "Hyaluronik asit ve peptit içeren ürünlerle nemlenin",
            "K vitamini içeren göz kremleri tercih edin",
            "Her gün güneş koruyucu kullanın",
        ],
        tips=[
            "Göz çevrenize nazikçe masaj yapın",
            "Soğuk kompres uygulayın",
            "Yeterli su için",
            "Uyku düzeninize dikkat edin",
        ],
    ),
}
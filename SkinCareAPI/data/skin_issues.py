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


# Labels and thresholds for ConvNeXt model (6 classes)
LABELS = ["acne", "pockmark", "stain", "wrinkle", "black_circle", "healthy"]

# Updated thresholds based on your training results
THRESHOLDS = {
    "acne": 0.5,
    "pockmark": 0.5,
    "stain": 0.92,        # High threshold as in your training
    "wrinkle": 0.9997,    # Very high threshold as in your training
    "black_circle": 0.5,
    "healthy": 0.5,
}


# Product recommendation mapping - Updated with healthy
PRODUCT_KEYWORDS = {
    "acne": ["acne", "sivilce", "akne", "siyah nokta", "cilt lekesi", "blemish"],
    "pockmark": ["çukur", "yara izi", "iz", "scar", "gözenek", "pore", "pockmark"],
    "stain": ["leke", "ton eşitsizliği", "pigment", "stain", "dark spot", "hiperpigmentasyon"],
    "wrinkle": ["kırışıklık", "ince çizgi", "yaşlanma", "anti-aging", "sıkılaştırıcı", "wrinkle"],
    "black_circle": [
        "göz altı morluk kremi", "aydınlatıcı göz kremi", "göz torbası",
        "göz altı serum", "eye brightening cream", "göz çevresi aydınlatıcı"
    ],
    "healthy": ["nemlendirici", "günlük bakım", "hassas cilt", "moisturizer", "hydrating", "koruyucu"],
    "no_skin_issue_detected": ["nemlendirici", "günlük bakım", "hassas cilt", "moisturizer", "hydrating"]
}

# Product recommendation options by skin issue - Updated with healthy
PRODUCT_TYPES = {
    "acne": ["Akne Serumu", "Salisilik Asit", "Çay Ağacı Yağı", "Akne Temizleyici", "Siyah Nokta Maskesi"],
    "pockmark": ["Retinol", "Vitamin C", "Peptit", "Hyaluronik Asit", "Kolajen"],
    "stain": ["Leke Kremi", "Aydınlatıcı Serum", "Vitamin C", "AHA", "Kojik Asit"],
    "wrinkle": ["Retinol", "Peptit Serum", "Kolajen", "Anti-aging Krem", "Sıkılaştırıcı"],
    "black_circle": ["Göz Kremi", "Kafein İçerikli", "Hyaluronik Asit", "Vitamin K", "Retinol"],
    "healthy": ["Nemlendirici", "Güneş Koruyucu", "Temizleyici", "Tonik", "Hafif Serum"],
    "no_skin_issue_detected": ["Nemlendirici", "Güneş Koruyucu", "Temizleyici", "Tonik", "Serum"]
}

# Skin issue information - HEALTHY EKLEME
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
    "healthy": SkinIssueInfo(
        title="Sağlıklı Cilt",
        description="Tebrikler! Cildiniz sağlıklı görünüyor. Bu durumu korumak için düzenli bakım rutininizi sürdürün.",
        causes=[
            "Düzenli cilt bakımı",
            "Sağlıklı beslenme",
            "Yeterli su tüketimi",
            "Güneş korunması",
            "İyi uyku düzeni",
            "Stres yönetimi",
        ],
        daily_care=[
            "Nazik temizleyici ile yıkayın",
            "Nemlendirici kullanın",
            "Güneş koruyucu uygulayın",
            "Haftalık maske yapın",
        ],
        tips=[
            "Mevcut rutininizi koruyun",
            "Cildinizi günlük gözlemleyin",
            "Yeni ürünleri dikkatli deneyin",
            "Sağlıklı yaşam tarzınızı sürdürün",
        ],
    ),
}
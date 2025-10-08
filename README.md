# Yapay Zeka Destekli Güncel Cilt Bakım Ürün Öneri Sistemi

## Proje Hakkında
Bu proje, yapay zeka teknolojileri kullanarak cilt sorunlarını otomatik olarak tespit eden ve kullanıcılara kişiselleştirilmiş kozmetik ürün önerileri sunan entegre bir sistemdir.  
Erciyes Üniversitesi Bilgisayar Mühendisliği Bölümü bitirme projesi olarak geliştirilmiş ve TÜBİTAK 2209-A programı tarafından desteklenmiştir.

## Özellikler

### Yapay Zeka Destekli Cilt Analizi
- Yüz görüntülerinden akne, leke, kırışıklık, koyu halka ve sivilce izi gibi cilt sorunlarını tespit eder.

### Kişiselleştirilmiş Ürün Önerileri
- Tespit edilen cilt sorunlarına göre Trendyol üzerinden güncel kozmetik ürünleri önerir.

### Kullanıcı Dostu Mobil Uygulama
- React Native ile geliştirilmiş, hem Android hem iOS platformlarında çalışır.

### Yüksek Doğruluk Oranı
- ConvNeXt tabanlı derin öğrenme modeliyle %90.05 doğruluk oranı sağlar.

### Hızlı Yanıt Süresi
- Önbellekleme mekanizması ile optimize edilmiş performans sunar.

## Teknik Detaylar

### Kullanılan Teknolojiler

**Backend**
- Python 3.x
- FastAPI: REST API geliştirme
- PyTorch: Derin öğrenme modeli
- ConvNeXt: Önceden eğitilmiş CNN mimarisi
- OpenCV: Görüntü işleme ve yüz tespiti
- BeautifulSoup: Web scraping
- Google Custom Search API: Ürün arama

**Frontend (Mobil Uygulama)**
- React Native
- TypeScript
- react-native-vision-camera: Kamera erişimi
- react-native-image-crop-picker: Görsel seçimi

### Model Performans Metrikleri
| Metrik       | Değer   |
| ------------ | ------- |
| Doğruluk     | %90.05  |
| Kesinlik     | %84.63  |
| Duyarlılık   | %91.75  |
| F1-Skor      | %87.81  |

### Tespit Edilen Cilt Sorunları
- Akne
- Sivilce İzi
- Leke
- Kırışıklık
- Koyu Halka
- Sağlıklı Cilt

## Mobil Uygulama Kullanımı
- **Anasayfa:** Cilt sorunları kartları ve bakım ipuçları
- **Cilt Analizi:** Kamera veya galeriden fotoğraf seçimi
- **Sonuç Ekranı:** Tespit edilen sorunlar ve ürün önerileri
- **Manuel Seçim:** Cilt sorunu seçerek bilgi ve ürün önerisi alma

## Veri Seti
- Toplam Görüntü: 1304 adet
- Eğitim Seti: %80
- Test Seti: %20
- Görüntü Boyutu: 224x224 piksel
- Kaynaklar: nexdata.ai ve Kaggle Human Faces veri seti

## Özellikler ve İyileştirmeler

### Uygulanan Teknikler
- Ağırlıklı kayıp fonksiyonu ile sınıf dengesizliği giderilmesi
- Özel ceza terimleri ile etiket korelasyonlarının optimize edilmesi
- In-memory cache ile performans optimizasyonu (1 saat)
- CORS Middleware ile güvenli veri alışverişi
- Responsive tasarım ile farklı cihaz desteği

## Proje Tanıtım Videosu
Projenin kısa tanıtımını [buradan izleyebilirsiniz](https://youtu.be/yYTlYJhYurQ?si=zS35NeWCBuL87l4j).

## Teşekkür
Bu projenin geliştirilmesinde değerli yönlendirmeleri için danışmanımız **Arş. Gör. Gökhan Azizoğlu**'na teşekkür ederiz.


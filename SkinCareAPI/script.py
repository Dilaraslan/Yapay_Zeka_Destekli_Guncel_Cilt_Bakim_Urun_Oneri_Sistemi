import cv2
import os
from PIL import Image
import numpy as np


def crop_faces_from_folder(input_folder, output_folder, target_size=(512, 512)):
    """
    Klasördeki tüm görsellerdeki yüzleri tespit eder ve kırpar
    """

    # Çıktı klasörü yoksa oluştur
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # OpenCV'nin hazır yüz tanıma modelini yükle
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Desteklenen formatlar
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

    # Klasördeki dosyaları al
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(supported_formats)]

    print(f"Toplam {len(files)} görsel dosyası bulundu.")

    success_count = 0
    failed_count = 0

    for i, filename in enumerate(files, 1):
        try:
            # Görseli oku (Türkçe karakter sorunu için numpy ile)
            img_path = os.path.join(input_folder, filename)

            # Türkçe karakter destekli okuma
            with open(img_path, 'rb') as f:
                img_data = f.read()

            # Numpy array'e çevir
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                print(f"✗ {filename} - Görsel okunamadı")
                failed_count += 1
                continue

            # Gri tonlama çevir (yüz tanıma için)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Yüzleri tespit et
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 50),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            if len(faces) == 0:
                print(f"✗ {filename} - Yüz bulunamadı")
                failed_count += 1
                continue

            # En büyük yüzü seç (birden fazla yüz varsa)
            if len(faces) > 1:
                faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)

            x, y, w, h = faces[0]

            # Yüz bölgesini genişlet (daha yakın kırpım için)
            margin = int(max(w, h) * 0.15)  # %15 margin (daha az arka plan)

            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(img.shape[1], x + w + margin)
            y2 = min(img.shape[0], y + h + margin)

            # Yüzü kırp
            face_crop = img[y1:y2, x1:x2]

            # PIL'e çevir ve boyutlandır
            face_crop_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(face_crop_rgb)

            # Kare şeklinde kırp (merkezi koruyarak)
            width, height = pil_image.size
            size = min(width, height)

            left = (width - size) // 2
            top = (height - size) // 2
            right = left + size
            bottom = top + size

            square_crop = pil_image.crop((left, top, right, bottom))

            # Hedef boyuta yeniden boyutlandır
            final_image = square_crop.resize(target_size, Image.Resampling.LANCZOS)

            # Kaydet (Türkçe karakter sorunu için)
            output_filename = f"{i:03d}_x_x_x_0_0_0_0_0.jpg"
            output_path = os.path.join(output_folder, output_filename)

            # PIL ile kaydet
            final_image.save(output_path, 'JPEG', quality=95)

            print(f"✓ {filename} -> {output_filename}")
            success_count += 1

        except Exception as e:
            print(f"✗ {filename} - Hata: {str(e)}")
            failed_count += 1

    print(f"\nİşlem tamamlandı!")
    print(f"Başarılı: {success_count} dosya")
    print(f"Başarısız: {failed_count} dosya")
    print(f"Kırpılan görseller: {output_folder}")


def main():
    # Klasör yolları (raw string kullan)
    input_folder = r"C:\Users\da404\OneDrive\Masaüstü\saglikli"
    output_folder = r"C:\Users\da404\OneDrive\Masaüstü\saglikli_cropped"

    # Klasörlerin var olup olmadığını kontrol et
    if not os.path.exists(input_folder):
        print(f"HATA: Kaynak klasör bulunamadı: {input_folder}")
        return

    # Hedef boyut (piksel olarak - kare şeklinde)
    target_size = (512, 512)  # İsterseniz değiştirebilirsiniz

    print(f"Kaynak klasör: {input_folder}")
    print(f"Hedef klasör: {output_folder}")
    print(f"Hedef boyut: {target_size[0]}x{target_size[1]} piksel")

    # Klasördeki dosya sayısını kontrol et
    test_files = os.listdir(input_folder)
    print(f"Klasörde toplam {len(test_files)} dosya var")

    # Onay al
    confirm = input("\nDevam etmek istiyor musunuz? (e/h): ").lower()

    if confirm in ['e', 'evet', 'yes', 'y']:
        crop_faces_from_folder(input_folder, output_folder, target_size)
    else:
        print("İşlem iptal edildi.")


# Alternatif: Daha hassas yüz tanıma için face_recognition kütüphanesi kullanımı
def crop_faces_advanced(input_folder, output_folder, target_size=(512, 512)):
    """
    face_recognition kütüphanesi ile daha hassas yüz tanıma
    Önce: pip install face_recognition
    """
    try:
        import face_recognition

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        files = [f for f in os.listdir(input_folder) if f.lower().endswith(supported_formats)]

        success_count = 0

        for i, filename in enumerate(files, 1):
            try:
                img_path = os.path.join(input_folder, filename)
                image = face_recognition.load_image_file(img_path)
                face_locations = face_recognition.face_locations(image)

                if not face_locations:
                    print(f"✗ {filename} - Yüz bulunamadı")
                    continue

                # En büyük yüzü seç
                if len(face_locations) > 1:
                    face_locations = sorted(face_locations,
                                            key=lambda x: (x[2] - x[0]) * (x[1] - x[3]),
                                            reverse=True)

                top, right, bottom, left = face_locations[0]

                # Margin ekle (daha yakın kırpım)
                height, width = image.shape[:2]
                margin = int(max(bottom - top, right - left) * 0.15)  # %15 margin

                top = max(0, top - margin)
                bottom = min(height, bottom + margin)
                left = max(0, left - margin)
                right = min(width, right + margin)

                # Kırp
                face_image = image[top:bottom, left:right]

                # PIL'e çevir ve işle
                pil_image = Image.fromarray(face_image)

                # Kare yap
                width, height = pil_image.size
                size = min(width, height)

                left_crop = (width - size) // 2
                top_crop = (height - size) // 2

                square_crop = pil_image.crop((left_crop, top_crop,
                                              left_crop + size, top_crop + size))

                # Boyutlandır ve kaydet
                final_image = square_crop.resize(target_size, Image.Resampling.LANCZOS)

                output_filename = f"{i:03d}_face_advanced.jpg"
                output_path = os.path.join(output_folder, output_filename)
                final_image.save(output_path, 'JPEG', quality=95)

                print(f"✓ {filename} -> {output_filename}")
                success_count += 1

            except Exception as e:
                print(f"✗ {filename} - Hata: {str(e)}")

        print(f"\nToplam {success_count} yüz başarıyla kırpıldı.")

    except ImportError:
        print("face_recognition kütüphanesi bulunamadı.")
        print("Yüklemek için: pip install face_recognition")


if __name__ == "__main__":
    main()

    # Daha hassas yüz tanıma için (opsiyonel):
    # crop_faces_advanced(r"C:\Users\da404\OneDrive\Masaüstü\saglikli",
    #                    r"C:\Users\da404\OneDrive\Masaüstü\saglikli_advanced")
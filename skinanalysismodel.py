import os
import random
import numpy as np
from PIL import Image
from collections import defaultdict
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader, ConcatDataset

from torchvision.models import convnext_base, ConvNeXt_Base_Weights

# ----------------------------------------------------------------------------
# SEED & DEVICE
# ----------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Using device: {device}")

# ----------------------------------------------------------------------------
# VERİ OKUMA - Sağlam Healthy Etiketi ile
# ----------------------------------------------------------------------------
klasor_yolu = '/kaggle/input/cropped-data/croppedData'
class_names = ['acne', 'pockmark', 'stain', 'wrinkle', 'black_circle', 'healthy']
num_classes = len(class_names)

image_paths = []
labels_list = []
class_counts = {name: 0 for name in class_names}

for dosya in os.listdir(klasor_yolu):
    if dosya.lower().endswith(('.png', '.jpg', '.jpeg')):
        filename = os.path.splitext(dosya)[0]
        parts = filename.split('_')
        if len(parts) < 9:
            continue
        try:
            label = list(map(int, parts[4:9]))
        except:
            continue

        # Stain ve wrinkle birlikte olanları (0_0_1_1_0) filtrele ve %50'sini çıkar
        if label == [0, 0, 1, 1, 0]:
            if random.random() < 0.5:  # %50 şansla atla
                continue

        label.append(1 if sum(label) == 0 else 0)  # Healthy etiketi

        image_paths.append(os.path.join(klasor_yolu, dosya))
        labels_list.append(label)

        for i, flag in enumerate(label):
            if flag == 1:
                class_counts[class_names[i]] += 1

labels = np.array(labels_list)

print("\n[ETİKET DAĞILIMI] (Healthy dahil, filtrelenmiş)")
for cname, ccount in class_counts.items():
    print(f"{cname}: {ccount} adet")

# Sınıf bazlı pos_weight tanımı
total_samples = len(labels_list)
pos_weights = []

# Her sınıf için ayrı katsayı ile
# [acne, pockmark, stain, wrinkle, black_circle, healthy]
custom_multipliers = [3.5, 3.5, 1.0, 1.0, 3.0, 1.0]

for i in range(num_classes):
    pos_count = np.sum(labels[:, i])
    neg_count = total_samples - pos_count
    multiplier = custom_multipliers[i]
    pos_weight = (neg_count / pos_count) * multiplier if pos_count > 0 else 1.0
    pos_weights.append(pos_weight)

pos_weights = torch.FloatTensor(pos_weights).to(device)
print(f"\n[CLASS-WISE POS WEIGHTS] {pos_weights}")

# ----------------------------------------------------------------------------
# TRANSFORM & DATASET
# ----------------------------------------------------------------------------
base_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])


class SkinDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img = Image.open(self.image_paths[idx]).convert('RGB')
        if self.transform:
            img = self.transform(img)
        label = torch.FloatTensor(self.labels[idx])
        return img, label


# ----------------------------------------------------------------------------
# TRAIN / TEST AYIRIMI
# ----------------------------------------------------------------------------
X_train_paths, X_test_paths, y_train, y_test = train_test_split(
    image_paths, labels_list, test_size=0.2, random_state=SEED
)

original_train = SkinDataset(X_train_paths, y_train, transform=base_transform)
train_dataset = original_train
test_dataset = SkinDataset(X_test_paths, y_test, transform=base_transform)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

print(f"\n[EĞİTİM VERİSİ] Orijinal: {len(original_train)} ")

# ----------------------------------------------------------------------------
# MODEL
# ----------------------------------------------------------------------------
model = convnext_base(weights=ConvNeXt_Base_Weights.IMAGENET1K_V1)
model.classifier[2] = nn.Linear(model.classifier[2].in_features, 6)
model = model.to(device)

# ----------------------------------------------------------------------------
# LOSS & OPTİMİZASYON
# ----------------------------------------------------------------------------
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weights)
optimizer = optim.Adam(model.parameters(), lr=1e-4)


# Stain-Wrinkle korelasyon penalty fonksiyonu
def stain_wrinkle_penalty(outputs, alpha=0.1):
    """Stain ve wrinkle arasındaki korelasyonu azaltmak için penalty"""
    stain_probs = torch.sigmoid(outputs[:, 2])  # stain index: 2
    wrinkle_probs = torch.sigmoid(outputs[:, 3])  # wrinkle index: 3

    # Pearson korelasyon benzeri penalty
    penalty = torch.mean((stain_probs - stain_probs.mean()) * (wrinkle_probs - wrinkle_probs.mean()))
    return alpha * penalty.abs()


def healthy_conflict_penalty(outputs, alpha=0.1):
    """
    Aynı anda hem healthy hem de diğer sınıflar yüksekse ceza uygular.
    """
    probs = torch.sigmoid(outputs)  # (batch_size, 6)
    healthy_probs = probs[:, 5]  # 6. sınıf = healthy
    other_probs_sum = probs[:, :5].sum(dim=1)  # İlk 5 sınıfın toplamı

    # Eğer healthy + diğerler birlikte yüksekse → ceza
    conflict = healthy_probs * other_probs_sum  # (batch_size,)
    return alpha * torch.mean(conflict)


# ----------------------------------------------------------------------------
# EĞİTİM DÖNGÜSÜ
# ----------------------------------------------------------------------------
epochs = 75
model.train()

for epoch in range(epochs):
    running_loss = 0.0
    for images, labels_6d in train_loader:
        images = images.to(device)
        labels_6d = labels_6d.to(device)

        optimizer.zero_grad()
        outputs = model(images)

        # Ana loss
        loss = criterion(outputs, labels_6d)

        # Ek cezalar
        penalty_sw = stain_wrinkle_penalty(outputs, alpha=0.05)
        penalty_healthy = healthy_conflict_penalty(outputs, alpha=0.1)

        # Toplam loss
        total_loss = loss + penalty_sw + penalty_healthy

        total_loss.backward()
        optimizer.step()

        running_loss += total_loss.item() * images.size(0)

    epoch_loss = running_loss / len(train_dataset)
    print(f"Epoch [{epoch + 1}/{epochs}], Loss: {epoch_loss:.4f}")
    torch.cuda.empty_cache()

# -----------------------------------------------------------------------------
# EĞİTİLMİŞ MODELİ KAYDETME
# -----------------------------------------------------------------------------
torch.save(model.state_dict(), "75epoch-convnextbase.pth")
print("\n[INFO] Model kaydedildi: '75epoch-convnextbase.pth'")

import os
import random
import numpy as np
from PIL import Image
from collections import defaultdict
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader, ConcatDataset

from torchvision.models import convnext_base, ConvNeXt_Base_Weights

# ----------------------------------------------------------------------------
# SEED & DEVICE
# ----------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Using device: {device}")

# ----------------------------------------------------------------------------
# VERİ OKUMA - Sağlam Healthy Etiketi ile
# ----------------------------------------------------------------------------
klasor_yolu = '/kaggle/input/cropped-data/croppedData'
class_names = ['acne', 'pockmark', 'stain', 'wrinkle', 'black_circle', 'healthy']
num_classes = len(class_names)

image_paths = []
labels_list = []
class_counts = {name: 0 for name in class_names}

for dosya in os.listdir(klasor_yolu):
    if dosya.lower().endswith(('.png', '.jpg', '.jpeg')):
        filename = os.path.splitext(dosya)[0]
        parts = filename.split('_')
        if len(parts) < 9:
            continue
        try:
            label = list(map(int, parts[4:9]))
        except:
            continue

        # Stain ve wrinkle birlikte olanları (0_0_1_1_0) filtrele ve %50'sini çıkar
        if label == [0, 0, 1, 1, 0]:
            if random.random() < 0.5:  # %50 şansla atla
                continue

        label.append(1 if sum(label) == 0 else 0)  # Healthy etiketi

        image_paths.append(os.path.join(klasor_yolu, dosya))
        labels_list.append(label)

        for i, flag in enumerate(label):
            if flag == 1:
                class_counts[class_names[i]] += 1

labels = np.array(labels_list)

print("\n[ETİKET DAĞILIMI] (Healthy dahil, filtrelenmiş)")
for cname, ccount in class_counts.items():
    print(f"{cname}: {ccount} adet")

# Sınıf bazlı pos_weight tanımı
total_samples = len(labels_list)
pos_weights = []

# Her sınıf için ayrı katsayı ile
# [acne, pockmark, stain, wrinkle, black_circle, healthy]
custom_multipliers = [3.5, 3.5, 1.0, 1.0, 3.0, 1.0]

for i in range(num_classes):
    pos_count = np.sum(labels[:, i])
    neg_count = total_samples - pos_count
    multiplier = custom_multipliers[i]
    pos_weight = (neg_count / pos_count) * multiplier if pos_count > 0 else 1.0
    pos_weights.append(pos_weight)

pos_weights = torch.FloatTensor(pos_weights).to(device)
print(f"\n[CLASS-WISE POS WEIGHTS] {pos_weights}")

# ----------------------------------------------------------------------------
# TRANSFORM & DATASET
# ----------------------------------------------------------------------------
base_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])


class SkinDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img = Image.open(self.image_paths[idx]).convert('RGB')
        if self.transform:
            img = self.transform(img)
        label = torch.FloatTensor(self.labels[idx])
        return img, label


# ----------------------------------------------------------------------------
# TRAIN / TEST AYIRIMI
# ----------------------------------------------------------------------------
X_train_paths, X_test_paths, y_train, y_test = train_test_split(
    image_paths, labels_list, test_size=0.2, random_state=SEED
)

original_train = SkinDataset(X_train_paths, y_train, transform=base_transform)
train_dataset = original_train
test_dataset = SkinDataset(X_test_paths, y_test, transform=base_transform)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

print(f"\n[EĞİTİM VERİSİ] Orijinal: {len(original_train)} ")

# ----------------------------------------------------------------------------
# MODEL
# ----------------------------------------------------------------------------
model = convnext_base(weights=ConvNeXt_Base_Weights.IMAGENET1K_V1)
model.classifier[2] = nn.Linear(model.classifier[2].in_features, 6)
model = model.to(device)

# ----------------------------------------------------------------------------
# LOSS & OPTİMİZASYON
# ----------------------------------------------------------------------------
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weights)
optimizer = optim.Adam(model.parameters(), lr=1e-4)


# Stain-Wrinkle korelasyon penalty fonksiyonu
def stain_wrinkle_penalty(outputs, alpha=0.1):
    """Stain ve wrinkle arasındaki korelasyonu azaltmak için penalty"""
    stain_probs = torch.sigmoid(outputs[:, 2])  # stain index: 2
    wrinkle_probs = torch.sigmoid(outputs[:, 3])  # wrinkle index: 3

    # Pearson korelasyon benzeri penalty
    penalty = torch.mean((stain_probs - stain_probs.mean()) * (wrinkle_probs - wrinkle_probs.mean()))
    return alpha * penalty.abs()


def healthy_conflict_penalty(outputs, alpha=0.1):
    """
    Aynı anda hem healthy hem de diğer sınıflar yüksekse ceza uygular.
    """
    probs = torch.sigmoid(outputs)  # (batch_size, 6)
    healthy_probs = probs[:, 5]  # 6. sınıf = healthy
    other_probs_sum = probs[:, :5].sum(dim=1)  # İlk 5 sınıfın toplamı

    # Eğer healthy + diğerler birlikte yüksekse → ceza
    conflict = healthy_probs * other_probs_sum  # (batch_size,)
    return alpha * torch.mean(conflict)


# ----------------------------------------------------------------------------
# EĞİTİM DÖNGÜSÜ
# ----------------------------------------------------------------------------
epochs = 75
model.train()

for epoch in range(epochs):
    running_loss = 0.0
    for images, labels_6d in train_loader:
        images = images.to(device)
        labels_6d = labels_6d.to(device)

        optimizer.zero_grad()
        outputs = model(images)

        # Ana loss
        loss = criterion(outputs, labels_6d)

        # Ek cezalar
        penalty_sw = stain_wrinkle_penalty(outputs, alpha=0.05)
        penalty_healthy = healthy_conflict_penalty(outputs, alpha=0.1)

        # Toplam loss
        total_loss = loss + penalty_sw + penalty_healthy

        total_loss.backward()
        optimizer.step()

        running_loss += total_loss.item() * images.size(0)

    epoch_loss = running_loss / len(train_dataset)
    print(f"Epoch [{epoch + 1}/{epochs}], Loss: {epoch_loss:.4f}")
    torch.cuda.empty_cache()

# -----------------------------------------------------------------------------
# EĞİTİLMİŞ MODELİ KAYDETME
# -----------------------------------------------------------------------------
torch.save(model.state_dict(), "75epoch-convnextbase.pth")
print("\n[INFO] Model kaydedildi: '75epoch-convnextbase.pth'")
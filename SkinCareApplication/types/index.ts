// Cilt tipi tanımları (analiz sonucu değerleri)
export type SkinType = 'Leke' | 'Akne' | 'Kırışıklık' | 'Koyu Halka';

// Ürün bilgisi
export interface Product {
  id: string;
  name: string;
  imageUrl: any; // local require(...) veya remote URI olabilir
  price: string;
}

// Navigation Stack tipi
export type RootStackParamList = {
  Home: undefined;
  SkinAnalysis: undefined;
  Results: {skinType: SkinType};
  ProductDetail: {product: any};
  SkinTypeScreen: {skinType: string};
};

//SkinTypeScreen.tsx
import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  Image,
  Linking,
} from 'react-native';
// sadece dışardan gelenleri al
import {
  getSkinIssueProductsOnly,
  SkinIssueInfo,
  Product,
} from '../services/apiService';

import ProductCard from '../components/ProductCard';
import LinearGradient from 'react-native-linear-gradient';

//apiService.ts doyasından çekerken sürekli hata alındığı için buraya taşındı oradaki yorum satırında
const getSkinIssueInfoOnly = async (
  issueType: string,
): Promise<SkinIssueInfo> => {
  const res = await fetch(
    `http://192.168.1.114:8000/skin-issue/info/${issueType}`,
  );
  if (!res.ok) throw new Error('Cilt bilgisi alınamadı');
  return await res.json();
};

// Tüm cilt tipleri için tek bir temizleme görseli kullanılacak
const cleansingImage = require('../assets/cleansing.png');

const LABEL_MAP: Record<string, string> = {
  leke: 'stain',
  akne: 'acne',
  kırışıklık: 'wrinkle',
  gözaltı: 'black_circle',
  gözenek: 'pockmark',
};

// SkinType ekranı için props tipi
interface SkinTypeScreenProps {
  route: {
    params: {
      skinType: string; // 'acne', 'wrinkle', 'stain', 'black_circle', 'pockmark' gibi
    };
  };
  navigation: any;
}

const SkinTypeScreen: React.FC<SkinTypeScreenProps> = ({route, navigation}) => {
  const {skinType} = route.params;
  const [loading, setLoading] = useState(true);
  const [skinIssueData, setSkinIssueData] = useState<{
    info: SkinIssueInfo;
    products: Product[];
  }>({
    info: {
      title: '',
      description: '',
      causes: [],
      daily_care: [],
      tips: [],
    },
    products: [],
  });
  const [error, setError] = useState<string | null>(null);

  const mappedSkinType = LABEL_MAP[skinType.toLowerCase()] || skinType;

  console.log('getSkinIssueInfoOnly type:', typeof getSkinIssueInfoOnly);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [info, products] = await Promise.all([
          getSkinIssueInfoOnly(mappedSkinType),
          getSkinIssueProductsOnly(mappedSkinType, 3),
        ]);
        setSkinIssueData({info, products});
      } catch (err) {
        console.error('Veri çekme hatası:', err);
        setError('Veriler yüklenemedi.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [skinType, mappedSkinType]);

  const handleProductPress = (product: Product) => {
    // Ürün linki varsa, o linki aç
    if (product.purchase_link) {
      Linking.openURL(product.purchase_link).catch(err =>
        console.error('Ürün linki açılamadı:', err),
      );
    } else {
      // Ürün detay sayfasına yönlendirme (link yoksa)
      navigation.navigate('ProductDetail', {product});
    }
  };

  // Tüm cilt tipleri için temizleme görselini kullan
  const skinImage = cleansingImage;

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#F6C3D5" />
        <Text style={styles.loadingText}>Bilgiler yükleniyor...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity
          style={styles.retryButton}
          onPress={() => navigation.goBack()}>
          <Text style={styles.retryButtonText}>Geri Dön</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const renderSectionHeader = (title: string) => (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{title}</Text>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.headerImageContainer}>
        <Image
          source={skinImage}
          style={styles.headerImage}
          resizeMode="cover"
        />
        <View style={styles.headerTextContainer}>
          <Text style={styles.title}>{skinIssueData.info.title}</Text>
        </View>
      </View>

      <View style={styles.contentContainer}>
        <View style={styles.section}>
          {renderSectionHeader('Nedir?')}
          <Text style={styles.description}>
            {skinIssueData.info.description}
          </Text>
        </View>

        <View style={styles.section}>
          {renderSectionHeader('Nedenleri')}
          {skinIssueData.info.causes.map((cause, index) => (
            <View key={index} style={styles.listItem}>
              <View style={styles.bulletPoint}>
                <Text style={styles.bulletDot}>•</Text>
              </View>
              <Text style={styles.listText}>{cause}</Text>
            </View>
          ))}
        </View>

        <View style={styles.section}>
          {renderSectionHeader('Günlük Bakım Önerileri')}
          {skinIssueData.info.daily_care.map((care, index) => (
            <View key={index} style={styles.listItem}>
              <View style={styles.bulletPoint}>
                <Text style={styles.bulletDot}>•</Text>
              </View>
              <Text style={styles.listText}>{care}</Text>
            </View>
          ))}
        </View>

        <View style={styles.section}>
          {renderSectionHeader('İpuçları')}
          {skinIssueData.info.tips.map((tip, index) => (
            <View key={index} style={styles.listItem}>
              <View style={styles.bulletPoint}>
                <Text style={styles.bulletDot}>•</Text>
              </View>
              <Text style={styles.listText}>{tip}</Text>
            </View>
          ))}
        </View>

        <View style={styles.section}>
          {renderSectionHeader('Önerilen Ürünler')}
          {skinIssueData.products.length > 0 ? (
            <View style={styles.productsContainer}>
              {skinIssueData.products.map((product, index) => (
                <View key={index} style={styles.productCardVertical}>
                  <ProductCard
                    product={product}
                    onPress={() => handleProductPress(product)}
                  />
                </View>
              ))}
            </View>
          ) : (
            <View style={styles.noProductsContainer}>
              <Text style={styles.noProductsText}>
                Ürün önerisi bulunamadı.
              </Text>
            </View>
          )}
        </View>

        <TouchableOpacity
          style={styles.analysisInfoBox}
          onPress={() => navigation.navigate('SkinAnalysis')}>
          <LinearGradient
            colors={['#F6E6C2', '#F9F2EA']}
            start={{x: 0, y: 0}}
            end={{x: 1, y: 0}}
            style={styles.analysisGradient}>
            <View style={styles.analysisContent}>
              <Image
                source={require('../assets/scan.png')}
                style={styles.scanIcon}
              />
              <View style={styles.analysisTextContainer}>
                <Text style={styles.analysisInfoText}>
                  Size özel cilt analizinizi yaptırmak ve kişiselleştirilmiş
                  ürün önerileri almak için{' '}
                  <Text style={{fontWeight: 'bold'}}>"Cilt Analizi"</Text>{' '}
                  bölümümüzü kullanabilirsiniz.
                </Text>
              </View>
            </View>
          </LinearGradient>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF9FC', // Çok açık pembe/beyaz arka plan
  },
  contentContainer: {
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFF9FC',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#B39CD0',
    fontFamily: 'Avenir-Medium',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#FFF2F0',
  },
  errorText: {
    fontSize: 16,
    color: '#F8AFA6',
    textAlign: 'center',
    marginVertical: 20,
    fontFamily: 'Avenir-Medium',
  },
  retryButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: '#F5C3C5',
    borderRadius: 25,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    fontFamily: 'Avenir-Medium',
  },
  headerImageContainer: {
    height: 220,
    width: '100%',
    position: 'relative',
    backgroundColor: '#FFF2F9',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerImage: {
    marginTop: 30,
    width: 140,
    height: 140,
    borderRadius: 75,
  },
  headerTextContainer: {
    padding: 10,
    marginTop: 8,
    backgroundColor: 'rgba(255,255,255,0.8)',
    borderRadius: 15,
    alignSelf: 'center',
    minWidth: '80%',
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#957DAD',
    textShadowColor: 'rgba(255,255,255,0.8)',
    textShadowOffset: {width: 0, height: 1},
    textShadowRadius: 4,
    fontFamily: 'Avenir-Heavy',
  },
  section: {
    marginBottom: 20,
    padding: 18,
    backgroundColor: '#ffffff',
    borderRadius: 20,
    elevation: 2,
    shadowColor: '#FFDFD3',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.2,
    shadowRadius: 8,
    borderWidth: 1,
    borderColor: '#FFF2F2',
  },
  sectionHeader: {
    marginBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#F5E6CC',
    paddingBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#957DAD',
    fontFamily: 'Avenir-Heavy',
  },
  scanIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
  },
  description: {
    fontSize: 15,
    lineHeight: 24,
    color: '#7D7D7D',
    fontFamily: 'Avenir-Book',
  },
  listItem: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'flex-start',
  },
  bulletPoint: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: '#F5E6CC',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    marginTop: 2,
  },
  bulletDot: {
    fontSize: 14,
    color: '#D4A5A5',
    fontWeight: 'bold',
  },
  listText: {
    fontSize: 15,
    flex: 1,
    color: '#7D7D7D',
    lineHeight: 22,
    fontFamily: 'Avenir-Book',
  },
  productsContainer: {
    marginTop: 15,
  },
  productCardVertical: {
    width: '100%',
    marginBottom: 16,
  },
  noProductsContainer: {
    alignItems: 'center',
    padding: 20,
    marginTop: 10,
  },
  noProductsText: {
    fontSize: 15,
    color: '#B39CD0',
    textAlign: 'center',
    marginTop: 10,
    fontFamily: 'Avenir-Book',
  },
  analysisInfoBox: {
    marginVertical: 30,
    borderRadius: 20,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.15,
    shadowRadius: 8,
  },
  analysisGradient: {
    width: '100%',
    borderRadius: 20,
  },
  analysisContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
  },
  analysisTextContainer: {
    flex: 1,
    marginHorizontal: 15,
  },
  analysisInfoText: {
    fontSize: 14,
    color: '#957DAD',
    textAlign: 'left',
    lineHeight: 20,
    fontFamily: 'Avenir-Medium',
  },
});

export default SkinTypeScreen;

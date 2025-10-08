//ResultScreen.tsx
import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  Linking,
  SafeAreaView,
} from 'react-native';
import {useRoute, RouteProp, useNavigation} from '@react-navigation/native';
import {
  analyzeImage,
  Product,
  SkincareRecommendation,
} from '../services/apiService';
import ProductCard from '../components/ProductCard';
import LinearGradient from 'react-native-linear-gradient';

type ResultsRouteParams = {
  imageUri: string;
  analysisResults?: SkincareRecommendation;
};

type ResultsScreenRouteProp = RouteProp<
  {Results: ResultsRouteParams},
  'Results'
>;

const skinIssueLabels: Record<string, string> = {
  acne: 'Sivilce',
  pockmark: 'Çukur İzleri',
  stain: 'Leke',
  wrinkle: 'Kırışıklık',
  black_circle: 'Koyu Halka',
  no_skin_issue_detected: 'Cilt sorunu tespit edilmedi',
};

const ResultsScreen: React.FC = () => {
  const route = useRoute<ResultsScreenRouteProp>();
  const navigation = useNavigation<any>();
  const {imageUri, analysisResults} = route.params;

  const [loading, setLoading] = useState(!analysisResults);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SkincareRecommendation | null>(
    analysisResults || null,
  );

  useEffect(() => {
    // If results were already passed, don't fetch again
    if (analysisResults) {
      setResults(analysisResults);
      setLoading(false);
      return;
    }

    const fetchResults = async () => {
      try {
        const result = await analyzeImage(imageUri);
        setResults(result);
      } catch (err: any) {
        console.error('API Error:', err);
        setError(
          `Cilt analizi sırasında bir hata oluştu: ${err.message || err}`,
        );
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [imageUri, analysisResults]);

  const renderHeader = () => (
    <LinearGradient
      colors={['#E8F8F5', '#C8EDE9']}
      start={{x: 0, y: 0}}
      end={{x: 1, y: 0}}
      style={styles.header}>
      <Text style={styles.headerTitle}>Cilt Analizi Sonuçları</Text>
    </LinearGradient>
  );

  const renderNoIssuesMessage = () => (
    <View style={styles.noIssuesContainer}>
      <Image
        source={require('../assets/healthy-skin.png')}
        style={styles.healthyImage}
        defaultSource={require('../assets/pp.png')}
      />
      <Text style={styles.noIssuesTitle}>Harika Haber!</Text>
      <Text style={styles.noIssuesText}>
        Cildinizde herhangi bir sorun tespit edilmedi. Cildiniz sağlıklı
        görünüyor! Cildinizin güzelliğini korumak için aşağıdaki ürünleri
        değerlendirebilirsiniz.
      </Text>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.safeArea}>
        {renderHeader()}
        <View style={styles.centered}>
          <ActivityIndicator size="large" color="#89CCC5" />
          <Text style={styles.loadingText}>Cilt analizi yapılıyor...</Text>
          <Text style={styles.loadingSubText}>
            Bu işlem birkaç saniye sürebilir
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={styles.safeArea}>
        {renderHeader()}
        <View style={styles.centered}>
          <Image
            source={require('../assets/error.png')}
            style={styles.errorImage}
            defaultSource={require('../assets/pp.png')}
          />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity
            style={styles.tryAgainButton}
            onPress={() => navigation.goBack()}>
            <Text style={styles.tryAgainButtonText}>Tekrar Dene</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  if (!results) {
    return (
      <SafeAreaView style={styles.safeArea}>
        {renderHeader()}
        <View style={styles.centered}>
          <Text style={styles.errorText}>Sonuç bulunamadı.</Text>
          <TouchableOpacity
            style={styles.tryAgainButton}
            onPress={() => navigation.goBack()}>
            <Text style={styles.tryAgainButtonText}>Tekrar Dene</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  // Flatten all product recommendations into a single array for display
  const allProducts: Product[] = Object.values(
    results.recommended_products,
  ).flat();

  const hasNoSkinIssues =
    results.detected_skin_issues.length === 0 ||
    (results.detected_skin_issues.length === 1 &&
      results.detected_skin_issues[0] === 'healthy');

  return (
    <SafeAreaView style={styles.safeArea}>
      {renderHeader()}
      <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
        <View style={styles.imageContainer}>
          <Image source={{uri: imageUri}} style={styles.image} />
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Tespit Edilen Cilt Sorunları</Text>
          {!hasNoSkinIssues
            ? results.detected_skin_issues.map((issue, index) => (
                <View key={index} style={styles.issueItem}>
                  <View style={styles.issueDot} />
                  <Text style={styles.issueText}>
                    {skinIssueLabels[issue] || issue}
                  </Text>
                </View>
              ))
            : renderNoIssuesMessage()}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            {hasNoSkinIssues
              ? 'Cildiniz İçin Önerilen Bakım Ürünleri'
              : 'Kişiselleştirilmiş Ürün Önerileri'}
          </Text>
          {allProducts.length === 0 ? (
            <View style={styles.noProductsContainer}>
              <Text style={styles.noProductsText}>
                Uygun ürün bulunamadı. Lütfen daha sonra tekrar deneyiniz.
              </Text>
            </View>
          ) : (
            allProducts.map((product, idx) => (
              <ProductCard
                key={idx}
                product={product}
                onPress={() => {
                  if (product.purchase_link) {
                    Linking.openURL(product.purchase_link);
                  }
                }}
              />
            ))
          )}
        </View>

        <TouchableOpacity
          style={styles.homeButton}
          onPress={() => {
            navigation.navigate('Home');
          }}>
          <Text style={styles.homeButtonText}>Ana Sayfaya Dön</Text>
        </TouchableOpacity>

        <View style={styles.footer} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F2F9F9', // Soft mint background
  },
  header: {
    paddingVertical: 16,
    paddingHorizontal: 20,
    elevation: 2,
    backgroundColor: '#FFFFFF',
  },
  headerTitle: {
    color: '#5DACA9', // Soft teal header text
    fontSize: 20,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  container: {
    flex: 1,
    backgroundColor: '#F2F9F9', // Soft mint background
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 18,
    color: '#70B1A1', // Soft teal text
    fontWeight: '600',
  },
  loadingSubText: {
    marginTop: 8,
    fontSize: 14,
    color: '#A8A8A8', // Light gray
  },
  errorImage: {
    width: 120,
    height: 120,
    marginBottom: 20,
  },
  errorText: {
    color: '#E99090', // Soft error color
    fontSize: 16,
    textAlign: 'center',
    marginHorizontal: 20,
  },
  tryAgainButton: {
    marginTop: 24,
    backgroundColor: '#89CCC5', // Soft teal button
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 25,
    elevation: 2,
  },
  tryAgainButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  imageContainer: {
    alignItems: 'center',
    marginVertical: 24,
  },
  image: {
    width: 180,
    height: 180,
    borderRadius: 90,
    borderWidth: 3,
    borderColor: '#B8E0D8', // Soft mint border
  },
  section: {
    marginHorizontal: 20,
    marginBottom: 24,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    elevation: 1, // Lighter shadow
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#5DACA9', // Soft teal title
  },
  issueItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  issueDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#A0D6CA', // Soft mint dot
    marginRight: 8,
  },
  issueText: {
    fontSize: 16,
    color: '#707070', // Medium gray text
  },
  noIssuesContainer: {
    alignItems: 'center',
    padding: 16,
  },
  healthyImage: {
    width: 100,
    height: 100,
    marginBottom: 16,
  },
  noIssuesTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#7BBEB0', // Soft teal title
    marginBottom: 8,
  },
  noIssuesText: {
    fontSize: 15,
    color: '#808080',
    textAlign: 'center',
    lineHeight: 22,
  },
  noProductsContainer: {
    padding: 16,
    alignItems: 'center',
  },
  noProductsText: {
    fontSize: 15,
    color: '#909090',
    textAlign: 'center',
  },
  homeButton: {
    marginHorizontal: 20,
    marginBottom: 24,
    backgroundColor: '#89CCC5', // Soft teal button
    paddingVertical: 14,
    borderRadius: 25,
    elevation: 2,
    alignItems: 'center',
  },
  homeButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  footer: {
    height: 24,
  },
});

export default ResultsScreen;

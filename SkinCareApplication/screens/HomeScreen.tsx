//Homescreen.tsx
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ScrollView,
  StatusBar,
} from 'react-native';
import {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {RootStackParamList, SkinType} from '../types';
import SkinTypeCard from '../components/SkinTypeCard';

interface HomeScreenProps {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Home'>;
}

const HomeScreen: React.FC<HomeScreenProps> = ({navigation}) => {
  const skinTypes: Array<{type: SkinType; image: any}> = [
    {type: 'Leke', image: require('../assets/leke.jpg')},
    {type: 'Akne', image: require('../assets/akne.jpg')},
    {type: 'Kırışıklık', image: require('../assets/kırışıklık.jpg')},
    {type: 'Koyu Halka', image: require('../assets/koyuHalka.jpg')},
    {type: 'Gözenek', image: require('../assets/facePlaceholder.jpg')}, // Yeni eklenen gözenek seçeneği
  ];

  const tips = [
    {
      id: '1',
      emoji: '🧼',
      title: 'Nazik Temizlik',
      description:
        'Cildinizi günde iki kez, sabah ve akşam olmak üzere nazik bir temizleyici ile yıkayın. Sert sabunlar cilt bariyerine zarar verebilir.',
      backgroundColor: '#DDF3F5',
      borderColor: '#A5E0E6',
    },
    {
      id: '2',
      emoji: '🌞',
      title: 'Güneş Koruyucu',
      description:
        'UVA ve UVB ışınlarına karşı koruma sağlayan, en az SPF 30 içeren geniş spektrumlu bir güneş koruyucu kullanın.',
      backgroundColor: '#FFF0F5',
      borderColor: '#FFD6E7',
    },
    {
      id: '3',
      emoji: '🌙',
      title: 'Gece Bakımı',
      description:
        'Gece boyunca cilt yenilenmesi için nemlendirici ve retinol içeren gece kremi uygulayın. Gece cilt hücrelerinin yenilendiği saatlerdir.',
      backgroundColor: '#F3EAC2',
      borderColor: '#EAD98C',
    },
    {
      id: '4',
      emoji: '💧',
      title: 'Yeterli Su Tüketimi',
      description:
        'Cilt sağlığı için yeterli su tüketimi önemlidir. Susuz kalmak cildin kurumasına ve donuk görünmesine neden olabilir.',
      backgroundColor: '#E3F2FD',
      borderColor: '#B6DCFC',
    },
    {
      id: '5',
      emoji: '🌿',
      title: 'Peeling (Eksfoliasyon)',
      description:
        'Haftada 1-2 kez yapılan kimyasal veya fiziksel peeling, ölü hücreleri temizleyerek cildin yenilenmesini destekler.',
      backgroundColor: '#E8F5E9',
      borderColor: '#A5D6A7',
    },
    {
      id: '6',
      emoji: '🧴',
      title: 'Nemlendirme',
      description:
        'Her cilt tipi için uygun bir nemlendirici kullanmak, cildin bariyerini korumaya yardımcı olur. Özellikle seramid ve hyaluronik asit içeren ürünleri tercih edin.',
      backgroundColor: '#F5E6CC',
      borderColor: '#E6C88F',
    },
    {
      id: '7',
      emoji: '🥦',
      title: 'Beslenme ve Cilt Sağlığı',
      description:
        'Omega-3 yağ asitleri, C vitamini ve antioksidanlar açısından zengin bir beslenme, cilt yaşlanmasını geciktirir ve sivilce oluşumunu azaltabilir.',
      backgroundColor: '#E1F5FE',
      borderColor: '#81D4FA',
    },
    {
      id: '8',
      emoji: '💻',
      title: 'Mavi Işık Koruması',
      description:
        'Telefon, bilgisayar gibi cihazlardan yayılan mavi ışık da cilt yaşlanmasına neden olabilir. Antioksidan içerikli ürünler bu etkiye karşı koruyucudur.',
      backgroundColor: '#F3E5F5',
      borderColor: '#CE93D8',
    },
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <StatusBar barStyle="dark-content" />

      <View style={styles.horizontalHeader}>
        <Image
          source={require('../assets/logo.png')}
          style={styles.smallLogo}
        />
        <Text style={styles.horizontalTitle}>
          Yapay Zekâ Destekli Güncel Cilt Bakım Ürün Öneri Sistemi
        </Text>
      </View>

      <View style={styles.horizontalCardContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {skinTypes.map((item, index) => (
            <View key={index} style={styles.skinCardWrapper}>
              <SkinTypeCard type={item.type} image={item.image} />
            </View>
          ))}
        </ScrollView>
      </View>

      <TouchableOpacity
        style={styles.analysisBox}
        onPress={() => navigation.navigate('SkinAnalysis')}>
        <View style={styles.scanIconContainer}>
          <Image
            source={require('../assets/scan.png')}
            style={styles.scanIcon}
          />
        </View>
        <View style={{flex: 1}}>
          <Text style={styles.analysisTitle}>Cilt Analizi</Text>
          <Text style={styles.analysisDescription}>
            Size uygun kozmetik ürünü bulmak için cilt analizini başlatın.
          </Text>
        </View>
      </TouchableOpacity>

      <View style={styles.recommendationHeader}>
        <Text style={styles.recommendationTitle}>Cilt Bakımı İpuçları</Text>
      </View>

      {/* Geliştirilmiş dikdörtgen kartlar */}
      <View style={styles.tipsContainer}>
        {tips.map(tip => (
          <View
            key={tip.id}
            style={[styles.tipCardOuter, {borderColor: tip.borderColor}]}>
            <TouchableOpacity
              style={[styles.tipCard, {backgroundColor: tip.backgroundColor}]}
              activeOpacity={0.7}>
              <View style={styles.tipHeader}>
                <Text style={styles.tipEmoji}>{tip.emoji}</Text>
                <Text style={styles.tipTitle}>{tip.title}</Text>
              </View>
              <Text style={styles.tipDescription}>{tip.description}</Text>
            </TouchableOpacity>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9F9F9',
    paddingHorizontal: 16,
  },

  horizontalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 24,
    marginBottom: 16,
    gap: 10,
  },

  smallLogo: {
    width: 75,
    height: 75,
    borderRadius: 35,
    resizeMode: 'contain',
  },

  horizontalTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#222',
    flexShrink: 1,
    flexWrap: 'wrap',
    textAlign: 'center',
  },

  horizontalCardContainer: {
    marginVertical: 16,
  },

  skinCardWrapper: {
    marginRight: 12,
  },

  analysisBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E6F4F9',
    padding: 20,
    borderRadius: 16,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 3},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#C7E8F3',
  },
  scanIconContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.7)',
    borderRadius: 30,
    width: 70,
    height: 70,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  scanIcon: {
    width: 50,
    height: 50,
  },
  analysisTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#222',
    marginBottom: 4,
  },
  analysisDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  recommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  recommendationTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#222',
  },
  tipsContainer: {
    marginBottom: 20,
    gap: 12,
  },
  tipCardOuter: {
    borderRadius: 14,
    borderWidth: 1,
    overflow: 'hidden',
  },
  tipCard: {
    padding: 16,
  },
  tipHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  tipEmoji: {
    fontSize: 18,
    marginRight: 8,
  },
  tipTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#000',
  },
  tipDescription: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
    marginBottom: 6,
  },
});

export default HomeScreen;

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Linking,
  Platform,
} from 'react-native';
import {Camera} from 'react-native-vision-camera';
import {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {RootStackParamList} from '../types';
import CameraView from '../components/CameraView';
import {analyzeImage} from '../services/apiService';

// Types
type SkinAnalysisScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'SkinAnalysis'
>;

interface SkinAnalysisScreenProps {
  navigation: SkinAnalysisScreenNavigationProp;
}

const SkinAnalysisScreen: React.FC<SkinAnalysisScreenProps> = ({
  navigation,
}) => {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    const checkPermission = async () => {
      try {
        const status = await Camera.getCameraPermissionStatus();
        if (status === 'authorized' || status === 'granted') {
          setHasPermission(true);
        } else {
          const newStatus = await Camera.requestCameraPermission();
          setHasPermission(
            newStatus === 'authorized' || newStatus === 'granted',
          );
        }
      } catch (error) {
        console.error('Permission check error:', error);
        setHasPermission(false);
      }
    };

    checkPermission();
  }, []);

  const handleCapture = async (uri: string) => {
    try {
      setIsAnalyzing(true);
      console.log('Picture captured:', uri);

      // Navigate to Results screen with just the image URI
      // The Results screen will handle the API call
      navigation.navigate('Results', {
        imageUri: uri,
      });
    } catch (error) {
      console.error('Capture error:', error);
      Alert.alert('Hata', 'Fotoğraf işleme sırasında bir hata oluştu.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const openSettings = () => {
    if (Platform.OS === 'ios') {
      Linking.openURL('app-settings:');
    } else {
      Linking.openSettings();
    }
  };

  if (hasPermission === null) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#000" />
        <Text style={styles.loadingText}>Kamera izni kontrol ediliyor...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.centered}>
        <Text style={styles.permissionText}>Kamera erişim izni verilmedi</Text>
        <TouchableOpacity style={styles.button} onPress={openSettings}>
          <Text style={styles.buttonText}>Ayarları Aç</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Yüz Analizi</Text>
        <View style={{width: 24}} />
      </View>

      {/* Camera */}
      <CameraView onCapture={handleCapture} />

      {isAnalyzing && (
        <View style={styles.centeredOverlay}>
          <ActivityIndicator size="large" color="#000" />
          <Text style={styles.loadingText}>Fotoğraf hazırlanıyor...</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    position: 'absolute',
    top: 50,
    left: 20,
    right: 20,
    zIndex: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  backText: {
    fontSize: 22,
    color: '#fff',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  centeredOverlay: {
    position: 'absolute',
    top: '50%',
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 15,
    marginTop: 12,
    color: '#fff',
    textAlign: 'center',
  },
  permissionText: {
    fontSize: 16,
    color: 'red',
    textAlign: 'center',
    marginBottom: 16,
  },
  button: {
    marginTop: 12,
    backgroundColor: '#333',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  buttonText: {
    color: '#FFF',
    fontSize: 15,
    fontWeight: 'bold',
  },
});

export default SkinAnalysisScreen;

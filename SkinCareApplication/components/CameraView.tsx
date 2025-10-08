//CameraView.tsx

import React, {useEffect, useRef, useState} from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  Text,
  ActivityIndicator,
  Alert,
  PermissionsAndroid,
  Platform,
} from 'react-native';
import {Camera, useCameraDevices} from 'react-native-vision-camera';
import ImagePicker from 'react-native-image-crop-picker';

interface CameraViewProps {
  onCapture: (uri: string) => void;
}

const CameraView: React.FC<CameraViewProps> = ({onCapture}) => {
  const cameraRef = useRef<Camera>(null);
  const devices = useCameraDevices();
  const device = devices.find(d => d.position === 'front') ?? devices[0];

  const [isTakingPhoto, setIsTakingPhoto] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);

  // Kamera izni kontrolü
  useEffect(() => {
    (async () => {
      const status = await Camera.getCameraPermissionStatus();
      if (status !== 'granted') {
        await Camera.requestCameraPermission();
      }
    })();
  }, []);

  const requestGalleryPermission = async () => {
    if (Platform.OS === 'android') {
      const permission =
        Platform.Version >= 33
          ? PermissionsAndroid.PERMISSIONS.READ_MEDIA_IMAGES
          : PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE;

      const result = await PermissionsAndroid.request(permission, {
        title: 'Galeri Erişimi',
        message: 'Galeriye erişim izni vermeniz gerekiyor.',
        buttonPositive: 'Tamam',
      });

      return result === PermissionsAndroid.RESULTS.GRANTED;
    }
    return true;
  };

  const pickFromGallery = async () => {
    const hasPermission = await requestGalleryPermission();
    if (!hasPermission) {
      Alert.alert('İzin Gerekli', 'Lütfen galeri erişim izni verin.');
      return;
    }

    try {
      const image = await ImagePicker.openPicker({
        mediaType: 'photo',
        cropping: false,
      });

      if (image?.path) {
        onCapture(image.path);
      }
    } catch (err: any) {
      if (err.code !== 'E_PICKER_CANCELLED') {
        console.error('🖼️ Galeri seçim hatası:', err);
        Alert.alert('Hata', 'Galeri açılırken bir sorun oluştu.');
      }
    }
  };

  const takePhoto = async () => {
    if (!cameraRef.current || isTakingPhoto || !cameraReady) return;

    try {
      setIsTakingPhoto(true);
      const photo = await cameraRef.current.takePhoto({});
      onCapture(`file://${photo.path}`);
    } catch (error) {
      console.error('📸 Fotoğraf çekme hatası:', error);
      Alert.alert('Hata', 'Fotoğraf çekilemedi.');
    } finally {
      setIsTakingPhoto(false);
    }
  };

  if (!device) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#000" />
        <Text>Kamera yükleniyor...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Camera
        ref={cameraRef}
        style={StyleSheet.absoluteFill}
        device={device}
        isActive={true}
        photo={true}
        onInitialized={() => setCameraReady(true)}
      />

      <View style={styles.controls}>
        <TouchableOpacity style={styles.button} onPress={pickFromGallery}>
          <Text style={styles.buttonText}>Galeriden Seç</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.captureButton,
            (!cameraReady || isTakingPhoto) && styles.disabledButton,
          ]}
          onPress={takePhoto}
          disabled={!cameraReady || isTakingPhoto}>
          <Text style={styles.captureText}>Fotoğraf</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  controls: {
    position: 'absolute',
    bottom: 30,
    left: 0,
    right: 0,
    alignItems: 'center',
    gap: 12,
  },
  button: {
    backgroundColor: '#444',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
  },
  buttonText: {
    color: '#FFF',
    fontSize: 14,
  },
  captureButton: {
    backgroundColor: '#000',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 24,
  },
  disabledButton: {
    opacity: 0.5,
  },
  captureText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default CameraView;

import {useEffect, useState} from 'react';
import {Camera} from 'react-native-vision-camera';

const useCameraPermission = () => {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);

  useEffect(() => {
    const checkPermission = async () => {
      const status = await Camera.getCameraPermissionStatus();
      if (status === 'authorized' || status === 'granted') {
        setHasPermission(true);
      } else {
        const newStatus = await Camera.requestCameraPermission();
        setHasPermission(newStatus === 'authorized' || newStatus === 'granted');
      }
    };

    checkPermission();
  }, []);

  return hasPermission;
};

export default useCameraPermission;

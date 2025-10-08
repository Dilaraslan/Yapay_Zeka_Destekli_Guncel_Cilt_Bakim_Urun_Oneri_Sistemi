//SkinTypeCard.tsx
import React from 'react';
import {Text, StyleSheet, Image, TouchableOpacity} from 'react-native';
import {SkinType} from '../types';
import {useNavigation} from '@react-navigation/native';
import {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {RootStackParamList} from '../types';

interface SkinTypeCardProps {
  type: SkinType;
  image: any;
  onPress?: () => void;
}

const SkinTypeCard: React.FC<SkinTypeCardProps> = ({type, image, onPress}) => {
  const navigation =
    useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  const getSkinTypeParam = (uiType: SkinType): string => {
    switch (uiType) {
      case 'Akne':
        return 'acne';
      case 'Kırışıklık':
        return 'wrinkle';
      case 'Leke':
        return 'stain';
      case 'Koyu Halka':
        return 'black_circle';
      case 'Gözenek': // Yeni eklenen Gözenek tipi
        return 'pockmark';
      default:
        return 'acne';
    }
  };

  const handlePress = () => {
    if (onPress) {
      onPress();
    } else {
      const skinTypeParam = getSkinTypeParam(type);
      navigation.navigate('SkinTypeScreen', {skinType: skinTypeParam});
    }
  };

  return (
    <TouchableOpacity style={styles.card} onPress={handlePress}>
      <Image source={image} style={styles.image} />
      <Text style={styles.label}>{type}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    width: 70,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  image: {
    width: 75,
    height: 80,
    borderRadius: 20,
    marginBottom: 6,
    backgroundColor: '#eee',
  },
  label: {
    fontSize: 14,
    color: '#607d8b',
    textAlign: 'center',
  },
});

export default SkinTypeCard;

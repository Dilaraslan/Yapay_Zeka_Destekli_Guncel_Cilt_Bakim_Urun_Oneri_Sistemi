//ProductCard.tsx
import React from 'react';
import {View, Text, StyleSheet, TouchableOpacity, Image} from 'react-native';
import {Product} from '../services/apiService';
//import Icon from 'react-native-vector-icons/FontAwesome';

interface ProductCardProps {
  product: Product;
  onPress?: () => void;
}

const ProductCard: React.FC<ProductCardProps> = ({product, onPress}) => {
  const imageSource: {uri: string} = {
    uri: product.image_url || 'https://via.placeholder.com/150',
  };

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={onPress}
      disabled={!product.purchase_link}>
      <View style={styles.card}>
        {/* Görsel Bölümü - Grid'in sol sütunu */}
        <View style={styles.imageColumn}>
          <Image
            source={imageSource}
            style={styles.productImage}
            resizeMode="contain"
          />
        </View>

        {/* İçerik Bölümü - Grid'in sağ sütunu */}
        <View style={styles.contentContainer}>
          {product.brand && <Text style={styles.brand}>{product.brand}</Text>}

          <Text style={styles.name} numberOfLines={2}>
            {product.name || 'İsimsiz Ürün'}
          </Text>

          {product.price && <Text style={styles.price}>{product.price} ₺</Text>}

          <View style={styles.linkContainer}>
            <Image
              source={require('../assets/shopping-cart.png')}
              style={{width: 18, height: 18, tintColor: '#888'}}
            />
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 12,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    overflow: 'hidden',
    flexDirection: 'row',
    borderWidth: 1,
    borderColor: '#EEEEEE',
  },
  imageColumn: {
    width: 80,
    backgroundColor: '#f2f2f2',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 4,
  },
  productImage: {
    width: '100%',
    height: 72,
    alignSelf: 'center',
  },
  contentContainer: {
    flex: 1,
    padding: 12,
    justifyContent: 'space-between',
  },
  brand: {
    fontSize: 12,
    color: '#555555',
    marginBottom: 2,
  },
  name: {
    fontSize: 15,
    fontWeight: '600',
    color: '#000000',
    flex: 1,
    marginBottom: 4,
  },
  price: {
    fontSize: 16,
    fontWeight: '700',
    color: '#000000',
    marginTop: 4,
  },
  linkContainer: {
    alignSelf: 'flex-end',
    marginTop: 2,
  },
});

export default ProductCard;

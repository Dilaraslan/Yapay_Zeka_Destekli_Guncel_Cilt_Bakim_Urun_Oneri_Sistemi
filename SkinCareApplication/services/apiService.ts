//import axios from 'axios';

//const BASE_URL = 'http://192.168.1.16:8000'; // kendi IP adresinle değiştir

// src/services/apiService.ts

export interface Product {
  name?: string;
  purchase_link: string;
  price?: string;
  rating?: number;
  image_url?: string;
  brand?: string;
}

// For image analysis endpoint
export interface SkincareRecommendation {
  detected_skin_issues: string[];
  recommended_products: Record<string, Product[]>;
}

// For direct recommendation endpoint
export interface DirectRecommendation {
  [key: string]: Product[]; // key is the skin issue type
}

// New skin issue info interface
export interface SkinIssueInfo {
  title: string;
  description: string;
  causes: string[];
  daily_care: string[];
  tips: string[];
}

// New skin issue with products response
export interface SkinIssueWithProducts {
  info: SkinIssueInfo;
  products: Product[];
}

export const analyzeImage = async (
  imageUri: string,
): Promise<SkincareRecommendation> => {
  const formData = new FormData();

  // Add image to form data with proper naming
  formData.append('file', {
    uri: imageUri,
    name: 'photo.jpg',
    type: 'image/jpeg',
  } as any);

  // Add optional parameters
  formData.append('product_count', '3');

  try {
    console.log('Sending request to API...');
    console.log('Image URI:', imageUri);

    // Ensure the IP address is correct and the server is running
    const apiUrl = `http://192.168.1.114:8000/analyze-and-recommend`;
    console.log('API URL:', apiUrl);

    const response = await fetch(apiUrl, {
      method: 'POST',
      body: formData,
      headers: {
        // Do not set Content-Type header as it's automatically set with the boundary
        Accept: 'application/json',
      },
    });

    console.log('Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API error response:', errorText);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const json = await response.json();
    console.log(
      'API response:',
      JSON.stringify(json).substring(0, 200) + '...',
    );

    return json as SkincareRecommendation;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// Function for direct recommendations without image analysis
export const getRecommendationsForIssue = async (
  skinIssue: string,
  productCount: number = 3,
  minRating?: number,
): Promise<DirectRecommendation> => {
  try {
    console.log('Getting recommendations for skin issue:', skinIssue);

    const apiUrl = `http://192.168.1.114:8000/recommend`;
    const params = new URLSearchParams({
      skin_issue: skinIssue,
      product_count: productCount.toString(),
    });

    if (minRating !== undefined) {
      params.append('min_rating', minRating.toString());
    }

    const urlWithParams = `${apiUrl}?${params.toString()}`;
    console.log('API URL:', urlWithParams);

    const response = await fetch(urlWithParams, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    console.log('Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API error response:', errorText);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const json = await response.json();
    console.log(
      'API response:',
      JSON.stringify(json).substring(0, 200) + '...',
    );

    return json as DirectRecommendation;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// New function to get skin issue information and recommended products
export const getSkinIssueInfo = async (
  issueType: string,
  productCount: number = 3,
  minRating?: number,
): Promise<SkinIssueWithProducts> => {
  try {
    console.log('Getting skin issue info for:', issueType);

    const apiUrl = `http://192.168.1.114:8000/skin-issue/${issueType}`;
    const params = new URLSearchParams({
      product_count: productCount.toString(),
    });

    if (minRating !== undefined) {
      params.append('min_rating', minRating.toString());
    }

    const urlWithParams = `${apiUrl}?${params.toString()}`;
    console.log('API URL:', urlWithParams);

    const response = await fetch(urlWithParams, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    console.log('Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API error response:', errorText);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const json = await response.json();
    console.log(
      'API response:',
      JSON.stringify(json).substring(0, 200) + '...',
    );

    return json as SkinIssueWithProducts;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// sadece bilgi
//export const getSkinIssueInfoOnly = async (issueType: string): Promise<SkinIssueInfo> => {
//  const res = await fetch(http://192.168.1.16:8000/skin-issue/info/${issueType});
//  if (!res.ok) throw new Error("Cilt bilgisi alınamadı");
//  return await res.json();
//};

// sadece ürünler
export const getSkinIssueProductsOnly = async (
  issueType: string,
  productCount: number = 3,
): Promise<Product[]> => {
  const res = await fetch(
    `http://192.168.1.114:8000/skin-issue/products/${issueType}?product_count=${productCount}`,
  );
  if (!res.ok) throw new Error('Ürünler alınamadı');
  return await res.json();
};

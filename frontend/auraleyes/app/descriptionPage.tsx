import React, { useState } from 'react';
import { View, Image, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native'; 
import { FC } from 'react';
import { useLocalSearchParams, useRouter } from 'expo-router';



const DescriptionPage = () => {
  // Assuming the image is passed via navigation params
  const router = useRouter() 
  const params = useLocalSearchParams(); 
  
  const { image } = params.image ? JSON.parse(params.image as string) : null;
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null); 

  // Function to process the image with the API
  const processImage = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Create form data to send the image
      const formData = new FormData(); 
      const imageData = await fetch(image.uri);
      const blob = await imageData.blob();
      formData.append('image', blob, 'upload.jpg');
      
      // Make the API call
      const response = await fetch('https://your-api-endpoint.com/process', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Parse the response
      const responseData = await response.json();
      
      if (!response.ok) {
        throw new Error(responseData.message || 'Failed to process image');
      }
      
      setApiResponse(responseData);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      console.error('API error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Function for the second button
  const handleSecondButton = () => {
    // Implement whatever functionality you need for this button
    console.log('Second button pressed');
  };

  return (
    <View style={styles.container}>
      {/* Top button */}
      <TouchableOpacity style={styles.button} onPress={()=> router.push('/home')}>
        <Text style={styles.buttonText}>Process Image</Text>
      </TouchableOpacity>
      
      {/* Image display */}
      {image && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: image.uri }} style={styles.image} resizeMode="contain" />
        </View>
      )}
      
      {/* Second button */}
      <TouchableOpacity style={styles.button} onPress={handleSecondButton}>
        <Text style={styles.buttonText}>Second Action</Text>
      </TouchableOpacity>
      
      {/* Loading indicator */}
      {loading && (
        <View style={styles.loaderContainer}>
          <ActivityIndicator size="large" color="#0000ff" />
          <Text style={styles.loaderText}>Processing image...</Text>
        </View>
      )}
      
      {/* Error message */}
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Error: {error}</Text>
        </View>
      )}
      
      {/* API response display at the bottom */}
      {apiResponse && (
        <View style={styles.responseContainer}>
          <Text style={styles.responseTitle}>API Response:</Text>
          <Text style={styles.responseText}>
            {typeof apiResponse === 'object' 
              ? JSON.stringify(apiResponse, null, 2) 
              : apiResponse.toString()}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  button: {
    backgroundColor: '#3498db',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginVertical: 10,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  imageContainer: {
    alignItems: 'center',
    marginVertical: 20,
    borderRadius: 8,
    overflow: 'hidden',
    backgroundColor: '#fff',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.5,
  },
  image: {
    width: '100%',
    height: 300,
  },
  loaderContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  loaderText: {
    marginTop: 10,
    fontSize: 16,
    color: '#555',
  },
  errorContainer: {
    backgroundColor: '#ffebee',
    padding: 12,
    borderRadius: 8,
    marginVertical: 10,
  },
  errorText: {
    color: '#d32f2f',
    fontSize: 14,
  },
  responseContainer: {
    marginTop: 'auto', // Push to bottom
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.5,
  },
  responseTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  responseText: {
    fontSize: 14,
    color: '#333',
  },
});

export default DescriptionPage
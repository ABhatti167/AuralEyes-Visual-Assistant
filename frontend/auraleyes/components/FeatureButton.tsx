import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

/**
 * FeatureButton Component
 * @param {Object} props
 * @param {number} props.containerHeight - Height of the button container
 * @param {string} props.text - Button text content
 * @param {string} props.icon - Icon name from Ionicons (optional)
 * @param {string} props.color - Background color of the button
 * @param {Function} props.onPress - Function to call when button is pressed
 */

interface FeatureButtonProps {
  containerHeight: number;
  text: string;
  icon?: keyof typeof Ionicons.glyphMap;
  color: string;
  onPress: () => void;
}

const FeatureButton: React.FC<FeatureButtonProps> = ({ containerHeight, text, icon, color, onPress }) => {
  return (
    <TouchableOpacity 
      style={[
        styles.container, 
        { 
          height: containerHeight,
          backgroundColor: color 
        }
      ]}
      onPress={onPress}
    >
      {icon && (
        <View style={styles.iconContainer}>
          <Ionicons name={icon} size={64} color="white" />
        </View>
      )}
      <Text style={styles.text}>
        {text}
      </Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    borderRadius: 8,
    padding: 20,
    justifyContent: 'center',
    marginVertical: 10,
  },
  iconContainer: {
    marginBottom: 10,
  },
  text: {
    color: 'white',
    fontSize: 64,
    fontWeight: 'bold',
  },
});

export default FeatureButton;
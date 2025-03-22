import { StyleSheet, Image, Platform, View, SafeAreaView } from 'react-native';

import { Collapsible } from '@/components/Collapsible';
import { ExternalLink } from '@/components/ExternalLink';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';
import FeatureButton from '@/components/FeatureButton';

export default function TabTwoScreen() { 


  return ( 
    <SafeAreaView style={styles.wrapper}>
    <View style={styles.mainView}>
    <FeatureButton
      containerHeight={350}
      text="Live Navigation"
      icon="videocam-outline"
      color="#D94148"
      onPress={() => console.log('Live Navigation pressed')}
    />
    
    <FeatureButton
      containerHeight={250}
      text="Text Reader"
      color="#F7D63E"
      onPress={() => console.log('Text Reader pressed')}
    />
  </View> 
  </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  wrapper:{  
    flex: 1, 
    justifyContent: 'center',
    alignItems: 'center',  
    padding: 20, 
    backgroundColor: 'black'


  },  

  mainView:{ 
    width: '100%',
  }, 

  headerImage: {
    color: '#808080',
    bottom: -90,
    left: -35,
    position: 'absolute',
  },
  titleContainer: {
    flexDirection: 'row',
    gap: 8,
  },
});

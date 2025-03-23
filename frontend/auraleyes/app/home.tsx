import { StyleSheet, Image, Platform, View, SafeAreaView } from 'react-native';

import FeatureButton from '@/components/FeatureButton';
import {  useRouter } from 'expo-router';


export default function HomeScreen() { 

  const router = useRouter() 
  return ( 
    <SafeAreaView style={styles.wrapper}>
    <View style={styles.mainView}>
    <FeatureButton
      containerHeight={350}
      text="Live Navigation"
      icon="videocam-outline"
      color="#D94148"
      onPress={() =>  router.push('/livefeed')}
    />
    
    <FeatureButton
      containerHeight={250}
      text="Text Reader" 
      icon='document-text-outline'
      color="#F7D63E"
      onPress={() => router.push('/textCam')}
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

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function HomePage() {
  const [language, setLanguage] = useState<'tamil' | 'english'>('tamil');
  const [system, setSystem] = useState<'vakkiam' | 'thirukkanitham'>('vakkiam');

  const toggleLanguage = () => {
    setLanguage(language === 'tamil' ? 'english' : 'tamil');
  };

  const toggleSystem = () => {
    setSystem(system === 'vakkiam' ? 'thirukkanitham' : 'vakkiam');
  };

  const getText = (tamil: string, english: string) => {
    return language === 'tamil' ? tamil : english;
  };

  const navigationOptions = [
    {
      title: getText('ஜாதகம் கணித்தல்', 'Generate Horoscope'),
      subtitle: getText('தனிப்பட்ட ஜாதகம் உருவாக்குதல்', 'Create Personal Horoscope'),
      icon: 'planet-outline',
      color: '#4A90E2',
      route: '/horoscope'
    },
    {
      title: getText('திருமணப் பொருத்தம்', 'Marriage Compatibility'),
      subtitle: getText('திருமணப் பொருத்தம் பார்த்தல்', 'Check Marriage Compatibility'),
      icon: 'heart-outline',
      color: '#E74C3C',
      route: '/compatibility'
    },
    {
      title: getText('சேமிக்கப்பட்ட விவரங்கள்', 'Saved Profiles'),
      subtitle: getText('ஜாதகங்களை சேமித்தல்', 'Manage Birth Profiles'),
      icon: 'person-outline',
      color: '#27AE60',
      route: '/profiles'
    },
    {
      title: getText('தினசரி பஞ்சாங்கம்', 'Daily Panchangam'),
      subtitle: getText('இன்றைய பஞ்சாங்க விவரங்கள்', "Today's Panchangam Details"),
      icon: 'calendar-outline',
      color: '#F39C12',
      route: '/panchangam',
      systemRestriction: 'thirukkanitham'
    }
  ];

  const handleNavigation = (route: string, systemRestriction?: string) => {
    if (systemRestriction && system !== systemRestriction) {
      Alert.alert(
        getText('அமைப்பு தேவை', 'System Required'),
        getText(
          'இந்த அம்சம் திருக்கணித அமைப்பில் மட்டுமே கிடைக்கும்',
          'This feature is only available in Thirukkanitham system'
        ),
        [
          {
            text: getText('ரத்து செய்', 'Cancel'),
            style: 'cancel'
          },
          {
            text: getText('மாற்று', 'Switch'),
            onPress: () => {
              setSystem('thirukkanitham');
              // Navigate after switching
              setTimeout(() => {
                // TODO: Navigate to route
                console.log('Navigate to:', route);
              }, 100);
            }
          }
        ]
      );
      return;
    }
    
    // TODO: Navigate to route
    console.log('Navigate to:', route, 'with system:', system);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#2C3E50" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.headerTitle}>
            {getText('தமிழ் ஜோதிடம்', 'Tamil Astrology')}
          </Text>
          <Text style={styles.headerSubtitle}>
            {getText('பாரம்பரிய ஜோதிட சேவை', 'Traditional Astrology Service')}
          </Text>
        </View>
        
        <TouchableOpacity 
          style={styles.languageToggle}
          onPress={toggleLanguage}
        >
          <Text style={styles.languageText}>
            {language === 'tamil' ? 'த' : 'En'}
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* System Selection */}
        <View style={styles.systemSection}>
          <Text style={styles.sectionTitle}>
            {getText('அமைப்பு தேர்வு', 'System Selection')}
          </Text>
          
          <View style={styles.systemButtons}>
            <TouchableOpacity
              style={[
                styles.systemButton,
                system === 'vakkiam' && styles.systemButtonActive
              ]}
              onPress={() => setSystem('vakkiam')}
            >
              <Text style={[
                styles.systemButtonText,
                system === 'vakkiam' && styles.systemButtonTextActive
              ]}>
                {getText('வாக்கிய பஞ்சாங்கம்', 'Vakkiam Panchangam')}
              </Text>
              <Text style={[
                styles.systemButtonSubtext,
                system === 'vakkiam' && styles.systemButtonSubtextActive
              ]}>
                {getText('பாரம்பரிய கணக்கீடு', 'Traditional Calculation')}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[
                styles.systemButton,
                system === 'thirukkanitham' && styles.systemButtonActive
              ]}
              onPress={() => setSystem('thirukkanitham')}
            >
              <Text style={[
                styles.systemButtonText,
                system === 'thirukkanitham' && styles.systemButtonTextActive
              ]}>
                {getText('திருக்கணித பஞ்சாங்கம்', 'Thirukkanitham Panchangam')}
              </Text>
              <Text style={[
                styles.systemButtonSubtext,
                system === 'thirukkanitham' && styles.systemButtonSubtextActive
              ]}>
                {getText('திருக்கணித கணக்கீடு', 'Thirukkanitham Calculation')}
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Navigation Options */}
        <View style={styles.navigationSection}>
          <Text style={styles.sectionTitle}>
            {getText('சேவைகள்', 'Services')}
          </Text>
          
          {navigationOptions.map((option, index) => {
            const isDisabled = option.systemRestriction && system !== option.systemRestriction;
            
            return (
              <TouchableOpacity
                key={index}
                style={[
                  styles.navigationCard,
                  isDisabled && styles.navigationCardDisabled
                ]}
                onPress={() => handleNavigation(option.route, option.systemRestriction)}
                disabled={isDisabled}
              >
                <View style={[styles.navigationIcon, { backgroundColor: `${option.color}20` }]}>
                  <Ionicons 
                    name={option.icon as any} 
                    size={28} 
                    color={isDisabled ? '#95A5A6' : option.color} 
                  />
                </View>
                
                <View style={styles.navigationContent}>
                  <Text style={[
                    styles.navigationTitle,
                    isDisabled && styles.navigationTitleDisabled
                  ]}>
                    {option.title}
                  </Text>
                  <Text style={[
                    styles.navigationSubtitle,
                    isDisabled && styles.navigationSubtitleDisabled
                  ]}>
                    {option.subtitle}
                  </Text>
                  {option.systemRestriction && (
                    <Text style={styles.systemRestriction}>
                      {getText('திருக்கணித மட்டும்', 'Thirukkanitham Only')}
                    </Text>
                  )}
                </View>
                
                <Ionicons 
                  name="chevron-forward" 
                  size={20} 
                  color={isDisabled ? '#95A5A6' : '#7F8C8D'} 
                />
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Current System Info */}
        <View style={styles.infoSection}>
          <View style={styles.infoCard}>
            <Text style={styles.infoTitle}>
              {getText('தற்போதைய அமைப்பு', 'Current System')}
            </Text>
            <Text style={styles.infoContent}>
              {system === 'vakkiam' 
                ? getText('வாக்கிய பஞ்சாங்கம்', 'Vakkiam Panchangam')
                : getText('திருக்கணித பஞ்சாங்கம்', 'Thirukkanitham Panchangam')
              }
            </Text>
            
            <Text style={styles.infoDescription}>
              {system === 'vakkiam'
                ? getText(
                    'பாரம்பரிய வாக்கிய முறையில் கணிக்கப்படும் ஜோதிட சேவை',
                    'Traditional Vakkiam method astrology calculations'
                  )
                : getText(
                    'திருக்கணித முறையில் கணிக்கப்படும் ஜோதிட சேவை மற்றும் தினசரி பஞ்சாங்கம்',
                    'Thirukkanitham method astrology calculations with daily Panchangam'
                  )
              }
            </Text>
          </View>
        </View>

        {/* About Section */}
        <View style={styles.aboutSection}>
          <Text style={styles.aboutTitle}>
            {getText('பற்றி', 'About')}
          </Text>
          <Text style={styles.aboutText}>
            {getText(
              'இது ஒரு பாரம்பரிய தமிழ் ஜோதிட மொபைல் பயன்பாட்டு ஆகும். வாக்கிய மற்றும் திருக்கணித இரு முறைகளிலும் ஜாதகம் கணித்தல், திருமணப் பொருத்தம் பார்த்தல் போன்ற சேவைகள் வழங்கப்படுகின்றன.',
              'This is a traditional Tamil astrology mobile application. It provides services like horoscope generation and marriage compatibility checking in both Vakkiam and Thirukkanitham systems.'
            )}
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    backgroundColor: '#2C3E50',
    paddingHorizontal: 20,
    paddingVertical: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  headerLeft: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#BDC3C7',
  },
  languageToggle: {
    backgroundColor: '#34495E',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    minWidth: 44,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  languageText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  systemSection: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 12,
    marginTop: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 16,
  },
  systemButtons: {
    gap: 12,
  },
  systemButton: {
    borderWidth: 2,
    borderColor: '#E8E8E8',
    borderRadius: 12,
    padding: 16,
    backgroundColor: '#FFFFFF',
  },
  systemButtonActive: {
    borderColor: '#4A90E2',
    backgroundColor: '#F0F8FF',
  },
  systemButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#34495E',
    marginBottom: 4,
  },
  systemButtonTextActive: {
    color: '#4A90E2',
  },
  systemButtonSubtext: {
    fontSize: 14,
    color: '#7F8C8D',
  },
  systemButtonSubtextActive: {
    color: '#5BA0F2',
  },
  navigationSection: {
    marginTop: 24,
  },
  navigationCard: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 12,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  navigationCardDisabled: {
    opacity: 0.6,
  },
  navigationIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  navigationContent: {
    flex: 1,
  },
  navigationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 4,
  },
  navigationTitleDisabled: {
    color: '#95A5A6',
  },
  navigationSubtitle: {
    fontSize: 14,
    color: '#7F8C8D',
    marginBottom: 4,
  },
  navigationSubtitleDisabled: {
    color: '#BDC3C7',
  },
  systemRestriction: {
    fontSize: 12,
    color: '#E67E22',
    fontStyle: 'italic',
  },
  infoSection: {
    marginTop: 24,
  },
  infoCard: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 8,
  },
  infoContent: {
    fontSize: 18,
    fontWeight: '500',
    color: '#4A90E2',
    marginBottom: 12,
  },
  infoDescription: {
    fontSize: 14,
    color: '#7F8C8D',
    lineHeight: 20,
  },
  aboutSection: {
    marginTop: 24,
    marginBottom: 32,
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  aboutTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 12,
  },
  aboutText: {
    fontSize: 14,
    color: '#7F8C8D',
    lineHeight: 20,
  },
});

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  TextInput,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import DateTimePicker from '@react-native-community/datetimepicker';
import { router } from 'expo-router';

interface BirthDetails {
  name: string;
  date_of_birth: string;
  time_of_birth: string;
  place_of_birth: string;
  latitude: string;
  longitude: string;
  timezone: string;
  time_correction: string;
}

export default function HoroscopePage() {
  const [language, setLanguage] = useState<'tamil' | 'english'>('tamil');
  const [system, setSystem] = useState<'vakkiam' | 'thirukkanitham'>('vakkiam');
  const [loading, setLoading] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  
  const [birthDetails, setBirthDetails] = useState<BirthDetails>({
    name: '',
    date_of_birth: new Date().toISOString().split('T')[0],
    time_of_birth: '12:00',
    place_of_birth: '',
    latitude: '',
    longitude: '',
    timezone: 'IST',
    time_correction: '0',
  });

  const getText = (tamil: string, english: string) => {
    return language === 'tamil' ? tamil : english;
  };

  const handleInputChange = (field: keyof BirthDetails, value: string) => {
    setBirthDetails(prev => ({ ...prev, [field]: value }));
  };

  const handleDateChange = (event: any, selectedDate?: Date) => {
    setShowDatePicker(false);
    if (selectedDate) {
      handleInputChange('date_of_birth', selectedDate.toISOString().split('T')[0]);
    }
  };

  const handleTimeChange = (event: any, selectedTime?: Date) => {
    setShowTimePicker(false);
    if (selectedTime) {
      const hours = selectedTime.getHours().toString().padStart(2, '0');
      const minutes = selectedTime.getMinutes().toString().padStart(2, '0');
      handleInputChange('time_of_birth', `${hours}:${minutes}`);
    }
  };

  const validateForm = (): boolean => {
    if (!birthDetails.name.trim()) {
      Alert.alert(
        getText('பெயர் தேவை', 'Name Required'),
        getText('தயவுசெய்து பெயரை உள்ளிடவும்', 'Please enter the name')
      );
      return false;
    }
    
    if (!birthDetails.place_of_birth.trim()) {
      Alert.alert(
        getText('பிறந்த இடம் தேவை', 'Birth Place Required'),
        getText('தயவுசெய்து பிறந்த இடத்தை உள்ளிடவும்', 'Please enter the birth place')
      );
      return false;
    }
    
    if (!birthDetails.latitude.trim() || !birthDetails.longitude.trim()) {
      Alert.alert(
        getText('அட்சரேகை மற்றும் தீர்க்கரேகை தேவை', 'Latitude and Longitude Required'),
        getText('தயவுசெய்து அட்சரேகை மற்றும் தீர்க்கரேகை உள்ளிடவும்', 'Please enter latitude and longitude')
      );
      return false;
    }
    
    // Validate latitude and longitude ranges
    const lat = parseFloat(birthDetails.latitude);
    const lng = parseFloat(birthDetails.longitude);
    
    if (isNaN(lat) || lat < -90 || lat > 90) {
      Alert.alert(
        getText('தவறான அட்சரேகை', 'Invalid Latitude'),
        getText('அட்சரேகை -90 முதல் 90 வரை இருக்க வேண்டும்', 'Latitude must be between -90 and 90')
      );
      return false;
    }
    
    if (isNaN(lng) || lng < -180 || lng > 180) {
      Alert.alert(
        getText('தவறான தீர்க்கரேகை', 'Invalid Longitude'),
        getText('தீர்க்கரேகை -180 முதல் 180 வரை இருக்க வேண்டும்', 'Longitude must be between -180 and 180')
      );
      return false;
    }
    
    return true;
  };

  const generateHoroscope = async () => {
    if (!validateForm()) return;
    
    setLoading(true);
    
    try {
      const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/horoscope`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          birth_details: {
            name: birthDetails.name,
            date_of_birth: birthDetails.date_of_birth,
            time_of_birth: birthDetails.time_of_birth + ':00',  // Add seconds
            place_of_birth: birthDetails.place_of_birth,
            latitude: parseFloat(birthDetails.latitude),
            longitude: parseFloat(birthDetails.longitude),
            timezone: birthDetails.timezone,
            time_correction: parseInt(birthDetails.time_correction) || 0,
          },
          system: system,
          language: language,
        }),
      });

      const result = await response.json();
      
      if (response.ok) {
        // Navigate to horoscope result page
        Alert.alert(
          getText('வெற்றி', 'Success'),
          getText('ஜாதகம் வெற்றிகரமாக உருவாக்கப்பட்டது', 'Horoscope generated successfully'),
          [
            {
              text: getText('சரி', 'OK'),
              onPress: () => {
                // TODO: Navigate to result page with horoscope data
                console.log('Horoscope result:', result);
              }
            }
          ]
        );
      } else {
        throw new Error(result.detail || 'Failed to generate horoscope');
      }
    } catch (error) {
      console.error('Error generating horoscope:', error);
      Alert.alert(
        getText('பிழை', 'Error'),
        getText(
          'ஜாதகம் உருவாக்குவதில் பிழை ஏற்பட்டது',
          'Error occurred while generating horoscope'
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#2C3E50" />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
        </TouchableOpacity>
        
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>
            {getText('ஜாதகம் கணித்தல்', 'Generate Horoscope')}
          </Text>
        </View>
        
        <TouchableOpacity 
          style={styles.languageToggle}
          onPress={() => setLanguage(language === 'tamil' ? 'english' : 'tamil')}
        >
          <Text style={styles.languageText}>
            {language === 'tamil' ? 'த' : 'En'}
          </Text>
        </TouchableOpacity>
      </View>

      <KeyboardAvoidingView 
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
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
              </TouchableOpacity>
            </View>
          </View>

          {/* Birth Details Form */}
          <View style={styles.formSection}>
            <Text style={styles.sectionTitle}>
              {getText('பிறப்பு விவரங்கள்', 'Birth Details')}
            </Text>
            
            {/* Name */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('பெயர்', 'Name')} *
              </Text>
              <TextInput
                style={styles.textInput}
                value={birthDetails.name}
                onChangeText={(value) => handleInputChange('name', value)}
                placeholder={getText('உங்கள் பெயரை உள்ளிடவும்', 'Enter your name')}
                placeholderTextColor="#95A5A6"
              />
            </View>
            
            {/* Birth Date */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('பிறந்த தேதி', 'Date of Birth')} *
              </Text>
              <TouchableOpacity
                style={styles.dateTimeButton}
                onPress={() => setShowDatePicker(true)}
              >
                <Text style={styles.dateTimeText}>
                  {new Date(birthDetails.date_of_birth).toLocaleDateString()}
                </Text>
                <Ionicons name="calendar-outline" size={20} color="#7F8C8D" />
              </TouchableOpacity>
            </View>
            
            {/* Birth Time */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('பிறந்த நேரம்', 'Time of Birth')} *
              </Text>
              <TouchableOpacity
                style={styles.dateTimeButton}
                onPress={() => setShowTimePicker(true)}
              >
                <Text style={styles.dateTimeText}>
                  {birthDetails.time_of_birth}
                </Text>
                <Ionicons name="time-outline" size={20} color="#7F8C8D" />
              </TouchableOpacity>
            </View>
            
            {/* Birth Place */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('பிறந்த இடம்', 'Place of Birth')} *
              </Text>
              <TextInput
                style={styles.textInput}
                value={birthDetails.place_of_birth}
                onChangeText={(value) => handleInputChange('place_of_birth', value)}
                placeholder={getText('நகரம், மாநிலம், நாடு', 'City, State, Country')}
                placeholderTextColor="#95A5A6"
              />
            </View>
            
            {/* Latitude */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('அட்சரேகை (Latitude)', 'Latitude')} *
              </Text>
              <TextInput
                style={styles.textInput}
                value={birthDetails.latitude}
                onChangeText={(value) => handleInputChange('latitude', value)}
                placeholder={getText('உதா: 13.0827', 'e.g., 13.0827')}
                placeholderTextColor="#95A5A6"
                keyboardType="numeric"
              />
            </View>
            
            {/* Longitude */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('தீர்க்கரேகை (Longitude)', 'Longitude')} *
              </Text>
              <TextInput
                style={styles.textInput}
                value={birthDetails.longitude}
                onChangeText={(value) => handleInputChange('longitude', value)}
                placeholder={getText('உதா: 80.2707', 'e.g., 80.2707')}
                placeholderTextColor="#95A5A6"
                keyboardType="numeric"
              />
            </View>
            
            {/* Timezone */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('நேர மண்டலம்', 'Timezone')}
              </Text>
              <TextInput
                style={styles.textInput}
                value={birthDetails.timezone}
                onChangeText={(value) => handleInputChange('timezone', value)}
                placeholder={getText('IST, UTC+5:30', 'IST, UTC+5:30')}
                placeholderTextColor="#95A5A6"
              />
            </View>
            
            {/* Time Correction */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('நேரத் திருத்தம் (நிமிடங்களில்)', 'Time Correction (in minutes)')}
              </Text>
              <TextInput
                style={styles.textInput}
                value={birthDetails.time_correction}
                onChangeText={(value) => handleInputChange('time_correction', value)}
                placeholder={getText('0', '0')}
                placeholderTextColor="#95A5A6"
                keyboardType="numeric"
              />
            </View>
          </View>
        </ScrollView>
        
        {/* Generate Button */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.generateButton, loading && styles.generateButtonDisabled]}
            onPress={generateHoroscope}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#FFFFFF" size="small" />
            ) : (
              <Text style={styles.generateButtonText}>
                {getText('ஜாதகம் உருவாக்கு', 'Generate Horoscope')}
              </Text>
            )}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
      
      {/* Date Picker */}
      {showDatePicker && (
        <DateTimePicker
          value={new Date(birthDetails.date_of_birth)}
          mode="date"
          display="default"
          onChange={handleDateChange}
          maximumDate={new Date()}
        />
      )}
      
      {/* Time Picker */}
      {showTimePicker && (
        <DateTimePicker
          value={new Date(`2000-01-01T${birthDetails.time_of_birth}:00`)}
          mode="time"
          display="default"
          onChange={handleTimeChange}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  keyboardView: {
    flex: 1,
  },
  header: {
    backgroundColor: '#2C3E50',
    paddingHorizontal: 20,
    paddingVertical: 16,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  backButton: {
    minWidth: 44,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerCenter: {
    flex: 1,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
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
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 16,
  },
  systemButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  systemButton: {
    flex: 1,
    borderWidth: 2,
    borderColor: '#E8E8E8',
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
  },
  systemButtonActive: {
    borderColor: '#4A90E2',
    backgroundColor: '#F0F8FF',
  },
  systemButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#34495E',
    textAlign: 'center',
  },
  systemButtonTextActive: {
    color: '#4A90E2',
  },
  formSection: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 12,
    marginTop: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 8,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#E8E8E8',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#2C3E50',
    backgroundColor: '#FFFFFF',
    minHeight: 48,
  },
  dateTimeButton: {
    borderWidth: 1,
    borderColor: '#E8E8E8',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    minHeight: 48,
  },
  dateTimeText: {
    fontSize: 16,
    color: '#2C3E50',
  },
  buttonContainer: {
    paddingHorizontal: 20,
    paddingVertical: 20,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E8E8E8',
  },
  generateButton: {
    backgroundColor: '#4A90E2',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 56,
  },
  generateButtonDisabled: {
    opacity: 0.6,
  },
  generateButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

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
  Modal,
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

interface GeocodeResult {
  display_name: string;
  lat: string;
  lon: string;
  address?: {
    country?: string;
    state?: string;
    city?: string;
  };
}

export default function HoroscopePage() {
  const [language, setLanguage] = useState<'tamil' | 'english'>('tamil');
  const [system, setSystem] = useState<'vakkiam' | 'thirukkanitham'>('vakkiam');
  const [loading, setLoading] = useState(false);
  const [geocoding, setGeocoding] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedTime, setSelectedTime] = useState(new Date());
  
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

  // Geocoding function to get latitude, longitude from place name
  const geocodePlace = async (placeName: string) => {
    if (!placeName.trim()) return;
    
    setGeocoding(true);
    try {
      // Using Nominatim (OpenStreetMap) geocoding service - it's free
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(placeName)}&limit=1&addressdetails=1`,
        {
          headers: {
            'User-Agent': 'TamilAstrologyApp/1.0'
          }
        }
      );
      
      const data: GeocodeResult[] = await response.json();
      
      if (data && data.length > 0) {
        const result = data[0];
        const lat = parseFloat(result.lat).toFixed(4);
        const lon = parseFloat(result.lon).toFixed(4);
        
        // Update latitude and longitude
        setBirthDetails(prev => ({
          ...prev,
          latitude: lat,
          longitude: lon,
          timezone: getTimezoneFromCoordinates(parseFloat(lat), parseFloat(lon))
        }));
        
        Alert.alert(
          getText('இடம் கண்டறியப்பட்டது', 'Location Found'),
          getText(
            `அட்சரேகை: ${lat}\\nதீர்க்கரேகை: ${lon}\\nநேர மண்டலம்: ${getTimezoneFromCoordinates(parseFloat(lat), parseFloat(lon))}`,
            `Latitude: ${lat}\\nLongitude: ${lon}\\nTimezone: ${getTimezoneFromCoordinates(parseFloat(lat), parseFloat(lon))}`
          )
        );
      } else {
        Alert.alert(
          getText('இடம் கண்டுபிடிக்க முடியவில்லை', 'Location Not Found'),
          getText(
            'தயவுசெய்து வேறு வடிவத்தில் முயற்சிக்கவும் (எ.கா: சென்னை, தமிழ்நாடு, இந்தியா)',
            'Please try a different format (e.g., Chennai, Tamil Nadu, India)'
          )
        );
      }
    } catch (error) {
      console.error('Geocoding error:', error);
      Alert.alert(
        getText('பிழை', 'Error'),
        getText('இடம் கண்டுபிடிக்க முடியவில்லை', 'Could not find location')
      );
    } finally {
      setGeocoding(false);
    }
  };

  // Simple timezone detection based on coordinates
  const getTimezoneFromCoordinates = (lat: number, lon: number): string => {
    // India
    if (lat >= 6.0 && lat <= 37.0 && lon >= 68.0 && lon <= 97.0) {
      return 'IST';
    }
    // Sri Lanka
    if (lat >= 5.9 && lat <= 9.9 && lon >= 79.6 && lon <= 81.9) {
      return 'IST';
    }
    // USA Eastern
    if (lat >= 25.0 && lat <= 49.0 && lon >= -84.0 && lon <= -66.9) {
      return 'EST';
    }
    // USA Pacific
    if (lat >= 32.5 && lat <= 49.0 && lon >= -125.0 && lon <= -114.0) {
      return 'PST';
    }
    // UK
    if (lat >= 50.0 && lat <= 61.0 && lon >= -8.0 && lon <= 2.0) {
      return 'GMT';
    }
    // Default to UTC
    return 'UTC';
  };

  const handleDateChange = (event: any, selectedDate?: Date) => {
    const currentDate = selectedDate || new Date();
    setShowDatePicker(false);
    setSelectedDate(currentDate);
    
    const dateString = currentDate.toISOString().split('T')[0];
    handleInputChange('date_of_birth', dateString);
  };

  const handleTimeChange = (event: any, selectedTime?: Date) => {
    const currentTime = selectedTime || new Date();
    setShowTimePicker(false);
    setSelectedTime(currentTime);
    
    const hours = currentTime.getHours().toString().padStart(2, '0');
    const minutes = currentTime.getMinutes().toString().padStart(2, '0');
    handleInputChange('time_of_birth', `${hours}:${minutes}`);
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
        getText('பிறந்த இடத்தை உள்ளிட்ட பிறகு "இடம் கண்டறி" பொத்தானைச் சொடுக்கவும்', 'Please click "Find Location" button after entering birth place')
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
            time_of_birth: birthDetails.time_of_birth + ':00',
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
        Alert.alert(
          getText('வெற்றி', 'Success'),
          getText('ஜாதகம் வெற்றிகரமாக உருவாக்கப்பட்டது', 'Horoscope generated successfully'),
          [
            {
              text: getText('சரி', 'OK'),
              onPress: () => {
                console.log('Horoscope result:', result);
                // TODO: Navigate to result display page
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
                  {new Date(birthDetails.date_of_birth).toLocaleDateString('en-GB')}
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
                  {birthDetails.time_of_birth} ({birthDetails.timezone})
                </Text>
                <Ionicons name="time-outline" size={20} color="#7F8C8D" />
              </TouchableOpacity>
            </View>
            
            {/* Birth Place with Geocoding */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('பிறந்த இடம்', 'Place of Birth')} *
              </Text>
              <View style={styles.placeInputContainer}>
                <TextInput
                  style={[styles.textInput, { flex: 1 }]}
                  value={birthDetails.place_of_birth}
                  onChangeText={(value) => handleInputChange('place_of_birth', value)}
                  placeholder={getText('நகரம், மாநிலம், நாடு', 'City, State, Country')}
                  placeholderTextColor="#95A5A6"
                />
                <TouchableOpacity
                  style={[styles.geocodeButton, geocoding && styles.geocodeButtonDisabled]}
                  onPress={() => geocodePlace(birthDetails.place_of_birth)}
                  disabled={geocoding || !birthDetails.place_of_birth.trim()}
                >
                  {geocoding ? (
                    <ActivityIndicator size="small" color="#FFFFFF" />
                  ) : (
                    <>
                      <Ionicons name="location" size={16} color="#FFFFFF" />
                      <Text style={styles.geocodeButtonText}>
                        {getText('கண்டறி', 'Find')}
                      </Text>
                    </>
                  )}
                </TouchableOpacity>
              </View>
            </View>
            
            {/* Latitude & Longitude (Auto-filled) */}
            <View style={styles.row}>
              <View style={[styles.inputGroup, styles.halfWidth]}>
                <Text style={styles.inputLabel}>
                  {getText('அட்சரேகை', 'Latitude')} *
                </Text>
                <TextInput
                  style={[styles.textInput, { backgroundColor: '#F8F9FA' }]}
                  value={birthDetails.latitude}
                  onChangeText={(value) => handleInputChange('latitude', value)}
                  placeholder="13.0827"
                  placeholderTextColor="#95A5A6"
                  keyboardType="numeric"
                  editable={true}
                />
              </View>
              
              <View style={[styles.inputGroup, styles.halfWidth]}>
                <Text style={styles.inputLabel}>
                  {getText('தீர்க்கரேகை', 'Longitude')} *
                </Text>
                <TextInput
                  style={[styles.textInput, { backgroundColor: '#F8F9FA' }]}
                  value={birthDetails.longitude}
                  onChangeText={(value) => handleInputChange('longitude', value)}
                  placeholder="80.2707"
                  placeholderTextColor="#95A5A6"
                  keyboardType="numeric"
                  editable={true}
                />
              </View>
            </View>
            
            {/* Timezone (Auto-detected) */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('நேர மண்டலம்', 'Timezone')}
              </Text>
              <TextInput
                style={[styles.textInput, { backgroundColor: '#F8F9FA' }]}
                value={birthDetails.timezone}
                onChangeText={(value) => handleInputChange('timezone', value)}
                placeholder="IST"
                placeholderTextColor="#95A5A6"
                editable={true}
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
                placeholder="0"
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
      
      {/* Date Picker Modal */}
      {showDatePicker && (
        <Modal transparent={true} animationType="slide">
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>
                  {getText('தேதி தேர்ந்தெடுக்கவум்', 'Select Date')}
                </Text>
                <TouchableOpacity onPress={() => setShowDatePicker(false)}>
                  <Ionicons name="close" size={24} color="#2C3E50" />
                </TouchableOpacity>
              </View>
              <View style={styles.pickerContainer}>
{Platform.OS === 'web' ? (
                  <>
                    <TextInput
                      style={styles.webDateInput}
                      value={birthDetails.date_of_birth}
                      onChangeText={(value) => {
                        handleInputChange('date_of_birth', value);
                        setSelectedDate(new Date(value));
                      }}
                      placeholder="YYYY-MM-DD"
                      placeholderTextColor="#95A5A6"
                    />
                    <Text style={styles.webDateHelper}>
                      {getText('வடிவம்: YYYY-MM-DD (உதா: 2000-01-15)', 'Format: YYYY-MM-DD (e.g., 2000-01-15)')}
                    </Text>
                  </>
                ) : (
                  <DateTimePicker
                    value={selectedDate}
                    mode="date"
                    display="default"
                    onChange={handleDateChange}
                    maximumDate={new Date()}
                  />
                )}
              </View>
              <View style={styles.modalActions}>
                <TouchableOpacity
                  style={[styles.modalButton, styles.cancelButton]}
                  onPress={() => setShowDatePicker(false)}
                >
                  <Text style={styles.cancelButtonText}>
                    {getText('रद्द करें', 'Cancel')}
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.modalButton, styles.confirmButton]}
                  onPress={() => setShowDatePicker(false)}
                >
                  <Text style={styles.confirmButtonText}>
                    {getText('ठीक है', 'Done')}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>
      )}
      
      {/* Time Picker Modal */}
      {showTimePicker && (
        <Modal transparent={true} animationType="slide">
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>
                  {getText('நேரம் தேர்ந்தெடுக்கவும்', 'Select Time')}
                </Text>
                <TouchableOpacity onPress={() => setShowTimePicker(false)}>
                  <Ionicons name="close" size={24} color="#2C3E50" />
                </TouchableOpacity>
              </View>
              <View style={styles.pickerContainer}>
{Platform.OS === 'web' ? (
                  <>
                    <TextInput
                      style={styles.webDateInput}
                      value={birthDetails.time_of_birth}
                      onChangeText={(value) => {
                        handleInputChange('time_of_birth', value);
                      }}
                      placeholder="HH:MM"
                      placeholderTextColor="#95A5A6"
                    />
                    <Text style={styles.webDateHelper}>
                      {getText('வடிவம்: HH:MM (உதா: 14:30)', 'Format: HH:MM (e.g., 14:30)')}
                    </Text>
                  </>
                ) : (
                  <DateTimePicker
                    value={selectedTime}
                    mode="time"
                    display="default"
                    onChange={handleTimeChange}
                  />
                )}
              </View>
              <View style={styles.modalActions}>
                <TouchableOpacity
                  style={[styles.modalButton, styles.cancelButton]}
                  onPress={() => setShowTimePicker(false)}
                >
                  <Text style={styles.cancelButtonText}>
                    {getText('रद्द करें', 'Cancel')}
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.modalButton, styles.confirmButton]}
                  onPress={() => setShowTimePicker(false)}
                >
                  <Text style={styles.confirmButtonText}>
                    {getText('ठीक है', 'Done')}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>
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
  placeInputContainer: {
    flexDirection: 'row',
    gap: 12,
    alignItems: 'flex-end',
  },
  geocodeButton: {
    backgroundColor: '#27AE60',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 80,
    minHeight: 48,
  },
  geocodeButtonDisabled: {
    opacity: 0.6,
  },
  geocodeButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 4,
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  halfWidth: {
    flex: 1,
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
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    width: '90%',
    maxWidth: 400,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2C3E50',
  },
  pickerContainer: {
    paddingVertical: 20,
    alignItems: 'center',
    minHeight: 200,
  },
  datePicker: {
    width: '100%',
    height: 200,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#E8E8E8',
    gap: 12,
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
  },
  cancelButton: {
    backgroundColor: '#95A5A6',
  },
  confirmButton: {
    backgroundColor: '#4A90E2',
  },
  cancelButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  pickerContainer: {
    paddingVertical: 20,
    alignItems: 'center',
  },
  datePicker: {
    width: '100%',
    height: 200,
  },
  webDateInput: {
    borderWidth: 1,
    borderColor: '#E8E8E8',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#2C3E50',
    backgroundColor: '#FFFFFF',
    marginBottom: 8,
    textAlign: 'center',
  },
  webDateHelper: {
    fontSize: 12,
    color: '#7F8C8D',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#E8E8E8',
    gap: 12,
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
  },
  cancelButton: {
    backgroundColor: '#95A5A6',
  },
  confirmButton: {
    backgroundColor: '#4A90E2',
  },
  cancelButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
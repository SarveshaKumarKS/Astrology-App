import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  StatusBar,
  TextInput,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  useWindowDimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { ApiError, fetchJson, isAbortError } from '../lib/api';
import ScreenHeader from '../components/ScreenHeader';
import { colors, spacing, radius, font, shadow } from '../lib/theme';
import { useLanguage } from '../lib/language';
import NativeDateTimePicker from '../components/NativeDateTimePicker';

interface BirthDetails {
  name: string;
  mother_name?: string;
  father_name?: string;
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
  const { width } = useWindowDimensions();
  const { language, toggleLanguage, getText } = useLanguage();
  const [system, setSystem] = useState<'vakkiam' | 'thirukkanitham'>('vakkiam');
  const [loading, setLoading] = useState(false);
  const [geocoding, setGeocoding] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedTime, setSelectedTime] = useState(() => {
    const noon = new Date();
    noon.setHours(12, 0, 0, 0);
    return noon;
  });
  const isCompact = width < 360;
  
  const [birthDetails, setBirthDetails] = useState<BirthDetails>({
    name: '',
    mother_name: '',
    father_name: '',
    date_of_birth: new Date().toISOString().split('T')[0],
    time_of_birth: '12:00',
    place_of_birth: '',
    latitude: '',
    longitude: '',
    timezone: 'IST',
    time_correction: '0',
  });

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

  const handleDateChange = (currentDate: Date) => {
    setShowDatePicker(false);
    setSelectedDate(currentDate);
    
    // Format date without timezone conversion to avoid date shifting
    const year = currentDate.getFullYear();
    const month = (currentDate.getMonth() + 1).toString().padStart(2, '0');
    const day = currentDate.getDate().toString().padStart(2, '0');
    const dateString = `${year}-${month}-${day}`;
    
    handleInputChange('date_of_birth', dateString);
  };

  const handleTimeChange = (currentTime: Date) => {
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
      const result = await fetchJson<any>('/api/horoscope', {
        method: 'POST',
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
      // Navigate to results page with horoscope data
      router.push({
        pathname: '/horoscope-result',
        params: {
          data: JSON.stringify(result),
        },
      });
    } catch (error) {
      console.error('Error generating horoscope:', error);
      Alert.alert(
        getText('பிழை', 'Error'),
        error instanceof ApiError
          ? getText(
              error.detail || 'சேவையக பிழை ஏற்பட்டது',
              error.detail || 'Server error'
            )
          : isAbortError(error)
            ? getText('நேரம் முடிந்தது. மீண்டும் முயற்சிக்கவும்.', 'Request timed out. Please try again.')
            : getText(
                'இணைய இணைப்பு/சேவையக பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.',
                'Network/server error. Please try again.'
              )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.bg} />
      
      {/* Header */}
      <ScreenHeader
        title={getText('ஜாதகம் கணித்தல்', 'Generate Horoscope')}
        onBack={() => router.back()}
        right={
          <TouchableOpacity
            testID="horoscope-language-button"
            style={styles.langPill}
            onPress={toggleLanguage}
          >
            <Text style={styles.langPillText}>{language === 'tamil' ? 'த' : 'EN'}</Text>
          </TouchableOpacity>
        }
      />

      <KeyboardAvoidingView 
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          testID="horoscope-form-scroll"
          style={styles.content}
          contentContainerStyle={[
            styles.contentContainer,
            { paddingHorizontal: isCompact ? spacing.md : spacing.lg },
          ]}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* System Selection */}
          <View testID="system-selection-section" style={styles.systemSection}>
            <Text testID="system-selection-title" style={styles.sectionTitle}>
              {getText('அமைப்பு தேர்வு', 'System Selection')}
            </Text>
            
            <View style={styles.systemButtons}>
              <TouchableOpacity
                testID="select-vakkiam-button"
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
                testID="select-thirukkanitham-button"
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
              
              <TouchableOpacity
                testID="nkv-system-disabled-button"
                style={[
                  styles.systemButton,
                  styles.systemButtonDisabled
                ]}
                disabled={true}
              >
                <Text style={[
                  styles.systemButtonText,
                  styles.systemButtonTextDisabled
                ]}>
                  {getText('NKV அமைப்பு', 'NKV System')}
                </Text>
                <Text style={styles.comingSoonText}>
                  {getText('விரைவில்', 'Coming Soon')}
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Birth Details Form */}
          <View testID="birth-details-section" style={styles.formSection}>
            <Text testID="birth-details-title" style={styles.sectionTitle}>
              {getText('பிறப்பு விவரங்கள்', 'Birth Details')}
            </Text>
            
            {/* Name */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('பெயர்', 'Name')} *
              </Text>
              <TextInput
                testID="birth-name-input"
                style={styles.textInput}
                value={birthDetails.name}
                onChangeText={(value) => handleInputChange('name', value)}
                placeholder={getText('உங்கள் பெயரை உள்ளிடவும்', 'Enter your name')}
                placeholderTextColor="#95A5A6"
              />
            </View>
            
            {/* Mother's Name */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('தாய் பெயர்', "Mother's Name")}
              </Text>
              <TextInput
                testID="mother-name-input"
                style={styles.textInput}
                value={birthDetails.mother_name}
                onChangeText={(value) => handleInputChange('mother_name', value)}
                placeholder={getText('தாய் பெயரை உள்ளிடவும்', "Enter mother's name")}
                placeholderTextColor="#95A5A6"
              />
            </View>
            
            {/* Father's Name */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('தந்தை பெயர்', "Father's Name")}
              </Text>
              <TextInput
                testID="father-name-input"
                style={styles.textInput}
                value={birthDetails.father_name}
                onChangeText={(value) => handleInputChange('father_name', value)}
                placeholder={getText('தந்தை பெயரை உள்ளிடவும்', "Enter father's name")}
                placeholderTextColor="#95A5A6"
              />
            </View>
            
            {/* Birth Date */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {getText('பிறந்த தேதி', 'Date of Birth')} *
              </Text>
              <TouchableOpacity
                testID="birth-date-button"
                style={styles.dateTimeButton}
                onPress={() => setShowDatePicker(true)}
              >
                <Text style={styles.dateTimeText}>
                  {birthDetails.date_of_birth ? 
                    (() => {
                      const [year, month, day] = birthDetails.date_of_birth.split('-');
                      return `${day}/${month}/${year}`;
                    })() 
                    : getText('தேதி தேர்ந்தெடுக்கவும்', 'Select Date')
                  }
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
                testID="birth-time-button"
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
                  testID="birth-place-input"
                  style={[styles.textInput, styles.placeInput]}
                  value={birthDetails.place_of_birth}
                  onChangeText={(value) => handleInputChange('place_of_birth', value)}
                  placeholder={getText('நகரம், மாநிலம், நாடு', 'City, State, Country')}
                  placeholderTextColor="#95A5A6"
                />
                <TouchableOpacity
                  testID="find-location-button"
                  accessibilityLabel={getText('இடம் கண்டறி', 'Find location')}
                  style={[styles.geocodeButton, geocoding && styles.geocodeButtonDisabled]}
                  onPress={() => geocodePlace(birthDetails.place_of_birth)}
                  disabled={geocoding || !birthDetails.place_of_birth.trim()}
                >
                  {geocoding ? (
                    <ActivityIndicator size="small" color="#FFFFFF" />
                  ) : (
                    <Ionicons name="location-outline" size={22} color={colors.onBrand} />
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
                  testID="latitude-input"
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
                  testID="longitude-input"
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
                testID="timezone-input"
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
                testID="time-correction-input"
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
        <SafeAreaView edges={['bottom']} style={styles.buttonContainer}>
          <TouchableOpacity
            testID="generate-horoscope-button"
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
        </SafeAreaView>
      </KeyboardAvoidingView>
      
      <NativeDateTimePicker
        visible={showDatePicker}
        mode="date"
        value={selectedDate}
        title={getText('பிறந்த தேதியைத் தேர்ந்தெடுக்கவும்', 'Select date of birth')}
        cancelLabel={getText('ரத்து', 'Cancel')}
        confirmLabel={getText('சரி', 'Done')}
        testID="birth-date-picker"
        maximumDate={new Date()}
        onCancel={() => setShowDatePicker(false)}
        onConfirm={handleDateChange}
      />

      <NativeDateTimePicker
        visible={showTimePicker}
        mode="time"
        value={selectedTime}
        title={getText('பிறந்த நேரத்தைத் தேர்ந்தெடுக்கவும்', 'Select time of birth')}
        cancelLabel={getText('ரத்து', 'Cancel')}
        confirmLabel={getText('சரி', 'Done')}
        testID="birth-time-picker"
        onCancel={() => setShowTimePicker(false)}
        onConfirm={handleTimeChange}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  keyboardView: {
    flex: 1,
  },
  langPill: {
    backgroundColor: colors.brandSoft,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    minWidth: 44,
    minHeight: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },
  langPillText: {
    color: colors.brandStrong,
    fontSize: 13,
    fontWeight: '700',
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    paddingBottom: spacing.lg,
  },
  systemSection: {
    backgroundColor: colors.card,
    padding: spacing.lg,
    borderRadius: radius.lg,
    marginTop: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadow.soft,
  },
  sectionTitle: {
    fontSize: font.xl,
    lineHeight: 30,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.md,
  },
  systemButtons: {
    gap: spacing.sm,
  },
  systemButton: {
    width: '100%',
    minHeight: 56,
    borderWidth: 1,
    borderColor: colors.borderStrong,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    alignItems: 'center',
    justifyContent: 'center',
  },
  systemButtonActive: {
    borderColor: colors.brand,
    backgroundColor: colors.brandSoft,
  },
  systemButtonText: {
    fontSize: font.base,
    lineHeight: 22,
    fontWeight: '700',
    color: colors.text,
    textAlign: 'center',
  },
  systemButtonTextActive: {
    color: colors.brandStrong,
  },
  systemButtonDisabled: {
    borderColor: colors.border,
    backgroundColor: colors.surfaceTertiary,
    opacity: 0.7,
  },
  systemButtonTextDisabled: {
    color: colors.textMuted,
  },
  comingSoonText: {
    fontSize: 10,
    fontWeight: '500',
    color: colors.brandStrong,
    marginTop: 4,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  formSection: {
    backgroundColor: colors.card,
    padding: spacing.lg,
    borderRadius: radius.lg,
    marginTop: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadow.soft,
  },
  inputGroup: {
    minWidth: 0,
    marginBottom: spacing.lg,
  },
  inputLabel: {
    fontSize: font.base,
    lineHeight: 22,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  textInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    fontSize: font.lg,
    color: colors.text,
    backgroundColor: colors.card,
    minHeight: 52,
  },
  dateTimeButton: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    backgroundColor: colors.card,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    minHeight: 52,
  },
  dateTimeText: {
    flexShrink: 1,
    fontSize: font.lg,
    color: colors.text,
  },
  placeInputContainer: {
    flexDirection: 'row',
    gap: spacing.sm,
    alignItems: 'center',
    width: '100%',
  },
  placeInput: { flex: 1, minWidth: 0 },
  geocodeButton: {
    flexShrink: 0,
    width: 52,
    height: 52,
    backgroundColor: colors.brand,
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  geocodeButtonDisabled: {
    opacity: 0.6,
  },
  row: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  halfWidth: {
    flex: 1,
    minWidth: 0,
  },
  buttonContainer: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
    backgroundColor: colors.card,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  generateButton: {
    backgroundColor: colors.brand,
    paddingVertical: spacing.md,
    borderRadius: radius.pill,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 56,
  },
  generateButtonDisabled: {
    opacity: 0.6,
  },
  generateButtonText: {
    color: colors.onBrand,
    fontSize: font.lg,
    lineHeight: 24,
    fontWeight: '700',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.lg,
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
    fontSize: font.xl,
    fontWeight: '700',
    color: colors.text,
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
    borderTopColor: colors.border,
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
    backgroundColor: colors.surfaceTertiary,
  },
  confirmButton: {
    backgroundColor: colors.brand,
  },
  cancelButtonText: {
    color: colors.textSecondary,
    fontSize: 16,
    fontWeight: '600',
  },
  confirmButtonText: {
    color: colors.onBrand,
    fontSize: 16,
    fontWeight: '600',
  },
  webDateInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: colors.text,
    backgroundColor: colors.card,
    marginBottom: 8,
    textAlign: 'center',
  },
  webDateHelper: {
    fontSize: 12,
    color: colors.textMuted,
    textAlign: 'center',
    fontStyle: 'italic',
  },
});
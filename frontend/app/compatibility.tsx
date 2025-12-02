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

export default function CompatibilityPage() {
  const [language, setLanguage] = useState<'tamil' | 'english'>('tamil');
  const [system, setSystem] = useState<'vakkiam' | 'thirukkanitham'>('vakkiam');
  const [loading, setLoading] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState<{show: boolean, person: 'male' | 'female'}>({show: false, person: 'male'});
  const [showTimePicker, setShowTimePicker] = useState<{show: boolean, person: 'male' | 'female'}>({show: false, person: 'male'});
  const [geocoding, setGeocoding] = useState(false);
  
  const [maleDetails, setMaleDetails] = useState<BirthDetails>({
    name: '',
    date_of_birth: new Date().toISOString().split('T')[0],
    time_of_birth: '12:00',
    place_of_birth: '',
    latitude: '',
    longitude: '',
    timezone: 'IST',
    time_correction: '0',
  });

  const [femaleDetails, setFemaleDetails] = useState<BirthDetails>({
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

  const handleInputChange = (person: 'male' | 'female', field: keyof BirthDetails, value: string) => {
    if (person === 'male') {
      setMaleDetails(prev => ({ ...prev, [field]: value }));
    } else {
      setFemaleDetails(prev => ({ ...prev, [field]: value }));
    }
  };

  const handleDateChange = (event: any, selectedDate?: Date) => {
    const person = showDatePicker.person;
    setShowDatePicker({show: false, person: 'male'});
    if (selectedDate) {
      // Format date without timezone conversion to avoid date shifting
      const year = selectedDate.getFullYear();
      const month = (selectedDate.getMonth() + 1).toString().padStart(2, '0');
      const day = selectedDate.getDate().toString().padStart(2, '0');
      const dateString = `${year}-${month}-${day}`;
      
      handleInputChange(person, 'date_of_birth', dateString);
    }
  };

  const handleTimeChange = (event: any, selectedTime?: Date) => {
    setShowTimePicker({show: false, person: 'male'});
    if (selectedTime) {
      const hours = selectedTime.getHours().toString().padStart(2, '0');
      const minutes = selectedTime.getMinutes().toString().padStart(2, '0');
      handleInputChange(showTimePicker.person, 'time_of_birth', `${hours}:${minutes}`);
    }
  };

  const validateForm = (): boolean => {
    const details = [
      { data: maleDetails, name: getText('ஆண்', 'Male') },
      { data: femaleDetails, name: getText('பெண்', 'Female') }
    ];

    for (const person of details) {
      if (!person.data.name.trim()) {
        Alert.alert(
          getText('பெயர் தேவை', 'Name Required'),
          getText(`${person.name} பெயரை உள்ளிடவும்`, `Please enter ${person.name} name`)
        );
        return false;
      }
      
      if (!person.data.place_of_birth.trim() || !person.data.latitude.trim() || !person.data.longitude.trim()) {
        Alert.alert(
          getText('முழுமையான விவரங்கள் தேவை', 'Complete Details Required'),
          getText(`${person.name} பிறப்பு விவரங்களை முழுமையாக உள்ளிடவும்`, `Please enter complete birth details for ${person.name}`)
        );
        return false;
      }
    }
    
    return true;
  };

  const checkCompatibility = async () => {
    if (!validateForm()) return;
    
    setLoading(true);
    
    try {
      const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/compatibility`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          male_details: {
            name: maleDetails.name,
            date_of_birth: maleDetails.date_of_birth,
            time_of_birth: maleDetails.time_of_birth + ':00',
            place_of_birth: maleDetails.place_of_birth,
            latitude: parseFloat(maleDetails.latitude),
            longitude: parseFloat(maleDetails.longitude),
            timezone: maleDetails.timezone,
            time_correction: parseInt(maleDetails.time_correction) || 0,
          },
          female_details: {
            name: femaleDetails.name,
            date_of_birth: femaleDetails.date_of_birth,
            time_of_birth: femaleDetails.time_of_birth + ':00',
            place_of_birth: femaleDetails.place_of_birth,
            latitude: parseFloat(femaleDetails.latitude),
            longitude: parseFloat(femaleDetails.longitude),
            timezone: femaleDetails.timezone,
            time_correction: parseInt(femaleDetails.time_correction) || 0,
          },
          system: system,
          language: language,
        }),
      });

      const result = await response.json();
      
      if (response.ok) {
        Alert.alert(
          getText('வெற்றி', 'Success'),
          getText(`பொருத்தம் ${result.percentage.toFixed(1)}% - ${result.overall_rating_tamil || result.overall_rating}`, 
                 `Compatibility ${result.percentage.toFixed(1)}% - ${result.overall_rating}`),
          [
            {
              text: getText('சரி', 'OK'),
              onPress: () => {
                console.log('Compatibility result:', result);
              }
            }
          ]
        );
      } else {
        throw new Error(result.detail || 'Failed to check compatibility');
      }
    } catch (error) {
      console.error('Error checking compatibility:', error);
      Alert.alert(
        getText('பிழை', 'Error'),
        getText('பொருத்தம் சரிபார்க்கும்போது பிழை ஏற்பட்டது', 'Error occurred while checking compatibility')
      );
    } finally {
      setLoading(false);
    }
  };

  const renderPersonForm = (person: 'male' | 'female', details: BirthDetails, title: string) => (
    <View style={styles.formSection}>
      <Text style={styles.sectionTitle}>{title}</Text>
      
      {/* Name */}
      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>
          {getText('பெயர்', 'Name')} *
        </Text>
        <TextInput
          style={styles.textInput}
          value={details.name}
          onChangeText={(value) => handleInputChange(person, 'name', value)}
          placeholder={getText('பெயரை உள்ளிடவும்', 'Enter name')}
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
          onPress={() => setShowDatePicker({show: true, person})}
        >
          <Text style={styles.dateTimeText}>
            {new Date(details.date_of_birth).toLocaleDateString()}
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
          onPress={() => setShowTimePicker({show: true, person})}
        >
          <Text style={styles.dateTimeText}>
            {details.time_of_birth}
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
          value={details.place_of_birth}
          onChangeText={(value) => handleInputChange(person, 'place_of_birth', value)}
          placeholder={getText('நகரம், மாநிலம், நாடு', 'City, State, Country')}
          placeholderTextColor="#95A5A6"
        />
      </View>
      
      {/* Latitude & Longitude */}
      <View style={styles.row}>
        <View style={[styles.inputGroup, styles.halfWidth]}>
          <Text style={styles.inputLabel}>
            {getText('அட்சரேகை', 'Latitude')} *
          </Text>
          <TextInput
            style={styles.textInput}
            value={details.latitude}
            onChangeText={(value) => handleInputChange(person, 'latitude', value)}
            placeholder="13.0827"
            placeholderTextColor="#95A5A6"
            keyboardType="numeric"
          />
        </View>
        
        <View style={[styles.inputGroup, styles.halfWidth]}>
          <Text style={styles.inputLabel}>
            {getText('தீர்க்கரேகை', 'Longitude')} *
          </Text>
          <TextInput
            style={styles.textInput}
            value={details.longitude}
            onChangeText={(value) => handleInputChange(person, 'longitude', value)}
            placeholder="80.2707"
            placeholderTextColor="#95A5A6"
            keyboardType="numeric"
          />
        </View>
      </View>
    </View>
  );

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
            {getText('திருமணப் பொருத்தம்', 'Marriage Compatibility')}
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

          {/* Forms */}
          {renderPersonForm('male', maleDetails, getText('ஆண் விவரங்கள்', 'Male Details'))}
          {renderPersonForm('female', femaleDetails, getText('பெண் விவரங்கள்', 'Female Details'))}
        </ScrollView>
        
        {/* Check Button */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.checkButton, loading && styles.checkButtonDisabled]}
            onPress={checkCompatibility}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#FFFFFF" size="small" />
            ) : (
              <Text style={styles.checkButtonText}>
                {getText('பொருத்தம் பார்க்க', 'Check Compatibility')}
              </Text>
            )}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
      
      {/* Date Picker */}
      {showDatePicker.show && (
        <DateTimePicker
          value={new Date(showDatePicker.person === 'male' ? maleDetails.date_of_birth : femaleDetails.date_of_birth)}
          mode="date"
          display="default"
          onChange={handleDateChange}
          maximumDate={new Date()}
        />
      )}
      
      {/* Time Picker */}
      {showTimePicker.show && (
        <DateTimePicker
          value={new Date(`2000-01-01T${showTimePicker.person === 'male' ? maleDetails.time_of_birth : femaleDetails.time_of_birth}:00`)}
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
    borderColor: '#E74C3C',
    backgroundColor: '#FFF5F5',
  },
  systemButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#34495E',
    textAlign: 'center',
  },
  systemButtonTextActive: {
    color: '#E74C3C',
  },
  formSection: {
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
  inputGroup: {
    marginBottom: 16,
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
  checkButton: {
    backgroundColor: '#E74C3C',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 56,
  },
  checkButtonDisabled: {
    opacity: 0.6,
  },
  checkButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
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
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import DateTimePicker from '@react-native-community/datetimepicker';
import { router } from 'expo-router';
import { ApiError, fetchJson, isAbortError } from '../lib/api';
import ScreenHeader from '../components/ScreenHeader';
import { colors, shadow } from '../lib/theme';

interface PanchangamData {
  date: string;
  tithi: string;
  tithi_tamil: string;
  nakshatra: string;
  nakshatra_tamil: string;
  yoga: string;
  yoga_tamil: string;
  karana: string;
  karana_tamil: string;
  sunrise: string;
  sunset: string;
  moonrise: string;
  moonset: string;
  rahu_kalam: {
    start: string;
    end: string;
  };
  yama_gandam: {
    start: string;
    end: string;
  };
  gulika_kalam: {
    start: string;
    end: string;
  };
  abhijit_muhurta: {
    start: string;
    end: string;
  };
  auspicious_times: Array<{
    name: string;
    tamil: string;
    description: string;
  }>;
  inauspicious_times: Array<{
    name: string;
    tamil: string;
    description: string;
  }>;
}

export default function PanchangamPage() {
  const [language, setLanguage] = useState<'tamil' | 'english'>('tamil');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [panchangamData, setPanchangamData] = useState<PanchangamData | null>(null);

  const getText = (tamil: string, english: string) => {
    return language === 'tamil' ? tamil : english;
  };

  const loadPanchangam = async (date: Date = selectedDate) => {
    try {
      const dateString = date.toISOString().split('T')[0];
      const data = await fetchJson<PanchangamData>(`/api/panchangam/${dateString}?language=${language}`, {
        method: 'GET',
      });
      setPanchangamData(data);
    } catch (error) {
      console.error('Error loading panchangam:', error);
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
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadPanchangam();
  }, [selectedDate, language]);

  const onRefresh = () => {
    setRefreshing(true);
    loadPanchangam();
  };

  const handleDateChange = (event: any, date?: Date) => {
    setShowDatePicker(false);
    if (date) {
      setSelectedDate(date);
    }
  };

  const formatTime = (timeString: string) => {
    try {
      const time = new Date(`1970-01-01T${timeString}`);
      return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return timeString;
    }
  };

  const renderInfoCard = (title: string, titleTamil: string, value: string, valueTamil: string, icon: string, color: string) => (
    <View style={[styles.infoCard, { borderLeftColor: color }]}>
      <View style={styles.infoHeader}>
        <Ionicons name={icon as any} size={24} color={color} />
        <Text style={styles.infoTitle}>
          {getText(titleTamil, title)}
        </Text>
      </View>
      <Text style={styles.infoValue}>
        {getText(valueTamil, value)}
      </Text>
    </View>
  );

  const renderTimeCard = (title: string, titleTamil: string, startTime: string, endTime: string, icon: string, color: string, isAuspicious: boolean = true) => (
    <View style={[styles.timeCard, { backgroundColor: isAuspicious ? '#F0FFF0' : '#FFF0F0' }]}>
      <View style={styles.timeHeader}>
        <Ionicons name={icon as any} size={20} color={color} />
        <Text style={[styles.timeTitle, { color }]}>
          {getText(titleTamil, title)}
        </Text>
      </View>
      <Text style={styles.timeValue}>
        {formatTime(startTime)} - {formatTime(endTime)}
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.bg} />
      
      {/* Header */}
      <ScreenHeader
        title={getText('தினசரி பஞ்சாங்கம்', 'Daily Panchangam')}
        onBack={() => router.back()}
        right={
          <TouchableOpacity
            style={styles.langPill}
            onPress={() => setLanguage(language === 'tamil' ? 'english' : 'tamil')}
          >
            <Text style={styles.langPillText}>{language === 'tamil' ? 'த' : 'EN'}</Text>
          </TouchableOpacity>
        }
      />

      {/* Date Selection */}
      <View style={styles.dateSection}>
        <TouchableOpacity
          style={styles.dateSelector}
          onPress={() => setShowDatePicker(true)}
        >
          <Ionicons name="calendar-outline" size={24} color="#4A90E2" />
          <Text style={styles.dateText}>
            {selectedDate.toLocaleDateString('en-GB', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </Text>
          <Ionicons name="chevron-down" size={20} color="#7F8C8D" />
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#F39C12" />
          <Text style={styles.loadingText}>
            {getText('பஞ்சாங்கம் ஏற்றுகிறது...', 'Loading Panchangam...')}
          </Text>
        </View>
      ) : panchangamData ? (
        <ScrollView
          style={styles.content}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        >
          {/* Basic Information */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              {getText('அடிப்படை விவரங்கள்', 'Basic Information')}
            </Text>
            
            <View style={styles.infoGrid}>
              {renderInfoCard('Tithi', 'திதி', panchangamData.tithi, panchangamData.tithi_tamil, 'moon-outline', '#3498DB')}
              {renderInfoCard('Nakshatra', 'நட்சத்திரம்', panchangamData.nakshatra, panchangamData.nakshatra_tamil, 'star-outline', '#E74C3C')}
              {renderInfoCard('Yoga', 'யோகம்', panchangamData.yoga, panchangamData.yoga_tamil, 'fitness-outline', '#27AE60')}
              {renderInfoCard('Karana', 'கரணம்', panchangamData.karana, panchangamData.karana_tamil, 'triangle-outline', '#F39C12')}
            </View>
          </View>

          {/* Sun and Moon Times */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              {getText('சூரிய சந்திர காலங்கள்', 'Sun & Moon Times')}
            </Text>
            
            <View style={styles.timeGrid}>
              <View style={styles.timeCard}>
                <View style={styles.timeHeader}>
                  <Ionicons name="sunny" size={20} color="#F39C12" />
                  <Text style={[styles.timeTitle, { color: '#F39C12' }]}>
                    {getText('சூரிய உதயம்', 'Sunrise')}
                  </Text>
                </View>
                <Text style={styles.timeValue}>{formatTime(panchangamData.sunrise)}</Text>
              </View>
              
              <View style={styles.timeCard}>
                <View style={styles.timeHeader}>
                  <Ionicons name="moon" size={20} color="#3498DB" />
                  <Text style={[styles.timeTitle, { color: '#3498DB' }]}>
                    {getText('சந்திர உதயம்', 'Moonrise')}
                  </Text>
                </View>
                <Text style={styles.timeValue}>{formatTime(panchangamData.moonrise)}</Text>
              </View>
              
              <View style={styles.timeCard}>
                <View style={styles.timeHeader}>
                  <Ionicons name="sunny" size={20} color="#E67E22" />
                  <Text style={[styles.timeTitle, { color: '#E67E22' }]}>
                    {getText('சூரிய அஸ்தமனம்', 'Sunset')}
                  </Text>
                </View>
                <Text style={styles.timeValue}>{formatTime(panchangamData.sunset)}</Text>
              </View>
              
              <View style={styles.timeCard}>
                <View style={styles.timeHeader}>
                  <Ionicons name="moon" size={20} color="#8E44AD" />
                  <Text style={[styles.timeTitle, { color: '#8E44AD' }]}>
                    {getText('சந்திர அஸ்தமனம்', 'Moonset')}
                  </Text>
                </View>
                <Text style={styles.timeValue}>{formatTime(panchangamData.moonset)}</Text>
              </View>
            </View>
          </View>

          {/* Auspicious Time */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              {getText('நல்ல நேரம்', 'Auspicious Time')}
            </Text>
            
            {renderTimeCard(
              'Abhijit Muhurta',
              'அபிஜித் முகூர்த்தம்',
              panchangamData.abhijit_muhurta.start,
              panchangamData.abhijit_muhurta.end,
              'star',
              '#27AE60',
              true
            )}
          </View>

          {/* Inauspicious Times */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              {getText('தவிர்க்க வேண்டிய நேரங்கள்', 'Inauspicious Times')}
            </Text>
            
            <View style={styles.inauspiciousGrid}>
              {renderTimeCard(
                'Rahu Kalam',
                'ராகு காலம்',
                panchangamData.rahu_kalam.start,
                panchangamData.rahu_kalam.end,
                'warning',
                '#E74C3C',
                false
              )}
              
              {renderTimeCard(
                'Yama Gandam',
                'யம கண்டம்',
                panchangamData.yama_gandam.start,
                panchangamData.yama_gandam.end,
                'skull',
                '#8E44AD',
                false
              )}
              
              {renderTimeCard(
                'Gulika Kalam',
                'குளிக காலம்',
                panchangamData.gulika_kalam.start,
                panchangamData.gulika_kalam.end,
                'close-circle',
                '#E67E22',
                false
              )}
            </View>
          </View>

          {/* Note */}
          <View style={styles.noteSection}>
            <View style={styles.noteCard}>
              <Ionicons name="information-circle-outline" size={24} color="#3498DB" />
              <Text style={styles.noteText}>
                {getText(
                  'இந்த பஞ்சாங்க விவரங்கள் திருக்கணித முறையில் கணிக்கப்பட்டது. முக்கிய முடிவுகளுக்கு ஜோதிடரை அணுகவும்.',
                  'These Panchangam details are calculated using Thirukkanitham method. Consult an astrologer for important decisions.'
                )}
              </Text>
            </View>
          </View>
        </ScrollView>
      ) : (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={64} color="#E74C3C" />
          <Text style={styles.errorTitle}>
            {getText('பஞ்சாங்கம் கிடைக்கவில்லை', 'Panchangam Not Available')}
          </Text>
          <Text style={styles.errorDescription}>
            {getText('தேர்ந்தெடுத்த தேதிக்கு பஞ்சாங்கம் கிடைக்கவில்லை', 'Panchangam not available for selected date')}
          </Text>
        </View>
      )}

      {/* Date Picker */}
      {showDatePicker && (
        <DateTimePicker
          value={selectedDate}
          mode="date"
          display="default"
          onChange={handleDateChange}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
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
  dateSection: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E8E8E8',
  },
  dateSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E8E8E8',
  },
  dateText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginLeft: 12,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#7F8C8D',
    marginTop: 16,
  },
  section: {
    marginTop: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 16,
  },
  infoGrid: {
    gap: 12,
  },
  infoCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    ...shadow.soft,
  },
  infoHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  infoTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#7F8C8D',
    marginLeft: 12,
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
  },
  timeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  timeCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    flex: 1,
    minWidth: '45%',
    ...shadow.soft,
  },
  timeHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  timeTitle: {
    fontSize: 13,
    fontWeight: '600',
    marginLeft: 8,
  },
  timeValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
  },
  inauspiciousGrid: {
    gap: 12,
  },
  noteSection: {
    marginTop: 24,
    marginBottom: 32,
  },
  noteCard: {
    backgroundColor: '#E8F4FD',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  noteText: {
    flex: 1,
    fontSize: 14,
    color: '#2980B9',
    lineHeight: 20,
    marginLeft: 12,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 80,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#E74C3C',
    marginTop: 16,
    marginBottom: 8,
  },
  errorDescription: {
    fontSize: 14,
    color: '#7F8C8D',
    textAlign: 'center',
    paddingHorizontal: 32,
    lineHeight: 20,
  },
});

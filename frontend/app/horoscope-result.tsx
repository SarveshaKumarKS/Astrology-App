import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  StatusBar,
  ActivityIndicator,
  Alert,
  Platform,
  useWindowDimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { router, useLocalSearchParams } from 'expo-router';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import SouthIndianChart from '../components/SouthIndianChart';
import CorrectableField from '../components/CorrectableField';
import { fetchApi, fetchJson, isAbortError, ApiError } from '../lib/api';
import { useAuth } from '../lib/auth';
import ScreenHeader from '../components/ScreenHeader';
import { CorrectionControls } from '../lib/debug';
import { colors, radius, font } from '../lib/theme';

interface PlanetaryPosition {
  planet: string;
  planet_tamil: string;
  longitude: number;
  sign: number;
  sign_name: string;
  sign_name_tamil: string;
  nakshatra: number;
  nakshatra_name: string;
  nakshatra_name_tamil: string;
  house: number;
  retrograde: boolean;
  longitude_dms?: string;
  longitude_in_sign?: number;
  longitude_in_sign_dms?: string;
  nakshatra_pada?: number;
  nakshatra_lord?: string;
  nakshatra_lord_tamil?: string;
}

interface Chart {
  chart_type: string;
  houses: { [key: string]: string[] };
  houses_tamil: { [key: string]: string[] };
  ascendant_house: number;
}

interface DasaPeriod {
  planet: string;
  planet_tamil: string;
  start_date: string;
  end_date: string;
  level: string;
  years: number;
  months: number;
  days: number;
  // Extended fields
  balance_years?: number;
  balance_months?: number;
  balance_days?: number;
  next_dasa_planet?: string;
  next_dasa_planet_tamil?: string;
  next_dasa_end_date?: string;
  current_bhukti_planet?: string;
  current_bhukti_planet_tamil?: string;
  current_bhukti_end_date?: string;
  next_bhukti_planet?: string;
  next_bhukti_planet_tamil?: string;
  next_bhukti_end_date?: string;
  first_dasha_planet?: string;
  first_dasha_planet_tamil?: string;
}

interface HoroscopeData {
  birth_details: {
    name: string;
    date_of_birth: string;
    time_of_birth: string;
    place_of_birth: string;
    latitude?: number;
    longitude?: number;
    timezone?: string;
    time_correction?: number;
  };
  system: string;
  language: string;
  ascendant: string;
  ascendant_tamil: string;
  moon_sign: string;
  moon_sign_tamil: string;
  nakshatra: string;
  nakshatra_tamil: string;
  planetary_positions: PlanetaryPosition[];
  rasi_chart: Chart;
  navamsa_chart: Chart;
  karu_udayam_rasi_chart?: Chart;
  karu_udayam_date_of_birth?: string;
  karu_udayam_time_of_birth?: string;
  karu_udayam_tamil_month?: string;
  karu_udayam_tamil_day?: number;
  karu_udayam_approx_diff_days?: number;
  dasa_periods: DasaPeriod[];
  current_dasa: DasaPeriod;
  // Extended fields
  retrograde_planets?: string[];
  retrograde_planets_tamil?: string[];
  bhava_maruthal?: { [key: string]: number };
  bhava_maruthal_tamil?: { [key: string]: number };
}

export default function HoroscopeResultPage() {
  const { width } = useWindowDimensions();
  const { user, login } = useAuth();
  const [language, setLanguage] = useState<'tamil' | 'english'>('tamil');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [horoscopeData, setHoroscopeData] = useState<HoroscopeData | null>(null);
  const params = useLocalSearchParams();
  const isCompact = width < 360;
  const chartSize = Math.max(236, Math.min(360, width - (isCompact ? 56 : 64)));

  useEffect(() => {
    if (params.data) {
      try {
        const data = JSON.parse(params.data as string);
        setHoroscopeData(data);
        setLanguage(data.language || 'tamil');
      } catch (error) {
        console.error('Error parsing horoscope data:', error);
        Alert.alert('Error', 'Failed to load horoscope data');
      }
    }
  }, [params.data]);

  const getText = (tamil: string, english: string) => {
    return language === 'tamil' ? tamil : english;
  };

  const saveProfile = async () => {
    if (!horoscopeData) return;

    if (!user) {
      Alert.alert(
        getText('உள்நுழையவும்', 'Sign In Required'),
        getText(
          'ஜாதகத்தை சேமிக்க Google மூலம் உள்நுழையவும்.',
          'Sign in with Google to save this horoscope.'
        ),
        [
          { text: getText('ரத்து செய்', 'Cancel'), style: 'cancel' },
          { text: getText('உள்நுழைக', 'Sign In'), onPress: () => login() },
        ]
      );
      return;
    }

    const bd = horoscopeData.birth_details;
    setSaving(true);
    try {
      await fetchJson('/api/profiles', {
        method: 'POST',
        body: JSON.stringify({
          name: bd.name,
          birth_details: {
            name: bd.name,
            date_of_birth: bd.date_of_birth,
            time_of_birth: bd.time_of_birth,
            place_of_birth: bd.place_of_birth,
            latitude: bd.latitude ?? 0,
            longitude: bd.longitude ?? 0,
            timezone: bd.timezone ?? 'Asia/Kolkata',
            time_correction: bd.time_correction ?? 0,
          },
        }),
      });
      Alert.alert(
        getText('வெற்றி', 'Saved'),
        getText('ஜாதகம் சேமிக்கப்பட்டது', 'Horoscope saved to your profiles')
      );
    } catch (error) {
      console.error('Error saving profile:', error);
      Alert.alert(
        getText('பிழை', 'Error'),
        error instanceof ApiError
          ? getText(error.detail || 'சேமிக்க முடியவில்லை', error.detail || 'Could not save')
          : getText('சேமிக்க முடியவில்லை. மீண்டும் முயற்சிக்கவும்.', 'Could not save. Please try again.')
      );
    } finally {
      setSaving(false);
    }
  };

  const extractErrorDetail = async (response: Response): Promise<string | undefined> => {
    try {
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const data: any = await response.json();
        return data?.detail ? String(data.detail) : undefined;
      }
      const text = await response.text();
      return text ? text.slice(0, 300) : undefined;
    } catch {
      return undefined;
    }
  };

  const renderBasicInfo = () => {
    if (!horoscopeData) return null;

    return (
      <View testID="horoscope-basic-info-section" style={styles.section}>
        <Text testID="horoscope-basic-info-title" style={styles.sectionTitle}>
          {getText('அடிப்படை விவரங்கள்', 'Basic Information')}
        </Text>
        
        <View style={styles.infoGrid}>
          <CorrectableField
            screenId="horoscope_result"
            field="Name"
            label={getText('பெயர்', 'Name')}
            value={horoscopeData.birth_details.name}
            testID="result-name-card"
          />
          <CorrectableField
            screenId="horoscope_result"
            field="Ascendant"
            label={getText('லக்னம்', 'Ascendant')}
            value={getText(horoscopeData.ascendant_tamil, horoscopeData.ascendant)}
            testID="result-ascendant-card"
          />
          <CorrectableField
            screenId="horoscope_result"
            field="MoonSign"
            label={getText('ராசி', 'Moon Sign')}
            value={getText(horoscopeData.moon_sign_tamil, horoscopeData.moon_sign)}
            testID="result-rasi-card"
          />
          <CorrectableField
            screenId="horoscope_result"
            field="Nakshatra"
            label={getText('நட்சத்திரம்', 'Nakshatra')}
            value={getText(horoscopeData.nakshatra_tamil, horoscopeData.nakshatra)}
            testID="result-nakshatra-card"
          />
        </View>
      </View>
    );
  };

  const renderPlanetaryPositions = () => {
    if (!horoscopeData?.planetary_positions) return null;

    return (
      <View testID="planetary-positions-section" style={styles.section}>
        <Text testID="planetary-positions-title" style={styles.sectionTitle}>
          {getText('கிரக நிலைகள்', 'Planetary Positions')}
        </Text>

        <View style={styles.planetList}>
          {horoscopeData.planetary_positions.map((planet, index) => (
            <View key={`${planet.planet}-${index}`} testID={`planet-position-card-${index}`} style={styles.planetCard}>
              <CorrectableField
                variant="row"
                screenId="horoscope_result"
                field={`Planet.${index}.Name`}
                label={getText('கிரகம்', 'Planet')}
                value={getText(planet.planet_tamil, planet.planet)}
                testID={`planet-${index}-name`}
              />
              <View style={styles.planetGrid}>
                <CorrectableField
                  variant="row"
                  screenId="horoscope_result"
                  field={`Planet.${index}.Degree`}
                  label={getText('பாகை', 'Degree')}
                  value={planet.longitude_dms || 'N/A'}
                  testID={`planet-${index}-degree`}
                />
                <CorrectableField
                  variant="row"
                  screenId="horoscope_result"
                  field={`Planet.${index}.Nakshatra`}
                  label={getText('நட்சத்திரம்', 'Nakshatra')}
                  value={getText(planet.nakshatra_name_tamil, planet.nakshatra_name)}
                  testID={`planet-${index}-nakshatra`}
                />
                <CorrectableField
                  variant="row"
                  screenId="horoscope_result"
                  field={`Planet.${index}.Pada`}
                  label={getText('பாதம்', 'Pada')}
                  value={String(planet.nakshatra_pada || 'N/A')}
                  testID={`planet-${index}-pada`}
                />
                <CorrectableField
                  variant="row"
                  screenId="horoscope_result"
                  field={`Planet.${index}.SignDegree`}
                  label={getText('ராசி பாகை', 'Sign Degree')}
                  value={planet.longitude_in_sign_dms || 'N/A'}
                  testID={`planet-${index}-sign-degree`}
                />
                <CorrectableField
                  variant="row"
                  screenId="horoscope_result"
                  field={`Planet.${index}.Sign`}
                  label={getText('ராசி', 'Sign')}
                  value={getText(planet.sign_name_tamil, planet.sign_name)}
                  testID={`planet-${index}-sign`}
                />
              </View>
            </View>
          ))}
        </View>
      </View>
    );
  };

  const renderChart = (chart: Chart, title: string, titleTamil: string, subtitle?: string) => {
    // Convert houses object to use Tamil labels
    const housesForChart: { [key: number]: string[] } = {};
    for (let i = 1; i <= 12; i++) {
      housesForChart[i] = language === 'tamil' 
        ? (chart.houses_tamil[i.toString()] || [])
        : (chart.houses[i.toString()] || []);
    }

    return (
      <View testID={`chart-section-${chart.chart_type}`} style={styles.section}>
        <Text testID={`chart-title-${chart.chart_type}`} style={styles.sectionTitle}>
          {getText(titleTamil, title)}
        </Text>
        {subtitle ? <Text style={styles.chartMetaText}>{subtitle}</Text> : null}
        
        <View style={styles.chartContainer}>
          <SouthIndianChart 
            houses={housesForChart}
            title={getText(titleTamil, title).toUpperCase()}
            size={chartSize}
          />
        </View>
      </View>
    );
  };

  const formatDateDDMMYYYY = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      const day = date.getDate().toString().padStart(2, '0');
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const year = date.getFullYear();
      return `${day}/${month}/${year}`;
    } catch {
      return dateStr;
    }
  };

  const renderDasaPeriods = () => {
    if (!horoscopeData?.current_dasa) return null;

    const currentDasa = horoscopeData.current_dasa;
    const retrogradePlanets = horoscopeData.retrograde_planets_tamil || [];
    const firstRetrograde = retrogradePlanets.length > 0 ? retrogradePlanets[0] : null;
    const balanceValue = currentDasa.balance_years !== undefined && currentDasa.first_dasha_planet
      ? `${getText(currentDasa.first_dasha_planet_tamil || '', currentDasa.first_dasha_planet)} ${getText('திசை', 'Dasha')} · ${currentDasa.balance_years} ${getText('வருஷம்', 'years')}, ${currentDasa.balance_months || 0} ${getText('மாதம்', 'months')}, ${currentDasa.balance_days || 0} ${getText('நாள்', 'days')}`
      : null;
    const currentBhuktiValue = currentDasa.current_bhukti_planet && currentDasa.current_bhukti_end_date
      ? `${getText(currentDasa.planet_tamil, currentDasa.planet)} ${getText('திசை', 'Dasha')} ${formatDateDDMMYYYY(currentDasa.end_date)} ${getText('வரை', 'until')} · ${getText(currentDasa.current_bhukti_planet_tamil || '', currentDasa.current_bhukti_planet)} ${getText('புக்தி', 'Bhukti')} ${formatDateDDMMYYYY(currentDasa.current_bhukti_end_date)} ${getText('வரை', 'until')}`
      : null;
    const bhavaValue = horoscopeData.bhava_maruthal
      ? `${getText('சந்திரன்', 'Moon')}-${horoscopeData.bhava_maruthal.Moon || 'N/A'}, ${getText('புதன்', 'Mercury')}-${horoscopeData.bhava_maruthal.Mercury || 'N/A'}`
      : null;

    return (
      <View testID="palan-details-section" style={styles.section}>
        <Text testID="palan-details-title" style={styles.sectionTitle}>
          {getText('பலன் மற்றும் தசா விவரங்கள்', 'Palan & Dasa Details')}
        </Text>
        <View style={styles.palanGrid}>
          {firstRetrograde ? (
            <CorrectableField
              variant="row"
              screenId="horoscope_result"
              field="Palan.RetrogradePlanet"
              label={getText('கிரக வக்ர நிலை', 'Retrograde Planet')}
              value={getText(firstRetrograde, horoscopeData.retrograde_planets?.[0] || firstRetrograde)}
              testID="palan-retrograde-card"
            />
          ) : null}
          {balanceValue ? (
            <CorrectableField
              variant="row"
              screenId="horoscope_result"
              field="Palan.DashaBalance"
              label={getText('திசை இருப்பு', 'Dasha Balance')}
              value={balanceValue}
              testID="palan-dasha-balance-card"
            />
          ) : null}
          {currentBhuktiValue ? (
            <CorrectableField
              variant="row"
              screenId="horoscope_result"
              field="Palan.CurrentDashaBhukti"
              label={getText('நடப்பு திசை-புக்தி', 'Current Dasha-Bhukti')}
              value={currentBhuktiValue}
              testID="palan-current-bhukti-card"
            />
          ) : null}
          {bhavaValue ? (
            <CorrectableField
              variant="row"
              screenId="horoscope_result"
              field="Palan.BhavaMaruthal"
              label={getText('பாவக மாறுதல்', 'Bhava Maruthal')}
              value={bhavaValue}
              testID="palan-bhava-card"
            />
          ) : null}
        </View>
      </View>
    );
  };

  const generatePDF = async () => {
    if (!horoscopeData) return;
    
    try {
      setLoading(true);
      
      // Prepare request data
      const requestData = {
        birth_details: {
          name: horoscopeData.birth_details.name,
          date_of_birth: horoscopeData.birth_details.date_of_birth,
          time_of_birth: horoscopeData.birth_details.time_of_birth,
          place_of_birth: horoscopeData.birth_details.place_of_birth,
          latitude: parseFloat(String(horoscopeData.birth_details.latitude || 0)),
          longitude: parseFloat(String(horoscopeData.birth_details.longitude || 0)),
          timezone: horoscopeData.birth_details.timezone || 'IST',
          time_correction: parseInt(String(horoscopeData.birth_details.time_correction || 0))
        },
        system: horoscopeData.system,
        language: horoscopeData.language
      };
      
      const fileName = `horoscope_${horoscopeData.birth_details.name.replace(/\s+/g, '_')}.pdf`;
      
      console.log('Platform:', Platform.OS);
      console.log('Backend URL:', process.env.EXPO_PUBLIC_BACKEND_URL);
      
      if (Platform.OS === 'web') {
        // Web platform - direct download
        console.log('Using web download method');
        const response = await fetchApi('/api/generate-pdf', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData),
        });
        
        if (!response.ok) {
          const detail = await extractErrorDetail(response);
          throw new Error(detail || 'Failed to generate PDF');
        }
        
        // Get the blob
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        Alert.alert(
          getText('வெற்றி', 'Success'),
          getText('PDF பதிவிறக்கம் தொடங்கியது', 'PDF download started')
        );
      } else {
        // Mobile platform - direct download without base64 conversion
        Alert.alert(
          getText('தயாரிக்கப்படுகிறது', 'Preparing'),
          getText('PDF உருவாக்கப்படுகிறது...', 'Generating PDF...')
        );
        
        const fileUri = FileSystem.documentDirectory + fileName;
        
        // Create a temporary file with request data
        const tempRequestFile = FileSystem.documentDirectory + 'temp_request.json';
        await FileSystem.writeAsStringAsync(tempRequestFile, JSON.stringify(requestData));
        
        // Use downloadAsync - it will save the response directly
        // Since downloadAsync doesn't support POST with body, we'll use fetch and read as blob
        const response = await fetchApi('/api/generate-pdf', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData),
        });
        
        if (!response.ok) {
          const detail = await extractErrorDetail(response);
          throw new Error(detail || `Failed to generate PDF: ${response.status}`);
        }
        
        // Read response as blob and convert to base64 using FileReader
        const blob = await response.blob();
        const reader = new (FileReader as any)();
        
        await new Promise((resolve, reject) => {
          reader.onloadend = async () => {
            try {
              const base64data = reader.result;
              // Remove the data URL prefix
              const base64 = base64data.split(',')[1];
              
              // Write to file system
              await FileSystem.writeAsStringAsync(fileUri, base64, {
                encoding: FileSystem.EncodingType.Base64,
              });
              
              resolve(true);
            } catch (error) {
              reject(error);
            }
          };
          reader.onerror = reject;
          reader.readAsDataURL(blob);
        });
        
        // Share the PDF
        await Sharing.shareAsync(fileUri, {
          mimeType: 'application/pdf',
          dialogTitle: getText('ஜாதக PDF', 'Horoscope PDF'),
          UTI: 'com.adobe.pdf'
        });
      }
    } catch (error) {
      console.error('Error generating PDF:', error);
      Alert.alert(
        getText('பிழை', 'Error'),
        isAbortError(error)
          ? getText('நேரம் முடிந்தது. மீண்டும் முயற்சிக்கவும்.', 'Request timed out. Please try again.')
          : getText('PDF உருவாக்குவதில் பிழை: ', 'Error generating PDF: ') +
              (error instanceof Error ? error.message : String(error))
      );
    } finally {
      setLoading(false);
    }
  };

  const generatePalanPDF = async () => {
    if (!horoscopeData) return;

    try {
      setLoading(true);

      const requestData = {
        birth_details: {
          name: horoscopeData.birth_details.name,
          date_of_birth: horoscopeData.birth_details.date_of_birth,
          time_of_birth: horoscopeData.birth_details.time_of_birth,
          place_of_birth: horoscopeData.birth_details.place_of_birth,
          latitude: parseFloat(String((horoscopeData.birth_details as any).latitude || 0)),
          longitude: parseFloat(String((horoscopeData.birth_details as any).longitude || 0)),
          timezone: (horoscopeData.birth_details as any).timezone || 'IST',
          time_correction: parseInt(String((horoscopeData.birth_details as any).time_correction || 0)),
        },
        system: horoscopeData.system,
        language: horoscopeData.language,
      };

      const fileName = `palan_${horoscopeData.birth_details.name.replace(/\s+/g, '_')}.pdf`;

      if (Platform.OS === 'web') {
        const response = await fetchApi('/api/generate-palan-pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData),
        });

        if (!response.ok) {
          const detail = await extractErrorDetail(response);
          throw new Error(detail || 'Failed to generate Palan PDF');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        Alert.alert(
          getText('வெற்றி', 'Success'),
          getText('பலன் PDF பதிவிறக்கம் தொடங்கியது', 'Palan PDF download started')
        );
      } else {
        Alert.alert(
          getText('தயாரிக்கப்படுகிறது', 'Preparing'),
          getText('பலன் PDF உருவாக்கப்படுகிறது...', 'Generating Palan PDF...')
        );

        const fileUri = FileSystem.documentDirectory + fileName;

        const response = await fetchApi('/api/generate-palan-pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData),
        });

        if (!response.ok) {
          const detail = await extractErrorDetail(response);
          throw new Error(detail || `Failed to generate Palan PDF: ${response.status}`);
        }

        const blob = await response.blob();
        const reader = new (FileReader as any)();

        await new Promise((resolve, reject) => {
          reader.onloadend = async () => {
            try {
              const base64data = reader.result;
              const base64 = base64data.split(',')[1];
              await FileSystem.writeAsStringAsync(fileUri, base64, {
                encoding: FileSystem.EncodingType.Base64,
              });
              resolve(true);
            } catch (error) {
              reject(error);
            }
          };
          reader.onerror = reject;
          reader.readAsDataURL(blob);
        });

        await Sharing.shareAsync(fileUri, {
          mimeType: 'application/pdf',
          dialogTitle: getText('பலன் PDF', 'Palan PDF'),
          UTI: 'com.adobe.pdf',
        });
      }
    } catch (error) {
      console.error('Error generating Palan PDF:', error);
      Alert.alert(
        getText('பிழை', 'Error'),
        isAbortError(error)
          ? getText('நேரம் முடிந்தது. மீண்டும் முயற்சிக்கவும்.', 'Request timed out. Please try again.')
          : getText('பலன் PDF உருவாக்குவதில் பிழை: ', 'Error generating Palan PDF: ') +
              (error instanceof Error ? error.message : String(error))
      );
    } finally {
      setLoading(false);
    }
  };

  if (!horoscopeData) {
    return (
      <View style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.brand} />
          <Text style={styles.loadingText}>
            {getText('ஜாதகம் ஏற்றுகிறது...', 'Loading horoscope...')}
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.bg} />
      
      {/* Header */}
      <ScreenHeader
        title={getText('ஜாதக அறிக்கை', 'Horoscope Report')}
        onBack={() => router.back()}
        right={
          <View style={styles.headerActions}>
            <TouchableOpacity testID="save-horoscope-button" style={styles.headerIconBtn} onPress={saveProfile} disabled={saving}>
              {saving ? (
                <ActivityIndicator size="small" color={colors.brandStrong} />
              ) : (
                <Ionicons name="bookmark-outline" size={22} color={colors.brandStrong} />
              )}
            </TouchableOpacity>
            <TouchableOpacity
              testID="result-language-button"
              style={styles.langPill}
              onPress={() => setLanguage(language === 'tamil' ? 'english' : 'tamil')}
            >
              <Text style={styles.langPillText}>{language === 'tamil' ? 'த' : 'EN'}</Text>
            </TouchableOpacity>
          </View>
        }
      />

      <CorrectionControls />

      <ScrollView
        testID="horoscope-result-scroll"
        style={styles.content}
        contentContainerStyle={[
          styles.contentContainer,
          { paddingHorizontal: isCompact ? 12 : 16 },
        ]}
        showsVerticalScrollIndicator={false}
      >
        {renderBasicInfo()}
        {renderPlanetaryPositions()}
        {horoscopeData.rasi_chart && renderChart(
          horoscopeData.rasi_chart, 
          'Rasi Chart', 
          'ராசி கட்டம்'
        )}
        {horoscopeData.navamsa_chart && renderChart(
          horoscopeData.navamsa_chart, 
          'Navamsa Chart', 
          'நவாம்ச கட்டம்'
        )}
        {horoscopeData.karu_udayam_rasi_chart && renderChart(
          horoscopeData.karu_udayam_rasi_chart,
          'Karu Udayam Rasi Chart',
          'கரு உதயம் ராசி கட்டம்',
          `${getText('தமிழ் தேதி', 'Tamil Date')}: ${horoscopeData.karu_udayam_tamil_month || 'N/A'} ${horoscopeData.karu_udayam_tamil_day ?? ''} | ${getText('தேதி', 'Date')}: ${formatDateDDMMYYYY(horoscopeData.karu_udayam_date_of_birth || '')} | ${getText('நேரம்', 'Time')}: ${horoscopeData.karu_udayam_time_of_birth || horoscopeData.birth_details.time_of_birth || 'N/A'}`
        )}
        {renderDasaPeriods()}
      </ScrollView>

      {/* Action Buttons */}
      <SafeAreaView edges={['bottom']} style={styles.actionContainer}>
        <View style={[styles.actionButtonRow, isCompact && styles.actionButtonColumn]}>
          <TouchableOpacity
            testID="generate-horoscope-pdf-button"
            style={styles.actionButton}
            onPress={generatePDF}
            disabled={loading}
          >
            <Ionicons name="document-text-outline" size={20} color={colors.onBrand} />
            <Text style={styles.actionButtonText}>
              {getText('PDF உருவாக்கு', 'Generate PDF')}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            testID="generate-palan-pdf-button"
            style={[styles.actionButton, styles.palanButton]}
            onPress={generatePalanPDF}
            disabled={loading}
          >
            <Ionicons name="star-outline" size={20} color={colors.brandStrong} />
            <Text style={[styles.actionButtonText, { color: colors.brandStrong }]}>
              {getText('பலன் PDF', 'Palan PDF')}
            </Text>
          </TouchableOpacity>
        </View>
        {loading && (
          <ActivityIndicator size="small" color={colors.brand} style={{ marginTop: 8 }} />
        )}
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  headerIconBtn: {
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  langPill: {
    backgroundColor: colors.brandSoft,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: radius.pill,
    minWidth: 44,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 2,
  },
  langPillText: {
    color: colors.brandStrong,
    fontSize: font.sm,
    fontWeight: '700',
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    paddingBottom: 24,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: colors.textSecondary,
    marginTop: 16,
  },
  section: {
    backgroundColor: colors.card,
    borderRadius: 18,
    padding: 16,
    marginTop: 12,
    borderWidth: 1,
    borderColor: colors.border,
    shadowColor: '#8A6B3F',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.06,
    shadowRadius: 10,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 20,
    lineHeight: 30,
    fontWeight: '700',
    color: colors.text,
    marginBottom: 12,
  },
  infoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  planetList: { gap: 12 },
  planetCard: {
    minWidth: 0,
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 14,
    padding: 10,
    gap: 8,
  },
  planetGrid: { gap: 8 },
  chartContainer: {
    alignItems: 'center',
    width: '100%',
    overflow: 'hidden',
  },
  chartMetaText: {
    fontSize: 14,
    lineHeight: 22,
    color: colors.textSecondary,
    marginBottom: 10,
    fontWeight: '500',
  },
  palanGrid: { gap: 10 },
  actionContainer: {
    paddingHorizontal: 16,
    paddingTop: 10,
    paddingBottom: 6,
    backgroundColor: colors.card,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  actionButtonRow: {
    flexDirection: 'row',
    gap: 10,
  },
  actionButtonColumn: { flexDirection: 'column' },
  actionButton: {
    flex: 1,
    backgroundColor: colors.brand,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 50,
    paddingHorizontal: 10,
    paddingVertical: 12,
    borderRadius: radius.pill,
    gap: 8,
  },
  palanButton: {
    backgroundColor: colors.brandSoft,
  },
  actionButtonText: {
    color: colors.onBrand,
    flexShrink: 1,
    fontSize: 13,
    lineHeight: 20,
    fontWeight: '700',
    textAlign: 'center',
  },
});
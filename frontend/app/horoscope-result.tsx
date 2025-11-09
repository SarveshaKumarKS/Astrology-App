import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { router, useLocalSearchParams } from 'expo-router';
import SouthIndianChart from '../components/SouthIndianChart';

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
}

interface HoroscopeData {
  birth_details: {
    name: string;
    date_of_birth: string;
    time_of_birth: string;
    place_of_birth: string;
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
  dasa_periods: DasaPeriod[];
  current_dasa: DasaPeriod;
}

export default function HoroscopeResultPage() {
  const [language, setLanguage] = useState<'tamil' | 'english'>('tamil');
  const [loading, setLoading] = useState(false);
  const [horoscopeData, setHoroscopeData] = useState<HoroscopeData | null>(null);
  const params = useLocalSearchParams();

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

  const renderBasicInfo = () => {
    if (!horoscopeData) return null;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          {getText('அடிப்படை விவரங்கள்', 'Basic Information')}
        </Text>
        
        <View style={styles.infoGrid}>
          <View style={styles.infoCard}>
            <Text style={styles.infoLabel}>
              {getText('பெயர்', 'Name')}
            </Text>
            <Text style={styles.infoValue}>
              {horoscopeData.birth_details.name}
            </Text>
          </View>

          <View style={styles.infoCard}>
            <Text style={styles.infoLabel}>
              {getText('லக்னம்', 'Ascendant')}
            </Text>
            <Text style={styles.infoValue}>
              {getText(horoscopeData.ascendant_tamil, horoscopeData.ascendant)}
            </Text>
          </View>

          <View style={styles.infoCard}>
            <Text style={styles.infoLabel}>
              {getText('ராசி', 'Moon Sign')}
            </Text>
            <Text style={styles.infoValue}>
              {getText(horoscopeData.moon_sign_tamil, horoscopeData.moon_sign)}
            </Text>
          </View>

          <View style={styles.infoCard}>
            <Text style={styles.infoLabel}>
              {getText('நட்சத்திரம்', 'Nakshatra')}
            </Text>
            <Text style={styles.infoValue}>
              {getText(horoscopeData.nakshatra_tamil, horoscopeData.nakshatra)}
            </Text>
          </View>
        </View>
      </View>
    );
  };

  const renderPlanetaryPositions = () => {
    if (!horoscopeData?.planetary_positions) return null;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          {getText('கிரக நிலைகள்', 'Planetary Positions')}
        </Text>
        
        <ScrollView horizontal showsHorizontalScrollIndicator={true}>
          <View style={styles.planetaryTable}>
            <View style={styles.tableHeader}>
              <Text style={[styles.tableHeaderText, { width: 80 }]}>
                {getText('கிரகம்', 'Planet')}
              </Text>
              <Text style={[styles.tableHeaderText, { width: 90 }]}>
                {getText('பாகை', 'Degree')}
              </Text>
              <Text style={[styles.tableHeaderText, { width: 100 }]}>
                {getText('நட்சத்திரம்', 'Nakshatra')}
              </Text>
              <Text style={[styles.tableHeaderText, { width: 60 }]}>
                {getText('பாதம்', 'Pada')}
              </Text>
              <Text style={[styles.tableHeaderText, { width: 80 }]}>
                {getText('தலைவன்', 'Lord')}
              </Text>
              <Text style={[styles.tableHeaderText, { width: 90 }]}>
                {getText('ராசி பாகை', 'Sign Degree')}
              </Text>
              <Text style={[styles.tableHeaderText, { width: 90 }]}>
                {getText('ராசி', 'Sign')}
              </Text>
            </View>
            
            {horoscopeData.planetary_positions.map((planet, index) => (
              <View key={index} style={styles.tableRow}>
                <Text style={[styles.tableCellText, { width: 80 }]}>
                  {getText(planet.planet_tamil, planet.planet)}
                </Text>
                <Text style={[styles.tableCellText, { width: 90 }]}>
                  {planet.longitude_dms || 'N/A'}
                </Text>
                <Text style={[styles.tableCellText, { width: 100 }]}>
                  {getText(planet.nakshatra_name_tamil, planet.nakshatra_name)}
                </Text>
                <Text style={[styles.tableCellText, { width: 60 }]}>
                  {planet.nakshatra_pada || 'N/A'}
                </Text>
                <Text style={[styles.tableCellText, { width: 80 }]}>
                  {getText(planet.nakshatra_lord_tamil || '', planet.nakshatra_lord || 'N/A')}
                </Text>
                <Text style={[styles.tableCellText, { width: 90 }]}>
                  {planet.longitude_in_sign_dms || 'N/A'}
                </Text>
                <Text style={[styles.tableCellText, { width: 90 }]}>
                  {getText(planet.sign_name_tamil, planet.sign_name)}
                </Text>
              </View>
            ))}
          </View>
        </ScrollView>
      </View>
    );
  };

  const renderChart = (chart: Chart, title: string, titleTamil: string) => {
    // Convert houses object to use Tamil labels
    const housesForChart: { [key: number]: string[] } = {};
    for (let i = 1; i <= 12; i++) {
      housesForChart[i] = language === 'tamil' 
        ? (chart.houses_tamil[i.toString()] || [])
        : (chart.houses[i.toString()] || []);
    }

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          {getText(titleTamil, title)}
        </Text>
        
        <View style={styles.chartContainer}>
          <SouthIndianChart 
            houses={housesForChart}
            title={getText(titleTamil, title).toUpperCase()}
          />
        </View>
      </View>
    );
  };

  const renderDasaPeriods = () => {
    if (!horoscopeData?.current_dasa) return null;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          {getText('தசா காலங்கள்', 'Dasa Periods')}
        </Text>
        
        <View style={styles.currentDasaCard}>
          <View style={styles.dasaHeader}>
            <Ionicons name="time-outline" size={24} color="#4A90E2" />
            <Text style={styles.dasaTitle}>
              {getText('தற்போதைய தசா', 'Current Dasa')}
            </Text>
          </View>
          
          <Text style={styles.dasaPlanet}>
            {getText(horoscopeData.current_dasa.planet_tamil, horoscopeData.current_dasa.planet)} 
            {getText(' தசா', ' Dasa')}
          </Text>
          
          <View style={styles.dasaDetails}>
            <Text style={styles.dasaDetailText}>
              {getText('காலம்:', 'Period:')} {horoscopeData.current_dasa.years.toFixed(2)} {getText('ஆண்டுகள்', 'years')} 
              {' '}({horoscopeData.current_dasa.months} {getText('மாதங்கள்', 'months')}, {horoscopeData.current_dasa.days} {getText('நாட்கள்', 'days')})
            </Text>
            <Text style={styles.dasaDetailText}>
              {getText('தொடக்கம்:', 'Start:')} {new Date(horoscopeData.current_dasa.start_date).toLocaleDateString()}
            </Text>
            <Text style={styles.dasaDetailText}>
              {getText('முடிவு:', 'End:')} {new Date(horoscopeData.current_dasa.end_date).toLocaleDateString()}
            </Text>
          </View>
        </View>
      </View>
    );
  };

  const generatePDF = () => {
    Alert.alert(
      getText('PDF உருவாக்கம்', 'PDF Generation'),
      getText('இந்த அம்சம் விரைவில் கிடைக்கும்', 'This feature will be available soon')
    );
  };

  if (!horoscopeData) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4A90E2" />
          <Text style={styles.loadingText}>
            {getText('ஜாதகம் ஏற்றுகிறது...', 'Loading horoscope...')}
          </Text>
        </View>
      </SafeAreaView>
    );
  }

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
            {getText('ஜாதக அறிக்கை', 'Horoscope Report')}
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

      <ScrollView style={styles.content}>
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
        {renderDasaPeriods()}
      </ScrollView>

      {/* Action Buttons */}
      <View style={styles.actionContainer}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={generatePDF}
        >
          <Ionicons name="document-text-outline" size={20} color="#FFFFFF" />
          <Text style={styles.actionButtonText}>
            {getText('PDF உருவாக்கு', 'Generate PDF')}
          </Text>
        </TouchableOpacity>
      </View>
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
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
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
  infoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  infoCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#4A90E2',
  },
  infoLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#7F8C8D',
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
  },
  planetaryTable: {
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#E8E8E8',
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#4A90E2',
    paddingVertical: 12,
    paddingHorizontal: 8,
  },
  tableHeaderText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  tableRow: {
    flexDirection: 'row',
    paddingVertical: 10,
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  tableCellText: {
    fontSize: 11,
    color: '#2C3E50',
    textAlign: 'center',
  },
  chartContainer: {
    alignItems: 'center',
  },
  chartGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    width: 300,
    height: 300,
    borderWidth: 2,
    borderColor: '#2C3E50',
  },
  chartHouse: {
    width: '25%',
    height: '25%',
    borderWidth: 1,
    borderColor: '#7F8C8D',
    padding: 4,
    justifyContent: 'flex-start',
    alignItems: 'flex-start',
  },
  houseNumber: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#E74C3C',
    position: 'absolute',
    top: 2,
    right: 2,
  },
  planetsContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  planetInHouse: {
    fontSize: 8,
    color: '#2C3E50',
    fontWeight: '600',
    textAlign: 'center',
    marginVertical: 1,
  },
  currentDasaCard: {
    backgroundColor: '#E8F4FD',
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#4A90E2',
  },
  dasaHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  dasaTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginLeft: 8,
  },
  dasaPlanet: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4A90E2',
    marginBottom: 12,
  },
  dasaDetails: {
    gap: 4,
  },
  dasaDetailText: {
    fontSize: 14,
    color: '#2C3E50',
  },
  actionContainer: {
    paddingHorizontal: 20,
    paddingVertical: 20,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E8E8E8',
  },
  actionButton: {
    backgroundColor: '#E74C3C',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    gap: 8,
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
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
import { router } from 'expo-router';
import { ApiError, fetchJson, fetchApi, isAbortError } from './api';

interface UserProfile {
  id: string;
  name: string;
  birth_details: {
    name: string;
    date_of_birth: string;
    time_of_birth: string;
    place_of_birth: string;
    latitude: number;
    longitude: number;
    timezone: string;
    time_correction: number;
  };
  created_at: string;
  updated_at: string;
}

export default function ProfilesPage() {
  const [language, setLanguage] = useState<'tamil' | 'english'>('tamil');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [profiles, setProfiles] = useState<UserProfile[]>([]);

  const getText = (tamil: string, english: string) => {
    return language === 'tamil' ? tamil : english;
  };

  const loadProfiles = async () => {
    try {
      const data = await fetchJson<UserProfile[]>('/api/profiles', { method: 'GET' });
      setProfiles(data);
    } catch (error) {
      console.error('Error loading profiles:', error);
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
    loadProfiles();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadProfiles();
  };

  const generateHoroscope = (profile: UserProfile) => {
    Alert.alert(
      getText('ஜாதகம் உருவாக்க', 'Generate Horoscope'),
      getText(`${profile.name} க்கான ஜாதகம் உருவாக்க விரும்புகிறீர்களா?`, `Generate horoscope for ${profile.name}?`),
      [
        {
          text: getText('ரத்து செய்', 'Cancel'),
          style: 'cancel'
        },
        {
          text: getText('உருவாக்கு', 'Generate'),
          onPress: () => {
            // Navigate to horoscope generation with pre-filled data
            router.push({
              pathname: '/horoscope',
              params: {
                prefill: JSON.stringify(profile.birth_details)
              }
            });
          }
        }
      ]
    );
  };

  const deleteProfile = (profileId: string, profileName: string) => {
    Alert.alert(
      getText('நீக்க உறுதிப்படுத்தல்', 'Confirm Delete'),
      getText(`${profileName} என்ற சுயவிவரத்தை நீக்க விரும்புகிறீர்களா?`, `Do you want to delete ${profileName} profile?`),
      [
        {
          text: getText('ரத்து செய்', 'Cancel'),
          style: 'cancel'
        },
        {
          text: getText('நீக்கு', 'Delete'),
          style: 'destructive',
          onPress: async () => {
            try {
              const response = await fetchApi(`/api/profiles/${profileId}`, { method: 'DELETE' });
              
              if (response.ok) {
                setProfiles(profiles.filter(p => p.id !== profileId));
                Alert.alert(
                  getText('வெற்றி', 'Success'),
                  getText('சுயவிவரம் நீக்கப்பட்டது', 'Profile deleted successfully')
                );
              } else {
                throw new Error('Failed to delete profile');
              }
            } catch (error) {
              console.error('Error deleting profile:', error);
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
            }
          }
        }
      ]
    );
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const renderProfile = (profile: UserProfile) => (
    <View key={profile.id} style={styles.profileCard}>
      <View style={styles.profileHeader}>
        <View style={styles.profileIcon}>
          <Ionicons name="person" size={24} color="#4A90E2" />
        </View>
        <View style={styles.profileInfo}>
          <Text style={styles.profileName}>{profile.birth_details.name}</Text>
          <Text style={styles.profilePlace}>{profile.birth_details.place_of_birth}</Text>
          <Text style={styles.profileDate}>
            {formatDate(profile.birth_details.date_of_birth)} • {profile.birth_details.time_of_birth}
          </Text>
        </View>
        <TouchableOpacity
          style={styles.deleteButton}
          onPress={() => deleteProfile(profile.id, profile.birth_details.name)}
        >
          <Ionicons name="trash-outline" size={20} color="#E74C3C" />
        </TouchableOpacity>
      </View>
      
      <View style={styles.profileActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => generateHoroscope(profile)}
        >
          <Ionicons name="planet-outline" size={20} color="#4A90E2" />
          <Text style={styles.actionButtonText}>
            {getText('ஜாதகம்', 'Horoscope')}
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => {
            Alert.alert(
              getText('விரைவில்', 'Coming Soon'),
              getText('இந்த அம்சம் விரைவில் கிடைக்கும்', 'This feature will be available soon')
            );
          }}
        >
          <Ionicons name="heart-outline" size={20} color="#E74C3C" />
          <Text style={styles.actionButtonText}>
            {getText('பொருத்தம்', 'Compatibility')}
          </Text>
        </TouchableOpacity>
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
            {getText('சேமிக்கப்பட்ட விவரங்கள்', 'Saved Profiles')}
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

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4A90E2" />
          <Text style={styles.loadingText}>
            {getText('ஏற்றுகிறது...', 'Loading...')}
          </Text>
        </View>
      ) : (
        <ScrollView
          style={styles.content}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        >
          {profiles.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Ionicons name="person-add-outline" size={64} color="#95A5A6" />
              <Text style={styles.emptyTitle}>
                {getText('சுயவிவரங்கள் இல்லை', 'No Profiles Found')}
              </Text>
              <Text style={styles.emptyDescription}>
                {getText(
                  'ஜாதகம் உருவாக்கும்போது உங்கள் விவரங்களை சேமிக்கவும்',
                  'Save your details while generating horoscope'
                )}
              </Text>
              <TouchableOpacity
                style={styles.createButton}
                onPress={() => router.push('/horoscope')}
              >
                <Text style={styles.createButtonText}>
                  {getText('ஜாதகம் உருவாக்கு', 'Create Horoscope')}
                </Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.profilesList}>
              <Text style={styles.sectionTitle}>
                {getText(`${profiles.length} சுயவிவரங்கள்`, `${profiles.length} Profiles`)}
              </Text>
              {profiles.map(renderProfile)}
            </View>
          )}
          
          {/* Add New Profile Button */}
          {profiles.length > 0 && (
            <TouchableOpacity
              style={styles.addButton}
              onPress={() => router.push('/horoscope')}
            >
              <Ionicons name="add" size={24} color="#FFFFFF" />
              <Text style={styles.addButtonText}>
                {getText('புதிய ஜாதகம்', 'New Horoscope')}
              </Text>
            </TouchableOpacity>
          )}
        </ScrollView>
      )}
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
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 80,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#2C3E50',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyDescription: {
    fontSize: 14,
    color: '#7F8C8D',
    textAlign: 'center',
    marginBottom: 24,
    paddingHorizontal: 32,
    lineHeight: 20,
  },
  createButton: {
    backgroundColor: '#4A90E2',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 24,
  },
  createButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  profilesList: {
    paddingTop: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 16,
  },
  profileCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  profileIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F0F8FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  profileInfo: {
    flex: 1,
  },
  profileName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 4,
  },
  profilePlace: {
    fontSize: 14,
    color: '#7F8C8D',
    marginBottom: 2,
  },
  profileDate: {
    fontSize: 13,
    color: '#95A5A6',
  },
  deleteButton: {
    minWidth: 44,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileActions: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#F8F9FA',
    borderWidth: 1,
    borderColor: '#E8E8E8',
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
    marginLeft: 8,
  },
  addButton: {
    backgroundColor: '#27AE60',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    marginTop: 16,
    marginBottom: 32,
  },
  addButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
});

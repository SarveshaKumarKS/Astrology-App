import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  RefreshControl,
  Modal,
  TextInput,
  Platform,
  KeyboardAvoidingView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { ApiError, fetchJson, isAbortError } from '../lib/api';
import { useAuth } from '../lib/auth';
import ScreenHeader from '../components/ScreenHeader';
import { colors, spacing, radius, font, shadow, lineHeights } from '../lib/theme';

interface UserProfile {
  id: string;
  name: string;
  label?: string;
  birth_details: {
    name: string;
    date_of_birth: string;
    time_of_birth: string;
    place_of_birth: string;
  };
  created_at: string;
  updated_at: string;
}

export default function ProfilesPage() {
  const { user, loading: authLoading, signingIn, login } = useAuth();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [profiles, setProfiles] = useState<UserProfile[]>([]);

  // Rename modal state
  const [renameTarget, setRenameTarget] = useState<UserProfile | null>(null);
  const [renameValue, setRenameValue] = useState('');
  const [renaming, setRenaming] = useState(false);

  const loadProfiles = useCallback(async () => {
    try {
      const data = await fetchJson<UserProfile[]>('/api/profiles', { method: 'GET' });
      setProfiles(data);
    } catch (error) {
      console.error('Error loading profiles:', error);
      Alert.alert(
        'பிழை / Error',
        error instanceof ApiError
          ? error.detail || 'Server error'
          : isAbortError(error)
            ? 'நேரம் முடிந்தது / Request timed out'
            : 'இணைய பிழை / Network error'
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (user) {
      loadProfiles();
    } else {
      setProfiles([]);
      setLoading(false);
    }
  }, [user, loadProfiles]);

  const onRefresh = () => {
    if (!user) return;
    setRefreshing(true);
    loadProfiles();
  };

  const openRename = (profile: UserProfile) => {
    setRenameTarget(profile);
    setRenameValue(profile.label || profile.birth_details.name || '');
  };

  const submitRename = async () => {
    if (!renameTarget || !renameValue.trim()) return;
    setRenaming(true);
    try {
      await fetchJson(`/api/profiles/${renameTarget.id}`, {
        method: 'PUT',
        body: JSON.stringify({ label: renameValue.trim() }),
      });
      setProfiles((prev) =>
        prev.map((p) => (p.id === renameTarget.id ? { ...p, label: renameValue.trim() } : p))
      );
      setRenameTarget(null);
    } catch (error) {
      Alert.alert('பிழை / Error', error instanceof ApiError ? error.detail || 'Could not rename' : 'Could not rename');
    } finally {
      setRenaming(false);
    }
  };

  const generateHoroscope = (profile: UserProfile) => {
    router.push({
      pathname: '/horoscope',
      params: { prefill: JSON.stringify(profile.birth_details) },
    });
  };

  const deleteProfile = (profile: UserProfile) => {
    const displayName = profile.label || profile.birth_details.name;
    Alert.alert(
      'நீக்கு / Delete',
      `"${displayName}" — நீக்க விரும்புகிறீர்களா? / Delete this chart?`,
      [
        { text: 'ரத்து / Cancel', style: 'cancel' },
        {
          text: 'நீக்கு / Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await fetchJson(`/api/profiles/${profile.id}`, { method: 'DELETE' });
              setProfiles((prev) => prev.filter((p) => p.id !== profile.id));
            } catch (error) {
              Alert.alert('பிழை / Error', error instanceof ApiError ? error.detail || 'Could not delete' : 'Could not delete');
            }
          },
        },
      ]
    );
  };

  const formatDate = (dateString: string) => {
    try {
      const d = new Date(dateString);
      return d.toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const renderProfile = (profile: UserProfile) => {
    const displayName = profile.label || profile.birth_details.name;
    return (
      <View key={profile.id} style={styles.card}>
        <View style={styles.cardTop}>
          <View style={styles.avatar}>
            <Ionicons name="star" size={18} color={colors.brandStrong} />
          </View>
          <View style={styles.cardInfo}>
            <Text style={styles.cardName} numberOfLines={1}>{displayName}</Text>
            <Text style={styles.cardMeta} numberOfLines={1}>
              {profile.birth_details.place_of_birth} · {formatDate(profile.birth_details.date_of_birth)} · {profile.birth_details.time_of_birth}
            </Text>
          </View>
        </View>

        <View style={styles.cardActions}>
          <TouchableOpacity style={styles.actionBtn} onPress={() => generateHoroscope(profile)}>
            <Ionicons name="planet-outline" size={18} color={colors.brandStrong} />
            <Text style={styles.actionText}>ஜாதகம்</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionBtn} onPress={() => openRename(profile)}>
            <Ionicons name="create-outline" size={18} color={colors.brandStrong} />
            <Text style={styles.actionText}>மறுபெயர்</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionBtn} onPress={() => deleteProfile(profile)}>
            <Ionicons name="trash-outline" size={18} color={colors.error} />
            <Text style={[styles.actionText, { color: colors.error }]}>நீக்கு</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScreenHeader title="சேமித்த ஜாதகங்கள்" onBack={() => router.back()} />

      {authLoading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.brand} />
        </View>
      ) : !user ? (
        <View style={styles.gate}>
          <View style={styles.gateIcon}>
            <Ionicons name="lock-closed-outline" size={40} color={colors.brandStrong} />
          </View>
          <Text style={styles.gateTitle}>உள்நுழையவும் / Sign In</Text>
          <Text style={styles.gateText}>
            உங்கள் சேமித்த ஜாதகங்களை பாதுகாப்பாக பார்க்க Google மூலம் உள்நுழையவும்.
          </Text>
          <TouchableOpacity style={styles.googleBtn} onPress={login} disabled={signingIn}>
            {signingIn ? (
              <ActivityIndicator color={colors.onBrand} />
            ) : (
              <>
                <Ionicons name="logo-google" size={18} color={colors.onBrand} />
                <Text style={styles.googleBtnText}>Sign in with Google</Text>
              </>
            )}
          </TouchableOpacity>
        </View>
      ) : loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.brand} />
        </View>
      ) : (
        <ScrollView
          contentContainerStyle={{ padding: spacing.lg, paddingBottom: spacing.xxxl }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.brand} />}
          showsVerticalScrollIndicator={false}
        >
          {profiles.length === 0 ? (
            <View style={styles.empty}>
              <View style={styles.gateIcon}>
                <Ionicons name="bookmark-outline" size={40} color={colors.brandStrong} />
              </View>
              <Text style={styles.gateTitle}>ஜாதகங்கள் இல்லை / No Saved Charts</Text>
              <Text style={styles.gateText}>
                ஜாதகம் உருவாக்கியபின், மேலே உள்ள 🔖 பொத்தானை அழுத்தி சேமிக்கவும்.
              </Text>
              <TouchableOpacity style={styles.googleBtn} onPress={() => router.push('/horoscope')}>
                <Text style={styles.googleBtnText}>ஜாதகம் உருவாக்கு</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <>
              <Text style={styles.countLabel}>{profiles.length} ஜாதகங்கள்</Text>
              {profiles.map(renderProfile)}
            </>
          )}
        </ScrollView>
      )}

      {/* Rename modal */}
      <Modal visible={!!renameTarget} transparent animationType="slide" onRequestClose={() => setRenameTarget(null)}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.modalOverlay}>
          <View style={styles.sheet}>
            <View style={styles.sheetHandle} />
            <Text style={styles.sheetTitle}>மறுபெயரிடு / Rename Chart</Text>
            <TextInput
              style={styles.input}
              placeholder="பெயர் / Label"
              placeholderTextColor={colors.textMuted}
              value={renameValue}
              onChangeText={setRenameValue}
              autoFocus
            />
            <View style={styles.sheetActions}>
              <TouchableOpacity style={styles.cancelBtn} onPress={() => setRenameTarget(null)}>
                <Text style={styles.cancelText}>ரத்து / Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.sendBtn, (!renameValue.trim() || renaming) && { opacity: 0.5 }]}
                onPress={submitRename}
                disabled={!renameValue.trim() || renaming}
              >
                {renaming ? <ActivityIndicator color={colors.onBrand} /> : <Text style={styles.sendText}>சேமி / Save</Text>}
              </TouchableOpacity>
            </View>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  gate: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: spacing.xxl },
  empty: { alignItems: 'center', paddingTop: spacing.xxxl },
  gateIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.brandSoft,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  gateTitle: { fontSize: font.xl, fontWeight: '700', color: colors.text, textAlign: 'center' },
  gateText: {
    fontSize: font.base,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.sm,
    lineHeight: lineHeights.body,
  },
  googleBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.brand,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderRadius: radius.pill,
    marginTop: spacing.xl,
    gap: spacing.sm,
    minWidth: 220,
    minHeight: 48,
  },
  googleBtnText: { color: colors.onBrand, fontSize: font.lg, fontWeight: '700' },
  countLabel: {
    fontSize: font.sm,
    fontWeight: '700',
    color: colors.textMuted,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: spacing.md,
    marginLeft: spacing.xs,
  },
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...shadow.card,
  },
  cardTop: { flexDirection: 'row', alignItems: 'center' },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: radius.md,
    backgroundColor: colors.brandSoft,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  cardInfo: { flex: 1 },
  cardName: { fontSize: font.lg, fontWeight: '700', color: colors.text },
  cardMeta: { fontSize: font.sm, color: colors.textSecondary, marginTop: 2 },
  cardActions: {
    flexDirection: 'row',
    marginTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.md,
    justifyContent: 'space-between',
  },
  actionBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingVertical: 4, paddingHorizontal: 6 },
  actionText: { fontSize: font.base, fontWeight: '600', color: colors.brandStrong },
  modalOverlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.35)' },
  sheet: {
    backgroundColor: colors.card,
    borderTopLeftRadius: radius.xl,
    borderTopRightRadius: radius.xl,
    padding: spacing.xl,
    paddingBottom: spacing.xxl,
  },
  sheetHandle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.border,
    alignSelf: 'center',
    marginBottom: spacing.lg,
  },
  sheetTitle: { fontSize: font.xl, fontWeight: '700', color: colors.text },
  input: {
    backgroundColor: colors.surfaceTertiary,
    borderRadius: radius.md,
    padding: spacing.lg,
    fontSize: font.lg,
    color: colors.text,
    marginTop: spacing.lg,
  },
  sheetActions: { flexDirection: 'row', gap: spacing.md, marginTop: spacing.lg },
  cancelBtn: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    borderRadius: radius.pill,
    backgroundColor: colors.surfaceTertiary,
  },
  cancelText: { color: colors.textSecondary, fontSize: font.base, fontWeight: '700' },
  sendBtn: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    borderRadius: radius.pill,
    backgroundColor: colors.brand,
    minHeight: 48,
  },
  sendText: { color: colors.onBrand, fontSize: font.base, fontWeight: '700' },
});

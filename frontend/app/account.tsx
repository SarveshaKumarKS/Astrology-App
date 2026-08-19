import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Modal,
  TextInput,
  ActivityIndicator,
  Alert,
  Platform,
  KeyboardAvoidingView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { colors, spacing, radius, font, shadow, lineHeights } from '../lib/theme';
import { useAuth } from '../lib/auth';
import ScreenHeader from '../components/ScreenHeader';
import { fetchApi } from '../lib/api';
import { useLanguage } from '../lib/language';

export default function AccountPage() {
  const { user, loading, signingIn, login, logout } = useAuth();
  const { getText } = useLanguage();
  const [reportOpen, setReportOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);

  const initials = (user?.name || user?.email || '?').trim().charAt(0).toUpperCase();

  const submitFeedback = async () => {
    if (!message.trim()) return;
    setSending(true);
    try {
      await fetchApi('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message.trim(),
          screen: 'account',
          platform: Platform.OS,
        }),
      });
      setMessage('');
      setReportOpen(false);
      Alert.alert(getText('நன்றி', 'Thank you'), getText('உங்கள் கருத்து பதிவு செய்யப்பட்டது.', 'Your feedback has been logged.'));
    } catch {
      Alert.alert(getText('பிழை', 'Error'), getText('அனுப்ப முடியவில்லை. மீண்டும் முயற்சிக்கவும்.', 'Could not send. Please try again.'));
    } finally {
      setSending(false);
    }
  };

  const confirmLogout = () => {
    Alert.alert(getText('வெளியேறு', 'Logout'), getText('நிச்சயமாக வெளியேற விரும்புகிறீர்களா?', 'Are you sure you want to log out?'), [
      { text: getText('ரத்து', 'Cancel'), style: 'cancel' },
      { text: getText('வெளியேறு', 'Logout'), style: 'destructive', onPress: () => logout() },
    ]);
  };

  return (
    <SafeAreaView style={styles.container} edges={['top', 'bottom']}>
      <ScreenHeader title={getText('கணக்கு', 'Account')} onBack={() => router.back()} />

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator color={colors.brand} size="large" />
        </View>
      ) : !user ? (
        <View style={styles.gate}>
          <View style={styles.avatarLarge}>
            <Ionicons name="person-outline" size={40} color={colors.brandStrong} />
          </View>
          <Text style={styles.gateTitle}>{getText('உள்நுழையவும்', 'Sign In')}</Text>
          <Text style={styles.gateText}>
            {getText('உங்கள் சேமித்த ஜாதகங்களை பாதுகாப்பாக பார்க்க Google மூலம் உள்நுழையவும்.', 'Sign in with Google to securely access your saved horoscopes.')}
          </Text>
          <TouchableOpacity testID="account-google-signin-button" style={styles.googleBtn} onPress={login} disabled={signingIn}>
            {signingIn ? (
              <ActivityIndicator color={colors.onBrand} />
            ) : (
              <>
                <Ionicons name="logo-google" size={18} color={colors.onBrand} />
                <Text style={styles.googleBtnText}>{getText('Google மூலம் உள்நுழைக', 'Sign in with Google')}</Text>
              </>
            )}
          </TouchableOpacity>
        </View>
      ) : (
        <ScrollView contentContainerStyle={{ padding: spacing.lg }} showsVerticalScrollIndicator={false}>
          {/* Profile */}
          <View style={styles.profile}>
            {user.picture ? (
              <Image source={{ uri: user.picture }} style={styles.avatarImg} />
            ) : (
              <View style={styles.avatarLarge}>
                <Text style={styles.initials}>{initials}</Text>
              </View>
            )}
            <Text style={styles.name}>{user.name || getText('பயனர்', 'User')}</Text>
            <Text style={styles.email}>{user.email}</Text>
          </View>

          {/* Settings group */}
          <View style={styles.group}>
            <TouchableOpacity testID="account-report-issue-button" style={styles.row} onPress={() => setReportOpen(true)}>
              <View style={[styles.rowIcon, { backgroundColor: colors.brandSoft }]}>
                <Ionicons name="chatbox-ellipses-outline" size={20} color={colors.brandStrong} />
              </View>
              <View style={styles.rowBody}>
                <Text style={styles.rowTitle}>{getText('சிக்கலைத் தெரிவிக்க', 'Report an Issue')}</Text>
                <Text style={styles.rowSub}>{getText('சோதனையின்போது கண்ட தவறுகளைப் பதிவு செய்க', 'Report an error or share feedback')}</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color={colors.textMuted} />
            </TouchableOpacity>

            <View style={styles.rowDivider} />

            <TouchableOpacity testID="account-saved-charts-button" style={styles.row} onPress={() => router.push('/profiles')}>
              <View style={[styles.rowIcon, { backgroundColor: colors.brandSoft }]}>
                <Ionicons name="bookmark-outline" size={20} color={colors.brandStrong} />
              </View>
              <View style={styles.rowBody}>
                <Text style={styles.rowTitle}>{getText('சேமித்த ஜாதகங்கள்', 'Saved Charts')}</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color={colors.textMuted} />
            </TouchableOpacity>
          </View>

          {/* Logout */}
          <TouchableOpacity testID="account-logout-button" style={styles.logoutBtn} onPress={confirmLogout}>
            <Ionicons name="log-out-outline" size={20} color={colors.error} />
            <Text style={styles.logoutText}>{getText('வெளியேறு', 'Logout')}</Text>
          </TouchableOpacity>
        </ScrollView>
      )}

      {/* Report issue modal */}
      <Modal visible={reportOpen} transparent animationType="slide" onRequestClose={() => setReportOpen(false)}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          style={styles.modalOverlay}
        >
          <View style={styles.sheet}>
            <View style={styles.sheetHandle} />
            <Text style={styles.sheetTitle}>{getText('சிக்கலைத் தெரிவிக்க', 'Report an Issue')}</Text>
            <Text style={styles.sheetHint}>
              {getText('நீங்கள் கண்ட தவறு அல்லது கருத்தை எழுதுங்கள். எங்கள் குழு அதைச் சரிசெய்யும்.', 'Describe the problem or feedback. Our team will review it.')}
            </Text>
            <TextInput
              testID="account-feedback-input"
              style={styles.input}
              placeholder={getText('எ.கா. நேரக் கணக்கீட்டில் தவறு...', 'e.g. wrong time calculation...')}
              placeholderTextColor={colors.textMuted}
              value={message}
              onChangeText={setMessage}
              multiline
              textAlignVertical="top"
            />
            <View style={styles.sheetActions}>
              <TouchableOpacity testID="account-feedback-cancel-button" style={styles.cancelBtn} onPress={() => setReportOpen(false)}>
                <Text style={styles.cancelText}>{getText('ரத்து', 'Cancel')}</Text>
              </TouchableOpacity>
              <TouchableOpacity
                testID="account-feedback-submit-button"
                style={[styles.sendBtn, (!message.trim() || sending) && { opacity: 0.5 }]}
                onPress={submitFeedback}
                disabled={!message.trim() || sending}
              >
                {sending ? (
                  <ActivityIndicator color={colors.onBrand} />
                ) : (
                  <Text style={styles.sendText}>{getText('அனுப்பு', 'Send')}</Text>
                )}
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
  gateTitle: { fontSize: font.xl, fontWeight: '700', color: colors.text, marginTop: spacing.lg },
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
  profile: { alignItems: 'center', paddingVertical: spacing.lg },
  avatarImg: { width: 88, height: 88, borderRadius: 44, backgroundColor: colors.brandSoft },
  avatarLarge: {
    width: 88,
    height: 88,
    borderRadius: 44,
    backgroundColor: colors.brandSoft,
    justifyContent: 'center',
    alignItems: 'center',
  },
  initials: { fontSize: font.xxxl, fontWeight: '800', color: colors.brandStrong },
  name: { fontSize: font.xl, fontWeight: '700', color: colors.text, marginTop: spacing.md },
  email: { fontSize: font.base, color: colors.textSecondary, marginTop: 2 },
  group: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    marginTop: spacing.lg,
    overflow: 'hidden',
    ...shadow.soft,
  },
  row: { flexDirection: 'row', alignItems: 'center', padding: spacing.lg },
  rowIcon: {
    width: 40,
    height: 40,
    borderRadius: radius.sm,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  rowBody: { flex: 1 },
  rowTitle: { fontSize: font.base, fontWeight: '600', color: colors.text },
  rowSub: { fontSize: font.sm, color: colors.textSecondary, marginTop: 2 },
  rowDivider: { height: 1, backgroundColor: colors.border, marginLeft: 68 },
  logoutBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    paddingVertical: spacing.lg,
    marginTop: spacing.lg,
    gap: spacing.sm,
    ...shadow.soft,
  },
  logoutText: { color: colors.error, fontSize: font.lg, fontWeight: '700' },
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
  sheetHint: {
    fontSize: font.base,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    lineHeight: lineHeights.body,
  },
  input: {
    backgroundColor: colors.surfaceTertiary,
    borderRadius: radius.md,
    padding: spacing.lg,
    minHeight: 120,
    fontSize: font.base,
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

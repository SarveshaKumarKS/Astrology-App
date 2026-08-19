import React, { createContext, useContext, useMemo, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  ScrollView,
  TextInput,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import Constants from 'expo-constants';
import { Ionicons } from '@expo/vector-icons';
import { fetchApi } from './api';
import { colors, spacing, radius, font } from './theme';

export interface CorrectionItem {
  screen_id: string;
  field_name: string;
  original_value: string;
  corrected_value: string;
}

interface DebugContextValue {
  correctionMode: boolean;
  toggleMode: () => void;
  corrections: Record<string, CorrectionItem>;
  getCorrection: (screenId: string, field: string) => CorrectionItem | undefined;
  setCorrection: (screenId: string, field: string, original: string, corrected: string) => void;
  removeCorrection: (key: string) => void;
}

const keyOf = (screenId: string, field: string) => `${screenId}::${field}`;

const DebugContext = createContext<DebugContextValue | undefined>(undefined);

const APP_VERSION =
  (Constants.expoConfig?.version as string) ||
  ((Constants as any).manifest?.version as string) ||
  '1.0.0';
const DEVICE_MODEL = `${Platform.OS} ${Platform.Version ?? ''}`.trim();

export function DebugProvider({ children }: { children: React.ReactNode }) {
  const [correctionMode, setCorrectionMode] = useState(false);
  const [corrections, setCorrections] = useState<Record<string, CorrectionItem>>({});

  const toggleMode = useCallback(() => {
    setCorrectionMode((prev) => !prev);
  }, []);

  const setCorrection = useCallback((screenId: string, field: string, original: string, corrected: string) => {
    setCorrections((prev) => {
      const next = { ...prev };
      const k = keyOf(screenId, field);
      if (!corrected.trim()) {
        delete next[k];
      } else {
        next[k] = { screen_id: screenId, field_name: field, original_value: original, corrected_value: corrected.trim() };
      }
      return next;
    });
  }, []);

  const removeCorrection = useCallback((k: string) => {
    setCorrections((prev) => {
      const next = { ...prev };
      delete next[k];
      return next;
    });
  }, []);

  const getCorrection = useCallback(
    (screenId: string, field: string) => corrections[keyOf(screenId, field)],
    [corrections]
  );

  const value = useMemo(
    () => ({ correctionMode, toggleMode, corrections, getCorrection, setCorrection, removeCorrection }),
    [correctionMode, toggleMode, corrections, getCorrection, setCorrection, removeCorrection]
  );

  return (
    <DebugContext.Provider value={value}>
      {children}
    </DebugContext.Provider>
  );
}

export function useDebug(): DebugContextValue {
  const ctx = useContext(DebugContext);
  if (!ctx) throw new Error('useDebug must be used within DebugProvider');
  return ctx;
}

/** Result-screen-only controls. Keeping this outside the provider prevents
 * Correction Mode UI from leaking onto forms, profiles, or other screens. */
export function CorrectionControls() {
  const { correctionMode, toggleMode, corrections, removeCorrection } = useDebug();
  const [reviewOpen, setReviewOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [note, setNote] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const entries = Object.entries(corrections);
  const count = entries.length;

  const confirmEnter = () => {
    setConfirmOpen(true);
  };

  if (!correctionMode) {
    return (
      <>
        <View testID="correction-mode-entry" style={styles.entryBar}>
          <View style={styles.entryCopy}>
            <View style={styles.entryIcon}>
              <Ionicons name="construct-outline" size={18} color={colors.brandStrong} />
            </View>
            <View style={styles.entryTextWrap}>
              <Text testID="correction-mode-entry-title" style={styles.entryTitle}>Found a wrong value?</Text>
              <Text style={styles.entrySubtitle} numberOfLines={1}>Open Correction Mode to report it</Text>
            </View>
          </View>
          <TouchableOpacity
            testID="correction-mode-enter-button"
            style={styles.enterBtn}
            onPress={confirmEnter}
            activeOpacity={0.85}
          >
            <Text style={styles.enterBtnText}>Correct</Text>
          </TouchableOpacity>
        </View>

        <Modal visible={confirmOpen} transparent animationType="fade" onRequestClose={() => setConfirmOpen(false)}>
          <View testID="correction-mode-confirmation" style={styles.confirmOverlay}>
            <View style={styles.confirmDialog}>
              <View style={styles.confirmIcon}>
                <Ionicons name="construct-outline" size={24} color={colors.brandStrong} />
              </View>
              <Text testID="correction-mode-confirmation-title" style={styles.confirmTitle}>Enter Correction Mode?</Text>
              <Text style={styles.confirmBody}>
                Edit incorrect result values and submit them for review. Kattam charts stay read-only.
              </Text>
              <View style={styles.actions}>
                <TouchableOpacity testID="correction-mode-confirm-cancel" style={styles.cancelBtn} onPress={() => setConfirmOpen(false)}>
                  <Text style={styles.cancelText}>Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  testID="correction-mode-confirm-enter"
                  style={styles.sendBtn}
                  onPress={() => {
                    setConfirmOpen(false);
                    toggleMode();
                  }}
                >
                  <Text style={styles.sendText}>Enter</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>
      </>
    );
  }

  const submit = async () => {
    if (count === 0) return;
    setSubmitting(true);
    try {
      const response = await fetchApi('/api/corrections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          corrections: entries.map(([, value]) => value),
          app_version: APP_VERSION,
          device_model: DEVICE_MODEL,
          platform: Platform.OS,
          note: note.trim(),
        }),
      });
      if (!response.ok) throw new Error('Correction submission failed');
      entries.forEach(([key]) => removeCorrection(key));
      setNote('');
      setReviewOpen(false);
      Alert.alert('நன்றி / Thank you', 'திருத்தங்கள் பதிவு செய்யப்பட்டன.\nCorrections submitted.');
    } catch {
      Alert.alert('பிழை / Error', 'அனுப்ப முடியவில்லை. மீண்டும் முயற்சிக்கவும்.\nCould not submit. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <View testID="correction-mode-toolbar" style={styles.banner}>
        <View style={styles.bannerLabel}>
          <Ionicons name="build-outline" size={16} color={colors.brandStrong} />
          <Text style={styles.bannerText} numberOfLines={1}>Correction Mode</Text>
        </View>
        <View style={styles.bannerActions}>
          <TouchableOpacity testID="correction-mode-exit-button" style={styles.exitBtn} onPress={toggleMode}>
            <Text style={styles.exitBtnText}>Exit</Text>
          </TouchableOpacity>
          <TouchableOpacity
            testID="correction-review-button"
            style={styles.reviewBtn}
            onPress={() => setReviewOpen(true)}
          >
            <Text style={styles.reviewBtnText}>Review{count ? ` (${count})` : ''}</Text>
            <Ionicons name="chevron-forward" size={16} color={colors.onBrand} />
          </TouchableOpacity>
        </View>
      </View>

      <Modal visible={reviewOpen} transparent animationType="slide" onRequestClose={() => setReviewOpen(false)}>
        <View testID="correction-review-modal" style={styles.overlay}>
          <View style={styles.sheet}>
            <View style={styles.handle} />
            <Text testID="correction-review-title" style={styles.sheetTitle}>Submit Corrections</Text>
            <Text testID="correction-device-meta" style={styles.meta}>v{APP_VERSION} · {DEVICE_MODEL}</Text>

            {count === 0 ? (
              <Text testID="correction-empty-message" style={styles.emptyText}>
                No corrections yet. Tap a highlighted result value to fix it.
              </Text>
            ) : (
              <ScrollView style={{ maxHeight: 280 }}>
                {entries.map(([key, value]) => (
                  <View key={key} testID={`correction-review-item-${key}`} style={styles.row}>
                    <View style={{ flex: 1, minWidth: 0 }}>
                      <Text style={styles.rowField}>{value.field_name}</Text>
                      <Text style={styles.rowOld} numberOfLines={1}>Was: {value.original_value || '—'}</Text>
                      <Text style={styles.rowNew} numberOfLines={1}>Now: {value.corrected_value}</Text>
                    </View>
                    <TouchableOpacity testID={`remove-correction-${key}`} onPress={() => removeCorrection(key)} hitSlop={8}>
                      <Ionicons name="close-circle" size={24} color={colors.textMuted} />
                    </TouchableOpacity>
                  </View>
                ))}
              </ScrollView>
            )}

            <TextInput
              testID="correction-note-input"
              style={styles.note}
              placeholder="Extra note (optional)"
              placeholderTextColor={colors.textMuted}
              value={note}
              onChangeText={setNote}
              multiline
              textAlignVertical="top"
            />

            <View style={styles.actions}>
              <TouchableOpacity testID="correction-review-close-button" style={styles.cancelBtn} onPress={() => setReviewOpen(false)}>
                <Text style={styles.cancelText}>Close</Text>
              </TouchableOpacity>
              <TouchableOpacity
                testID="correction-submit-button"
                style={[styles.sendBtn, (count === 0 || submitting) && { opacity: 0.5 }]}
                onPress={submit}
                disabled={count === 0 || submitting}
              >
                {submitting ? <ActivityIndicator color={colors.onBrand} /> : <Text style={styles.sendText}>Submit</Text>}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  entryBar: {
    minHeight: 64,
    backgroundColor: colors.card,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: spacing.sm,
  },
  entryCopy: { flex: 1, minWidth: 0, flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  entryIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.brandSoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
  entryTextWrap: { flex: 1, minWidth: 0 },
  entryTitle: { color: colors.text, fontSize: font.base, lineHeight: 20, fontWeight: '700' },
  entrySubtitle: { color: colors.textSecondary, fontSize: font.sm, lineHeight: 18 },
  enterBtn: {
    minWidth: 76,
    minHeight: 44,
    borderRadius: radius.pill,
    backgroundColor: colors.brandSoft,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.md,
  },
  enterBtnText: { color: colors.brandStrong, fontSize: font.sm, fontWeight: '800' },
  confirmOverlay: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
    backgroundColor: 'rgba(43, 29, 20, 0.36)',
  },
  confirmDialog: {
    width: '100%',
    maxWidth: 400,
    borderRadius: radius.xl,
    backgroundColor: colors.card,
    padding: spacing.xl,
  },
  confirmIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.brandSoft,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
  },
  confirmTitle: { color: colors.text, fontSize: font.xl, lineHeight: 28, fontWeight: '800' },
  confirmBody: { color: colors.textSecondary, fontSize: font.base, lineHeight: 22, marginTop: spacing.sm },
  banner: {
    backgroundColor: colors.brandSoft,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  bannerLabel: { flex: 1, minWidth: 0, flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  bannerText: { flexShrink: 1, color: colors.brandStrong, fontSize: font.sm, fontWeight: '800' },
  bannerActions: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  exitBtn: {
    minHeight: 40,
    paddingHorizontal: spacing.md,
    borderRadius: radius.pill,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.borderStrong,
    backgroundColor: colors.card,
  },
  exitBtnText: { color: colors.textSecondary, fontSize: font.sm, fontWeight: '700' },
  reviewBtn: {
    backgroundColor: colors.brand,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    minHeight: 40,
    paddingHorizontal: spacing.md,
    borderRadius: radius.pill,
  },
  reviewBtnText: { color: colors.onBrand, fontSize: font.sm, fontWeight: '800' },
  overlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.35)' },
  sheet: {
    backgroundColor: colors.card,
    borderTopLeftRadius: radius.xl,
    borderTopRightRadius: radius.xl,
    padding: spacing.xl,
    paddingBottom: spacing.xxl,
  },
  handle: { width: 40, height: 4, borderRadius: 2, backgroundColor: colors.border, alignSelf: 'center', marginBottom: spacing.lg },
  sheetTitle: { fontSize: font.xl, fontWeight: '700', color: colors.text },
  meta: { fontSize: font.sm, color: colors.textMuted, marginTop: 2, marginBottom: spacing.md },
  emptyText: { fontSize: font.base, color: colors.textSecondary, lineHeight: 22, paddingVertical: spacing.lg },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surfaceTertiary,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
    gap: spacing.sm,
  },
  rowField: { fontSize: font.sm, fontWeight: '700', color: colors.textSecondary },
  rowOld: { fontSize: font.base, color: colors.error, marginTop: 2 },
  rowNew: { fontSize: font.base, color: colors.success, fontWeight: '600', marginTop: 1 },
  note: {
    backgroundColor: colors.surfaceTertiary,
    borderRadius: radius.md,
    padding: spacing.md,
    minHeight: 60,
    fontSize: font.base,
    color: colors.text,
    marginTop: spacing.md,
  },
  actions: { flexDirection: 'row', gap: spacing.md, marginTop: spacing.lg },
  cancelBtn: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: spacing.md, borderRadius: radius.pill, backgroundColor: colors.surfaceTertiary },
  cancelText: { color: colors.textSecondary, fontSize: font.base, fontWeight: '700' },
  sendBtn: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: spacing.md, borderRadius: radius.pill, backgroundColor: colors.brand, minHeight: 48 },
  sendText: { color: colors.onBrand, fontSize: font.base, fontWeight: '700' },
});

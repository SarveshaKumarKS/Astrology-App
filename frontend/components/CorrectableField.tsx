import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  TextInput,
  Platform,
  KeyboardAvoidingView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useDebug } from '../lib/debug';
import { colors, spacing, radius, font } from '../lib/theme';

interface Props {
  screenId: string;
  field: string;   // human-readable field name (used as field_name)
  label: string;   // shown label
  value: string;   // original on-screen value
  variant?: 'card' | 'row';
  testID?: string;
}

/**
 * Displays a labelled value. In Correction Mode the value becomes tappable —
 * the customer can enter a corrected value which is captured for logging.
 */
export default function CorrectableField({ screenId, field, label, value, variant = 'card', testID }: Props) {
  const { correctionMode, getCorrection, setCorrection } = useDebug();
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState('');

  const existing = getCorrection(screenId, field);
  const corrected = existing?.corrected_value;
  const fieldTestID = testID || `correctable-${field.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;

  const startEdit = () => {
    setDraft(corrected ?? value ?? '');
    setOpen(true);
  };

  const save = () => {
    setCorrection(screenId, field, value ?? '', draft);
    setOpen(false);
  };

  return (
    <>
      <TouchableOpacity
        testID={fieldTestID}
        activeOpacity={correctionMode ? 0.7 : 1}
        onPress={correctionMode ? startEdit : undefined}
        style={[
          variant === 'card' ? styles.card : styles.rowValue,
          correctionMode && styles.cardEditable,
          corrected != null && styles.cardCorrected,
        ]}
      >
        <View style={styles.labelRow}>
          <Text style={styles.label}>{label}</Text>
          {correctionMode && (
            <Ionicons
              name={corrected != null ? 'checkmark-circle' : 'create-outline'}
              size={16}
              color={corrected != null ? colors.success : colors.brandStrong}
            />
          )}
        </View>
        <Text style={[styles.value, variant === 'row' && styles.rowValueText, corrected != null && styles.valueCorrected]} numberOfLines={2}>
          {corrected != null ? corrected : value}
        </Text>
        {corrected != null && (
          <Text style={styles.wasText} numberOfLines={1}>was: {value || '—'}</Text>
        )}
      </TouchableOpacity>

      {open ? (
        <Modal visible transparent animationType="none" onRequestClose={() => setOpen(false)}>
          <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            style={styles.overlay}
          >
            <View testID={`${fieldTestID}-edit-dialog`} style={styles.dialog}>
              <Text testID={`${fieldTestID}-edit-title`} style={styles.dialogTitle}>{label}</Text>
              <Text testID={`${fieldTestID}-original-value`} style={styles.original}>Original: {value || '—'}</Text>
              <TextInput
                testID={`${fieldTestID}-correction-input`}
                style={styles.input}
                value={draft}
                onChangeText={setDraft}
                placeholder="சரியான மதிப்பு / Correct value"
                placeholderTextColor={colors.textMuted}
                autoFocus
              />
              <View style={styles.actions}>
                <TouchableOpacity testID={`${fieldTestID}-correction-cancel`} style={styles.cancelBtn} onPress={() => setOpen(false)}>
                  <Text style={styles.cancelText}>ரத்து / Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity testID={`${fieldTestID}-correction-save`} style={styles.saveBtn} onPress={save}>
                  <Text style={styles.saveText}>சேமி / Save</Text>
                </TouchableOpacity>
              </View>
            </View>
          </KeyboardAvoidingView>
        </Modal>
      ) : null}
    </>
  );
}

const styles = StyleSheet.create({
  card: {
    flexGrow: 1,
    flexBasis: '47%',
    minWidth: 0,
    backgroundColor: colors.surfaceTertiary,
    borderRadius: radius.md,
    padding: spacing.md,
    minHeight: 92,
  },
  rowValue: {
    width: '100%',
    minWidth: 0,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radius.md,
    backgroundColor: colors.surfaceTertiary,
  },
  cardEditable: {
    borderWidth: 1,
    borderColor: colors.brand,
    borderStyle: 'dashed',
  },
  cardCorrected: {
    backgroundColor: '#EAF6EC',
    borderColor: colors.success,
    borderStyle: 'solid',
  },
  labelRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  label: { flexShrink: 1, fontSize: font.sm, lineHeight: 18, color: colors.textSecondary, fontWeight: '600' },
  value: { flexShrink: 1, fontSize: font.lg, lineHeight: 24, color: colors.text, fontWeight: '700', marginTop: 4 },
  rowValueText: { fontSize: font.base, lineHeight: 21 },
  valueCorrected: { color: colors.success },
  wasText: { fontSize: 11, color: colors.textMuted, marginTop: 2, textDecorationLine: 'line-through' },
  overlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.4)', padding: spacing.xl },
  dialog: { width: '100%', maxWidth: 420, backgroundColor: colors.card, borderRadius: radius.lg, padding: spacing.xl },
  dialogTitle: { fontSize: font.lg, fontWeight: '700', color: colors.text },
  original: { fontSize: font.base, color: colors.textSecondary, marginTop: spacing.xs, marginBottom: spacing.md },
  input: {
    backgroundColor: colors.surfaceTertiary,
    borderRadius: radius.md,
    padding: spacing.md,
    fontSize: font.lg,
    color: colors.text,
  },
  actions: { flexDirection: 'row', gap: spacing.md, marginTop: spacing.lg },
  cancelBtn: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: spacing.md, borderRadius: radius.pill, backgroundColor: colors.surfaceTertiary },
  cancelText: { color: colors.textSecondary, fontSize: font.base, fontWeight: '700' },
  saveBtn: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: spacing.md, borderRadius: radius.pill, backgroundColor: colors.brand },
  saveText: { color: colors.onBrand, fontSize: font.base, fontWeight: '700' },
});

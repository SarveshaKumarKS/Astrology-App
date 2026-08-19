import React, { useEffect, useState } from 'react';
import { Modal, Platform, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import DateTimePicker, { DateTimePickerEvent } from '@react-native-community/datetimepicker';
import { colors, font, radius, spacing } from '../lib/theme';

interface Props {
  visible: boolean;
  mode: 'date' | 'time';
  value: Date;
  title: string;
  cancelLabel: string;
  confirmLabel: string;
  testID: string;
  maximumDate?: Date;
  onCancel: () => void;
  onConfirm: (value: Date) => void;
}

const pad = (value: number) => String(value).padStart(2, '0');

export default function NativeDateTimePicker({
  visible,
  mode,
  value,
  title,
  cancelLabel,
  confirmLabel,
  testID,
  maximumDate,
  onCancel,
  onConfirm,
}: Props) {
  const [draft, setDraft] = useState(value);
  const [parts, setParts] = useState({ day: '', month: '', year: '', hour: '', minute: '' });

  useEffect(() => {
    if (!visible) return;
    setDraft(value);
    setParts({
      day: pad(value.getDate()),
      month: pad(value.getMonth() + 1),
      year: String(value.getFullYear()),
      hour: pad(value.getHours()),
      minute: pad(value.getMinutes()),
    });
  }, [value, visible]);

  if (!visible) return null;

  const handleNativeChange = (event: DateTimePickerEvent, selected?: Date) => {
    if (Platform.OS === 'android') {
      if (event.type === 'set' && selected) onConfirm(selected);
      else onCancel();
      return;
    }
    if (selected) setDraft(selected);
  };

  if (Platform.OS === 'android') {
    return (
      <DateTimePicker
        testID={`${testID}-native`}
        value={value}
        mode={mode}
        display="default"
        maximumDate={maximumDate}
        onChange={handleNativeChange}
      />
    );
  }

  const confirmWebValue = () => {
    const next = new Date(draft);
    if (mode === 'date') {
      const year = Number(parts.year);
      const month = Math.min(12, Math.max(1, Number(parts.month)));
      const day = Math.min(31, Math.max(1, Number(parts.day)));
      next.setFullYear(year, month - 1, day);
    } else {
      next.setHours(
        Math.min(23, Math.max(0, Number(parts.hour))),
        Math.min(59, Math.max(0, Number(parts.minute))),
        0,
        0,
      );
    }
    onConfirm(maximumDate && next > maximumDate ? maximumDate : next);
  };

  const renderWebFields = () => {
    const fields = mode === 'date'
      ? ([['day', 'DD', 2], ['month', 'MM', 2], ['year', 'YYYY', 4]] as const)
      : ([['hour', 'HH', 2], ['minute', 'MM', 2]] as const);
    return (
      <View style={styles.fieldRow}>
        {fields.map(([key, label, maxLength]) => (
          <View key={key} style={styles.fieldGroup}>
            <Text style={styles.fieldLabel}>{label}</Text>
            <TextInput
              testID={`${testID}-${key}-input`}
              style={styles.fieldInput}
              value={parts[key]}
              onChangeText={(text) => setParts((current) => ({ ...current, [key]: text.replace(/\D/g, '') }))}
              keyboardType="number-pad"
              maxLength={maxLength}
              selectTextOnFocus
            />
          </View>
        ))}
      </View>
    );
  };

  return (
    <Modal visible transparent animationType="fade" onRequestClose={onCancel}>
      <View testID={`${testID}-modal`} style={styles.overlay}>
        <View style={styles.dialog}>
          <Text testID={`${testID}-title`} style={styles.title}>{title}</Text>
          {Platform.OS === 'web' ? renderWebFields() : (
            <DateTimePicker
              testID={`${testID}-native`}
              value={draft}
              mode={mode}
              display="spinner"
              maximumDate={maximumDate}
              onChange={handleNativeChange}
            />
          )}
          <View style={styles.actions}>
            <TouchableOpacity testID={`${testID}-cancel`} style={styles.cancelButton} onPress={onCancel}>
              <Text style={styles.cancelText}>{cancelLabel}</Text>
            </TouchableOpacity>
            <TouchableOpacity
              testID={`${testID}-confirm`}
              style={styles.confirmButton}
              onPress={Platform.OS === 'web' ? confirmWebValue : () => onConfirm(draft)}
            >
              <Text style={styles.confirmText}>{confirmLabel}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, justifyContent: 'center', padding: spacing.xl, backgroundColor: 'rgba(43,29,20,0.38)' },
  dialog: { width: '100%', maxWidth: 420, alignSelf: 'center', borderRadius: radius.xl, padding: spacing.xl, backgroundColor: colors.card },
  title: { fontSize: font.xl, lineHeight: 28, fontWeight: '800', color: colors.text },
  fieldRow: { flexDirection: 'row', gap: spacing.sm, marginTop: spacing.xl },
  fieldGroup: { flex: 1, minWidth: 0 },
  fieldLabel: { textAlign: 'center', color: colors.textMuted, fontSize: font.sm, fontWeight: '700', marginBottom: spacing.xs },
  fieldInput: { minHeight: 54, borderRadius: radius.md, backgroundColor: colors.surfaceTertiary, color: colors.text, fontSize: font.xl, fontWeight: '700', textAlign: 'center', paddingHorizontal: spacing.sm },
  actions: { flexDirection: 'row', gap: spacing.md, marginTop: spacing.xl },
  cancelButton: { flex: 1, minHeight: 48, alignItems: 'center', justifyContent: 'center', borderRadius: radius.pill, backgroundColor: colors.surfaceTertiary },
  confirmButton: { flex: 1, minHeight: 48, alignItems: 'center', justifyContent: 'center', borderRadius: radius.pill, backgroundColor: colors.brand },
  cancelText: { color: colors.textSecondary, fontSize: font.base, fontWeight: '700' },
  confirmText: { color: colors.onBrand, fontSize: font.base, fontWeight: '800' },
});
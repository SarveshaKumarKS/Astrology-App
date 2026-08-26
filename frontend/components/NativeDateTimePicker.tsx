import React, { useEffect, useMemo, useState } from 'react';
import { Modal, StyleSheet, Text, TouchableOpacity, View, useWindowDimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, font, radius, spacing, shadow } from '../lib/theme';

interface Props {
  visible: boolean;
  mode: 'date' | 'time';
  value: Date;
  title: string;
  cancelLabel: string;
  confirmLabel: string;
  testID: string;
  language?: 'tamil' | 'english';
  maximumDate?: Date;
  onCancel: () => void;
  onConfirm: (value: Date) => void;
}

const pad = (value: number) => String(value).padStart(2, '0');
const dateKey = (value: Date) => `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())}`;
const sameDay = (left: Date, right: Date) => dateKey(left) === dateKey(right);

export default function NativeDateTimePicker({
  visible,
  mode,
  value,
  title,
  cancelLabel,
  confirmLabel,
  testID,
  language = 'english',
  maximumDate,
  onCancel,
  onConfirm,
}: Props) {
  const { width } = useWindowDimensions();
  const [draft, setDraft] = useState(value);
  const [month, setMonth] = useState(() => new Date(value.getFullYear(), value.getMonth(), 1));
  const [hour, setHour] = useState(12);
  const [minute, setMinute] = useState(0);
  const [period, setPeriod] = useState<'AM' | 'PM'>('PM');
  const locale = language === 'tamil' ? 'ta-IN' : 'en-US';
  const compact = width < 360;

  useEffect(() => {
    if (!visible) return;
    setDraft(new Date(value));
    setMonth(new Date(value.getFullYear(), value.getMonth(), 1));
    const hours = value.getHours();
    setHour(hours % 12 || 12);
    setMinute(value.getMinutes());
    setPeriod(hours >= 12 ? 'PM' : 'AM');
  }, [value, visible]);

  const calendarDays = useMemo(() => {
    const firstWeekday = month.getDay();
    const daysInMonth = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
    return Array.from({ length: 42 }, (_, index) => {
      const day = index - firstWeekday + 1;
      return day >= 1 && day <= daysInMonth
        ? new Date(month.getFullYear(), month.getMonth(), day)
        : null;
    });
  }, [month]);

  if (!visible) return null;

  const updateClock = (nextHour: number, nextMinute: number, nextPeriod: 'AM' | 'PM') => {
    setHour(nextHour);
    setMinute(nextMinute);
    setPeriod(nextPeriod);
  };

  const confirm = () => {
    const next = new Date(draft);
    if (mode === 'time') {
      const hours24 = (hour % 12) + (period === 'PM' ? 12 : 0);
      next.setHours(hours24, minute, 0, 0);
    }
    onConfirm(next);
  };

  const renderCalendar = () => {
    const weekLabels = language === 'tamil'
      ? ['ஞா', 'தி', 'செ', 'பு', 'வி', 'வெ', 'ச']
      : ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
    const nextMonth = new Date(month.getFullYear(), month.getMonth() + 1, 1);
    const nextDisabled = maximumDate
      ? nextMonth > new Date(maximumDate.getFullYear(), maximumDate.getMonth(), 1)
      : false;

    return (
      <View testID={`${testID}-calendar`} style={styles.calendar}>
        <View style={styles.monthHeader}>
          <TouchableOpacity
            testID={`${testID}-previous-month`}
            accessibilityLabel="Previous month"
            style={styles.iconButton}
            onPress={() => setMonth((current) => new Date(current.getFullYear(), current.getMonth() - 1, 1))}
          >
            <Ionicons name="chevron-back" size={22} color={colors.brandStrong} />
          </TouchableOpacity>
          <Text testID={`${testID}-month-label`} style={styles.monthLabel} numberOfLines={1}>
            {month.toLocaleDateString(locale, { month: 'long', year: 'numeric' })}
          </Text>
          <TouchableOpacity
            testID={`${testID}-next-month`}
            accessibilityLabel="Next month"
            style={[styles.iconButton, nextDisabled && styles.disabled]}
            disabled={nextDisabled}
            onPress={() => setMonth(nextMonth)}
          >
            <Ionicons name="chevron-forward" size={22} color={colors.brandStrong} />
          </TouchableOpacity>
        </View>

        <View style={styles.weekRow}>
          {weekLabels.map((label, index) => (
            <Text key={`${label}-${index}`} style={styles.weekLabel}>{label}</Text>
          ))}
        </View>

        <View style={styles.daysGrid}>
          {calendarDays.map((day, index) => {
            if (!day) return <View key={`blank-${index}`} style={styles.dayCell} />;
            const selected = sameDay(day, draft);
            const disabled = !!maximumDate && day > maximumDate;
            const today = sameDay(day, new Date());
            return (
              <TouchableOpacity
                key={dateKey(day)}
                testID={`${testID}-day-${dateKey(day)}`}
                accessibilityLabel={day.toLocaleDateString(locale)}
                disabled={disabled}
                style={[styles.dayCell, selected && styles.daySelected, today && !selected && styles.dayToday]}
                onPress={() => setDraft((current) => {
                  const next = new Date(current);
                  next.setFullYear(day.getFullYear(), day.getMonth(), day.getDate());
                  return next;
                })}
              >
                <Text style={[styles.dayText, selected && styles.dayTextSelected, disabled && styles.dayTextDisabled]}>
                  {day.getDate()}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    );
  };

  const Stepper = ({
    label,
    valueText,
    onDecrease,
    onIncrease,
    id,
  }: {
    label: string;
    valueText: string;
    onDecrease: () => void;
    onIncrease: () => void;
    id: string;
  }) => (
    <View style={styles.stepper}>
      <Text style={styles.stepperLabel}>{label}</Text>
      <TouchableOpacity testID={`${testID}-${id}-increase`} style={styles.stepButton} onPress={onIncrease}>
        <Ionicons name="chevron-up" size={24} color={colors.brandStrong} />
      </TouchableOpacity>
      <View style={styles.timeValueBox}>
        <Text testID={`${testID}-${id}-value`} style={styles.timeValue}>{valueText}</Text>
      </View>
      <TouchableOpacity testID={`${testID}-${id}-decrease`} style={styles.stepButton} onPress={onDecrease}>
        <Ionicons name="chevron-down" size={24} color={colors.brandStrong} />
      </TouchableOpacity>
    </View>
  );

  const renderClock = () => (
    <View testID={`${testID}-clock`} style={styles.clock}>
      <View style={styles.clockBadge}>
        <Ionicons name="time-outline" size={20} color={colors.brandStrong} />
        <Text testID={`${testID}-clock-display`} style={styles.clockDisplay}>
          {pad(hour)}:{pad(minute)} {period}
        </Text>
      </View>

      <View style={styles.clockControls}>
        <Stepper
          id="hour"
          label={language === 'tamil' ? 'மணி' : 'Hour'}
          valueText={pad(hour)}
          onIncrease={() => updateClock(hour === 12 ? 1 : hour + 1, minute, period)}
          onDecrease={() => updateClock(hour === 1 ? 12 : hour - 1, minute, period)}
        />
        <Text style={styles.colon}>:</Text>
        <Stepper
          id="minute"
          label={language === 'tamil' ? 'நிமிடம்' : 'Minute'}
          valueText={pad(minute)}
          onIncrease={() => updateClock(hour, (minute + 1) % 60, period)}
          onDecrease={() => updateClock(hour, (minute + 59) % 60, period)}
        />
        <View style={styles.periodGroup}>
          <Text style={styles.stepperLabel}>{language === 'tamil' ? 'காலம்' : 'Period'}</Text>
          {(['AM', 'PM'] as const).map((item) => (
            <TouchableOpacity
              key={item}
              testID={`${testID}-period-${item.toLowerCase()}`}
              style={[styles.periodButton, period === item && styles.periodSelected]}
              onPress={() => updateClock(hour, minute, item)}
            >
              <Text style={[styles.periodText, period === item && styles.periodTextSelected]}>{item}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.quickMinutes}>
        {[0, 15, 30, 45].map((item) => (
          <TouchableOpacity
            key={item}
            testID={`${testID}-quick-minute-${item}`}
            style={[styles.quickMinute, minute === item && styles.quickMinuteSelected]}
            onPress={() => updateClock(hour, item, period)}
          >
            <Text style={[styles.quickMinuteText, minute === item && styles.quickMinuteTextSelected]}>:{pad(item)}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  return (
    <Modal visible transparent animationType="none" onRequestClose={onCancel} statusBarTranslucent>
      <View testID={`${testID}-modal`} style={styles.overlay}>
        <View style={[styles.dialog, compact && styles.dialogCompact]}>
          <View style={styles.titleRow}>
            <View style={styles.titleIcon}>
              <Ionicons name={mode === 'date' ? 'calendar-outline' : 'time-outline'} size={20} color={colors.brandStrong} />
            </View>
            <Text testID={`${testID}-title`} style={styles.title} numberOfLines={2}>{title}</Text>
          </View>

          {mode === 'date' ? renderCalendar() : renderClock()}

          <View style={styles.actions}>
            <TouchableOpacity testID={`${testID}-cancel`} style={styles.cancelButton} onPress={onCancel}>
              <Text style={styles.cancelText}>{cancelLabel}</Text>
            </TouchableOpacity>
            <TouchableOpacity testID={`${testID}-confirm`} style={styles.confirmButton} onPress={confirm}>
              <Text style={styles.confirmText}>{confirmLabel}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, justifyContent: 'center', padding: 18, backgroundColor: 'rgba(43,29,20,0.48)' },
  dialog: { width: '100%', maxWidth: 420, alignSelf: 'center', borderRadius: 28, padding: spacing.lg, backgroundColor: colors.card, ...shadow.card },
  dialogCompact: { padding: spacing.md },
  titleRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.md },
  titleIcon: { width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.brandSoft },
  title: { flex: 1, minWidth: 0, fontSize: font.xl, lineHeight: 29, fontWeight: '800', color: colors.text },
  calendar: { width: '100%' },
  monthHeader: { minHeight: 48, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  iconButton: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center', borderRadius: 22, backgroundColor: colors.brandSoft },
  disabled: { opacity: 0.3 },
  monthLabel: { flex: 1, textAlign: 'center', color: colors.text, fontSize: font.lg, fontWeight: '800', textTransform: 'capitalize' },
  weekRow: { flexDirection: 'row', marginTop: spacing.sm },
  weekLabel: { width: '14.285%', textAlign: 'center', color: colors.textMuted, fontSize: font.sm, lineHeight: 28, fontWeight: '700' },
  daysGrid: { flexDirection: 'row', flexWrap: 'wrap' },
  dayCell: { width: '14.285%', minHeight: 42, alignItems: 'center', justifyContent: 'center', borderRadius: 21 },
  daySelected: { backgroundColor: colors.brand },
  dayToday: { borderWidth: 1.5, borderColor: colors.brand },
  dayText: { color: colors.text, fontSize: font.base, fontWeight: '600' },
  dayTextSelected: { color: colors.onBrand, fontWeight: '800' },
  dayTextDisabled: { color: colors.textMuted, opacity: 0.35 },
  clock: { width: '100%', paddingTop: spacing.xs },
  clockBadge: { minHeight: 58, borderRadius: radius.lg, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.sm, backgroundColor: colors.brandSoft },
  clockDisplay: { color: colors.brandStrong, fontSize: 30, lineHeight: 38, fontWeight: '800', fontVariant: ['tabular-nums'] },
  clockControls: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.sm, marginTop: spacing.lg },
  stepper: { width: 84, alignItems: 'center' },
  stepperLabel: { minHeight: 20, color: colors.textMuted, fontSize: font.sm, fontWeight: '700', marginBottom: spacing.xs },
  stepButton: { width: 52, height: 44, alignItems: 'center', justifyContent: 'center', borderRadius: radius.md, backgroundColor: colors.surfaceTertiary },
  timeValueBox: { width: 72, height: 58, alignItems: 'center', justifyContent: 'center', marginVertical: spacing.xs, borderRadius: radius.md, borderWidth: 2, borderColor: colors.brand, backgroundColor: colors.card },
  timeValue: { color: colors.text, fontSize: 28, fontWeight: '800', fontVariant: ['tabular-nums'] },
  colon: { color: colors.brandStrong, fontSize: 30, fontWeight: '800', marginTop: 22 },
  periodGroup: { width: 70, alignItems: 'center' },
  periodButton: { width: 64, minHeight: 44, alignItems: 'center', justifyContent: 'center', borderRadius: radius.md, marginBottom: spacing.sm, backgroundColor: colors.surfaceTertiary },
  periodSelected: { backgroundColor: colors.brand },
  periodText: { color: colors.textSecondary, fontSize: font.base, fontWeight: '800' },
  periodTextSelected: { color: colors.onBrand },
  quickMinutes: { flexDirection: 'row', gap: spacing.sm, justifyContent: 'center', marginTop: spacing.md },
  quickMinute: { minWidth: 58, minHeight: 44, alignItems: 'center', justifyContent: 'center', borderRadius: radius.pill, backgroundColor: colors.surfaceTertiary },
  quickMinuteSelected: { backgroundColor: colors.brandSoft, borderWidth: 1, borderColor: colors.brand },
  quickMinuteText: { color: colors.textSecondary, fontSize: font.sm, fontWeight: '700' },
  quickMinuteTextSelected: { color: colors.brandStrong },
  actions: { flexDirection: 'row', gap: spacing.md, marginTop: spacing.lg },
  cancelButton: { flex: 1, minHeight: 50, alignItems: 'center', justifyContent: 'center', borderRadius: radius.pill, backgroundColor: colors.surfaceTertiary },
  confirmButton: { flex: 1, minHeight: 50, alignItems: 'center', justifyContent: 'center', borderRadius: radius.pill, backgroundColor: colors.brand },
  cancelText: { color: colors.textSecondary, fontSize: font.base, fontWeight: '700' },
  confirmText: { color: colors.onBrand, fontSize: font.base, fontWeight: '800' },
});
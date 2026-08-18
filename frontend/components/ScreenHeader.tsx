import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, font } from '../lib/theme';

interface Props {
  title: string;
  onBack?: () => void;
  right?: React.ReactNode;
}

/**
 * Clean, light, iOS-style header: white surface, espresso title,
 * chevron back, optional right-side actions.
 */
export default function ScreenHeader({ title, onBack, right }: Props) {
  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      <View testID="screen-header" style={styles.container}>
        <View style={styles.leftSide}>
          {onBack ? (
            <TouchableOpacity testID="screen-header-back-button" onPress={onBack} style={styles.iconBtn} hitSlop={8}>
              <Ionicons name="chevron-back" size={26} color={colors.brandStrong} />
            </TouchableOpacity>
          ) : null}
        </View>

        <Text testID="screen-header-title" style={styles.title} numberOfLines={1}>
          {title}
        </Text>

        {right ? <View style={styles.rightSide}>{right}</View> : null}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    backgroundColor: colors.bg,
  },
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    backgroundColor: colors.bg,
  },
  leftSide: {
    width: 44,
    flexDirection: 'row',
    alignItems: 'center',
  },
  rightSide: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    marginLeft: spacing.xs,
  },
  iconBtn: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    flex: 1,
    textAlign: 'left',
    fontSize: font.xl,
    fontWeight: '700',
    color: colors.text,
    marginLeft: spacing.xs,
  },
});

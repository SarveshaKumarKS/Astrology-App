import { Platform } from 'react-native';

// Central design tokens — warm, light & airy, Apple-minimalist with saffron accents.
// Derived from /app/design_guidelines.json.

export const colors = {
  // Surfaces
  bg: '#FCFAF8',            // app background (alabaster off-white)
  card: '#FFFFFF',          // cards / list rows
  surfaceTertiary: '#F4EFE6', // input backgrounds, subtle fills
  inverse: '#2B1D14',       // espresso (rare, for contrast blocks)

  // Text
  text: '#1A1A1A',          // primary text (espresso-black)
  textSecondary: '#6B6259', // secondary/label text
  textMuted: '#9A9187',     // captions / placeholders

  // Brand (saffron / gold)
  brand: '#D97706',
  brandStrong: '#C26500',
  brandSoft: '#FCE8D3',     // tinted icon containers / chips
  onBrand: '#FFFFFF',

  // Feedback
  success: '#2E7D32',
  warning: '#ED6C02',
  error: '#D32F2F',

  // Lines
  border: '#E8E2D9',
  borderStrong: '#D6C9B3',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
  xxxl: 48,
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 22,
  pill: 999,
} as const;

export const font = {
  sm: 12,
  base: 14,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 30,
} as const;

// Extra line-height so Tamil script stays legible & airy.
export const lineHeights = {
  body: 22,
  title: 34,
};

// Soft, Apple-clean elevation (tier 1). Subtle, not heavy.
export const shadow = {
  card: Platform.select({
    web: { boxShadow: '0 6px 16px rgba(138, 107, 63, 0.08)' },
    default: {
      shadowColor: '#8A6B3F',
      shadowOffset: { width: 0, height: 6 },
      shadowOpacity: 0.08,
      shadowRadius: 16,
      elevation: 3,
    },
  })!,
  soft: Platform.select({
    web: { boxShadow: '0 2px 8px rgba(138, 107, 63, 0.06)' },
    default: {
      shadowColor: '#8A6B3F',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.06,
      shadowRadius: 8,
      elevation: 2,
    },
  })!,
} as const;

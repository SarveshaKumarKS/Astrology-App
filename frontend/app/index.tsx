import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  StatusBar,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Constants from 'expo-constants';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { colors, spacing, radius, font, shadow, lineHeights } from '../lib/theme';
import { useAuth } from '../lib/auth';

export default function HomePage() {
  const { user } = useAuth();
  const [language, setLanguage] = useState<'tamil' | 'english'>('tamil');

  const appVersion =
    (Constants.expoConfig?.version as string) ||
    ((Constants as any).manifest?.version as string) ||
    '1.0.0';

  const getText = (tamil: string, english: string) =>
    language === 'tamil' ? tamil : english;

  const services: Array<{
    title: string;
    subtitle: string;
    icon: 'planet-outline' | 'heart-outline' | 'bookmark-outline' | 'calendar-outline';
    route: '/horoscope' | '/compatibility' | '/profiles' | '/panchangam';
  }> = [
    {
      title: getText('ஜாதகம் கணித்தல்', 'Generate Horoscope'),
      subtitle: getText('தனிப்பட்ட ஜாதகம் உருவாக்குதல்', 'Create a personal chart'),
      icon: 'planet-outline' as const,
      route: '/horoscope',
    },
    {
      title: getText('திருமணப் பொருத்தம்', 'Marriage Compatibility'),
      subtitle: getText('திருமணப் பொருத்தம் பார்த்தல்', 'Check marriage matching'),
      icon: 'heart-outline' as const,
      route: '/compatibility',
    },
    {
      title: getText('சேமிக்கப்பட்ட விவரங்கள்', 'Saved Charts'),
      subtitle: getText('ஜாதகங்களை நிர்வகித்தல்', 'Manage saved horoscopes'),
      icon: 'bookmark-outline' as const,
      route: '/profiles',
    },
    {
      title: getText('தினசரி பஞ்சாங்கம்', 'Daily Panchangam'),
      subtitle: getText('இன்றைய பஞ்சாங்க விவரங்கள்', "Today's panchangam"),
      icon: 'calendar-outline' as const,
      route: '/panchangam',
    },
  ];

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.bg} />

      {/* Top bar */}
      <View style={styles.topBar}>
        <TouchableOpacity
          testID="home-language-button"
          style={styles.langChip}
          onPress={() => setLanguage(language === 'tamil' ? 'english' : 'tamil')}
        >
          <Ionicons name="language-outline" size={16} color={colors.brandStrong} />
          <Text style={styles.langChipText}>{language === 'tamil' ? 'தமிழ்' : 'EN'}</Text>
        </TouchableOpacity>

        <TouchableOpacity testID="home-account-button" style={styles.accountBtn} onPress={() => router.push('/account')}>
          {user?.picture ? (
            <View style={styles.avatarRing}>
              <Ionicons name="person" size={18} color={colors.brandStrong} />
            </View>
          ) : (
            <Ionicons name="person-circle-outline" size={30} color={colors.brandStrong} />
          )}
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        contentContainerStyle={{ paddingBottom: spacing.xxxl }}
        showsVerticalScrollIndicator={false}
      >
        {/* Hero */}
        <View style={styles.hero}>
          <View style={styles.motif}>
            <Ionicons name="sunny" size={30} color={colors.brand} />
          </View>
          <Text style={styles.heroTitle}>
            {getText('தமிழ் ஜோதிடம்', 'Tamil Astrology')}
          </Text>
          <Text style={styles.heroSubtitle}>
            {getText('பாரம்பரிய ஜோதிட சேவை', 'Traditional astrology, refined')}
          </Text>
        </View>

        {/* Services */}
        <Text style={styles.sectionLabel}>{getText('சேவைகள்', 'Services')}</Text>

        {services.map((s) => (
          <TouchableOpacity
            key={s.route}
            testID={`home-service-${String(s.route).replace('/', '')}`}
            style={styles.card}
            activeOpacity={0.85}
            onPress={() => router.push(s.route)}
          >
            <View style={styles.iconWrap}>
              <Ionicons name={s.icon} size={24} color={colors.brandStrong} />
            </View>
            <View style={styles.cardBody}>
              <Text style={styles.cardTitle}>{s.title}</Text>
              <Text style={styles.cardSubtitle}>{s.subtitle}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={colors.textMuted} />
          </TouchableOpacity>
        ))}

        {/* About */}
        <View style={styles.aboutCard}>
          <Text style={styles.aboutTitle}>{getText('பற்றி', 'About')}</Text>
          <Text style={styles.aboutText}>
            {getText(
              'வாக்கிய மற்றும் திருக்கணித முறைகளில் ஜாதகம் கணித்தல், திருமணப் பொருத்தம் மற்றும் பஞ்சாங்கம் ஆகிய சேவைகளை வழங்கும் பாரம்பரிய தமிழ் ஜோதிட செயலி.',
              'A traditional Tamil astrology app offering horoscope generation, marriage compatibility and panchangam in both Vakkiam and Thirukkanitham systems.'
            )}
          </Text>
        </View>

        <View testID="app-version-label" style={styles.versionWrap}>
          <Text style={styles.versionText}>{getText('பதிப்பு', 'Version')} {appVersion}</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  langChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.brandSoft,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
    gap: 6,
  },
  langChipText: { color: colors.brandStrong, fontSize: font.sm, fontWeight: '700' },
  accountBtn: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarRing: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: colors.brandSoft,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: { flex: 1, paddingHorizontal: spacing.lg },
  hero: {
    alignItems: 'center',
    paddingTop: spacing.lg,
    paddingBottom: spacing.xl,
  },
  motif: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.brandSoft,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  heroTitle: {
    fontSize: font.xxxl,
    fontWeight: '800',
    color: colors.text,
    letterSpacing: 0.2,
    lineHeight: lineHeights.title,
    textAlign: 'center',
  },
  heroSubtitle: {
    fontSize: font.base,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  sectionLabel: {
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
    flexDirection: 'row',
    alignItems: 'center',
    ...shadow.card,
  },
  iconWrap: {
    width: 52,
    height: 52,
    borderRadius: radius.md,
    backgroundColor: colors.brandSoft,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.lg,
  },
  cardBody: { flex: 1 },
  cardTitle: {
    fontSize: font.lg,
    fontWeight: '700',
    color: colors.text,
    marginBottom: 2,
  },
  cardSubtitle: { fontSize: font.base, color: colors.textSecondary },
  aboutCard: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.xl,
    marginTop: spacing.lg,
    ...shadow.soft,
  },
  aboutTitle: {
    fontSize: font.lg,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  aboutText: {
    fontSize: font.base,
    color: colors.textSecondary,
    lineHeight: lineHeights.body,
  },
  versionWrap: {
    alignItems: 'center',
    marginTop: spacing.xl,
    paddingVertical: spacing.sm,
  },
  versionText: {
    fontSize: font.sm,
    color: colors.textMuted,
  },
});

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

export type AppLanguage = 'tamil' | 'english';

interface LanguageContextValue {
  language: AppLanguage;
  setLanguage: (language: AppLanguage) => void;
  toggleLanguage: () => void;
  getText: (tamil: string, english: string) => string;
}

const STORAGE_KEY = 'app_language';
const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<AppLanguage>('tamil');

  useEffect(() => {
    if (Platform.OS === 'web') return;
    SecureStore.getItemAsync(STORAGE_KEY)
      .then((saved) => {
        if (saved === 'tamil' || saved === 'english') setLanguageState(saved);
      })
      .catch(() => undefined);
  }, []);

  const setLanguage = useCallback((next: AppLanguage) => {
    setLanguageState(next);
    if (Platform.OS !== 'web') {
      SecureStore.setItemAsync(STORAGE_KEY, next).catch(() => undefined);
    }
  }, []);

  const toggleLanguage = useCallback(() => {
    setLanguage(language === 'tamil' ? 'english' : 'tamil');
  }, [language, setLanguage]);

  const getText = useCallback(
    (tamil: string, english: string) => (language === 'tamil' ? tamil : english),
    [language],
  );

  const value = useMemo(
    () => ({ language, setLanguage, toggleLanguage, getText }),
    [language, setLanguage, toggleLanguage, getText],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage(): LanguageContextValue {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('useLanguage must be used within LanguageProvider');
  return context;
}
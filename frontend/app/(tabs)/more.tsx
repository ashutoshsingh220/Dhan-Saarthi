import React, { useEffect, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";
import { router } from "expo-router";
import { Button } from "@/components/Form";
import { Screen } from "@/components/Screen";
import { colors } from "@/constants/theme";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/i18n/LanguageContext";
import { api } from "@/services/api";
import type { EducationLevel, ExplanationLevel, FinancialKnowledgeLevel, OccupationStatus, ProfileResponse } from "@/types/api";

import { useAccessibility } from "@/context/AccessibilityContext";
import type { AccessibilityProfile, TextSizePreference } from "@/services/accessibility/accessibilityTypes";
import { BrandLogo } from "@/components/branding/BrandLogo";
import { DomainIconBadge, DomainId } from "@/components/branding/DomainIconBadge";


export default function MoreTab() {
  const { user, signOut, token } = useAuth();
  const { language, setLanguage, voiceAssistanceEnabled, setVoiceAssistanceEnabled, t } = useLanguage();
  const {
    accessibilityModeEnabled,
    accessibilityProfile,
    textSizePreference,
    highContrastEnabled,
    reduceMotionEnabled,
    simplifiedInterfaceEnabled,
    voiceNavigationEnabled,
    autoSpeakImportantResults,
    sequentialNavigationEnabled,
    toggleAccessibilityMode,
    updatePreferences,
  } = useAccessibility();

  // --- Personalization state ---

  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [personAge, setPersonAge] = useState("");
  const [personMonthlySavings, setPersonMonthlySavings] = useState("");
  const [personTotalSavings, setPersonTotalSavings] = useState("");
  const [personEdu, setPersonEdu] = useState<EducationLevel | null>(null);
  const [personKnowledge, setPersonKnowledge] = useState<FinancialKnowledgeLevel | null>(null);
  const [personExplain, setPersonExplain] = useState<ExplanationLevel | null>(null);
  const [personOcc, setPersonOcc] = useState<OccupationStatus | null>(null);
  const [personSaving, setPersonSaving] = useState(false);
  const [personSaved, setPersonSaved] = useState(false);
  const [personError, setPersonError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      api.getProfile(token).then((p) => {
        setProfile(p);
        setPersonAge(p.age?.toString() || "");
        setPersonMonthlySavings(p.monthly_savings?.toString() || p.savings?.toString() || "");
        setPersonTotalSavings(p.total_savings?.toString() || "");
        setPersonEdu(p.education_level || null);
        setPersonKnowledge(p.financial_knowledge_level || null);
        setPersonExplain(p.preferred_explanation_level || null);
        setPersonOcc(p.occupation_status || null);
      }).catch(() => { /* profile may not exist yet */ });
    }
  }, [token]);

  const savePersonalization = async () => {
    if (!token || !profile) return;
    setPersonSaving(true);
    setPersonSaved(false);
    setPersonError(null);
    try {
      const ageNum = personAge ? Number(personAge) : profile.age;
      const mSavings = personMonthlySavings ? Number(personMonthlySavings) : Number(profile.monthly_savings || profile.savings || 0);
      const tSavings = personTotalSavings ? Number(personTotalSavings) : Number(profile.total_savings || 0);

      const updated = await api.saveProfile(
        {
          ...profile,
          age: ageNum,
          monthly_income: Number(profile.monthly_income),
          monthly_expenses: Number(profile.monthly_expenses),
          monthly_savings: mSavings,
          total_savings: tSavings,
          savings: mSavings,
          date_of_birth: null,
          education_level: personEdu,
          financial_knowledge_level: personKnowledge,
          preferred_explanation_level: personExplain,
          occupation_status: personOcc,
        },
        token
      );
      setProfile(updated);
      setPersonSaved(true);
    } catch (e) {
      setPersonError(e instanceof Error ? e.message : "Failed to save personalization preferences");
    } finally {
      setPersonSaving(false);
    }
  };


  const handleSignOut = async () => {
    await signOut();
    router.replace("/welcome");
  };

  const handleLanguageChange = async (lang: "en" | "hi") => {
    await setLanguage(lang);
    // Sync backend profile preferred language if user is logged in
    if (user && token && profile) {
      try {
        const fullLang = lang === "hi" ? "Hindi" : "English";
        await api.saveProfile(
          {
            ...profile,
            monthly_income: Number(profile.monthly_income),
            monthly_expenses: Number(profile.monthly_expenses),
            savings: Number(profile.savings),
            preferred_language: fullLang,
          },
          token
        );
      } catch (err) {
        console.warn("Failed to sync backend profile language", err);
      }
    }
  };

  const domainLinks: { title: string; domainId: DomainId; path: string; sub: string }[] = [
    { title: "Financial Twin Detail", domainId: "twin", path: "/twin-detail", sub: "View complete Twin score & profile" },
    { title: "Financial Guidance", domainId: "recommendations", path: "/domain/recommendations", sub: "Surplus allocation & priority guidance" },
    { title: "AI Saarthi", domainId: "saarthi", path: "/(tabs)/saarthi", sub: "Voice & text companion" },
    { title: "Financial Literacy", domainId: "learn", path: "/(tabs)/learn", sub: "Personalized learning modules" },
    { title: "Smart Planning", domainId: "planning", path: "/domain/planning", sub: "Goals & budget tracker" },
    { title: "Market Intelligence", domainId: "market", path: "/domain/market-intelligence", sub: "Market Pulse, Nifty, Sensex, Gold & USD/INR" },
    { title: "Government Support", domainId: "schemes", path: "/domain/schemes", sub: "Kisan & Small Business schemes" },
    { title: "Scam Shield", domainId: "scam", path: "/domain/scam-shield", sub: "Fraud detection & QR verify" },
  ];





  return (
    <Screen>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 40 }}>
        <View style={styles.header}>
          <Text style={styles.title}>{t("more.title")}</Text>
          <Text style={styles.subtitle}>Manage language, accessibility, and domain features</Text>
        </View>

        {/* USER PROFILE CARD */}
        {user && (
          <View style={styles.userCard}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>{user.full_name.charAt(0)}</Text>
            </View>
            <View style={styles.userInfo}>
              <Text style={styles.userName}>{user.full_name}</Text>
              <Text style={styles.userEmail}>{user.email}</Text>
              <Text style={styles.userMeta}>
                {t("more.language")}: {language === "hi" ? "हिन्दी (Hindi)" : "English"}
              </Text>
            </View>
          </View>
        )}

        {/* LANGUAGE SELECTOR SECTION */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🌐 {t("more.language")}</Text>
          <Text style={styles.cardSubtitle}>Select your preferred interface language:</Text>
          <View style={styles.langContainer}>
            <TouchableOpacity
              style={[styles.langChip, language === "en" && styles.langChipActive]}
              onPress={() => handleLanguageChange("en")}
              accessibilityRole="button"
              accessibilityLabel="Select English Language"
            >
              <Text style={[styles.langText, language === "en" && styles.langTextActive]}>English</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.langChip, language === "hi" && styles.langChipActive]}
              onPress={() => handleLanguageChange("hi")}
              accessibilityRole="button"
              accessibilityLabel="Select Hindi Language (हिन्दी)"
            >
              <Text style={[styles.langText, language === "hi" && styles.langTextActive]}>हिन्दी (Hindi)</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* VOICE ASSISTANCE & ACCESSIBILITY SECTION */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🎙️ {t("more.voice_assistance")}</Text>
          <Text style={styles.cardSubtitle}>{t("more.voice_mode")}</Text>
          <View style={styles.voiceToggleRow}>
            <Text style={styles.voiceToggleLabel}>
              {voiceAssistanceEnabled ? t("more.enable_voice") : t("more.disable_voice")}
            </Text>
            <TouchableOpacity
              style={[styles.toggleBtn, voiceAssistanceEnabled ? styles.toggleBtnOn : styles.toggleBtnOff]}
              onPress={() => setVoiceAssistanceEnabled(!voiceAssistanceEnabled)}
              accessibilityRole="switch"
              accessibilityLabel="Voice Assistance Toggle"
              accessibilityState={{ checked: voiceAssistanceEnabled }}
            >
              <Text style={styles.toggleBtnText}>{voiceAssistanceEnabled ? "ON" : "OFF"}</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* PROMPT 12: VOICE & CONVERSATION SETTINGS CARD */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🗣️ {t("voice.title")}</Text>
          <Text style={styles.cardSubtitle}>Configure voice input language, speech speed, and safety rules</Text>

          <Text style={styles.fieldLabel}>{t("voice.input_language")}</Text>
          <View style={styles.langContainer}>
            <TouchableOpacity style={[styles.langChip, styles.langChipActive]}>
              <Text style={styles.langTextActive}>{t("voice.auto_detect")}</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.langChip}>
              <Text style={styles.langText}>English</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.langChip}>
              <Text style={styles.langText}>हिन्दी</Text>
            </TouchableOpacity>
          </View>

          <Text style={styles.fieldLabel}>{t("voice.speech_speed")}</Text>
          <View style={styles.langContainer}>
            <TouchableOpacity style={styles.langChip}><Text style={styles.langText}>0.85x</Text></TouchableOpacity>
            <TouchableOpacity style={[styles.langChip, styles.langChipActive]}><Text style={styles.langTextActive}>1.0x</Text></TouchableOpacity>
            <TouchableOpacity style={styles.langChip}><Text style={styles.langText}>1.15x</Text></TouchableOpacity>
          </View>

          <View style={[styles.voiceToggleRow, { marginTop: 12 }]}>
            <Text style={styles.voiceToggleLabel}>{t("voice.interrupt_ai")}</Text>
            <View style={[styles.toggleBtn, styles.toggleBtnOn]}><Text style={styles.toggleBtnText}>ON</Text></View>
          </View>

          <View style={[styles.voiceToggleRow, { marginTop: 8 }]}>
            <Text style={styles.voiceToggleLabel}>{t("voice.auto_send")}</Text>
            <View style={[styles.toggleBtn, styles.toggleBtnOff]}><Text style={styles.toggleBtnText}>OFF</Text></View>
          </View>
        </View>

        {/* PROMPT 13: ACCESSIBILITY & ASSISTANCE CARD */}
        <View style={styles.card}>

          <Text style={styles.cardTitle}>♿ {t("a11y.title")}</Text>
          <Text style={styles.cardSubtitle}>{t("a11y.subtitle")}</Text>

          {/* Master Accessibility Mode Toggle */}
          <View style={styles.voiceToggleRow}>
            <Text style={styles.voiceToggleLabel}>{t("a11y.mode_enabled")}</Text>
            <TouchableOpacity
              style={[styles.toggleBtn, accessibilityModeEnabled ? styles.toggleBtnOn : styles.toggleBtnOff]}
              onPress={() => toggleAccessibilityMode(!accessibilityModeEnabled)}
              accessibilityRole="switch"
              accessibilityLabel="Accessibility Mode Toggle"
              accessibilityState={{ checked: accessibilityModeEnabled }}
            >
              <Text style={styles.toggleBtnText}>{accessibilityModeEnabled ? "ON" : "OFF"}</Text>
            </TouchableOpacity>
          </View>

          {/* Accessibility Profile Selector */}
          <Text style={styles.fieldLabel}>{t("a11y.profile_label")}</Text>
          <View style={{ gap: 6, marginBottom: 12 }}>
            {(['STANDARD', 'VISUAL_ASSIST', 'VOICE_ASSIST', 'LOW_LITERACY', 'ELDERLY_FRIENDLY'] as AccessibilityProfile[]).map((prof) => (
              <TouchableOpacity
                key={prof}
                style={[styles.langChip, { width: '100%' }, accessibilityProfile === prof && styles.langChipActive]}
                onPress={() => updatePreferences({ accessibilityProfile: prof, accessibilityModeEnabled: prof !== 'STANDARD' })}
              >
                <Text style={accessibilityProfile === prof ? styles.langTextActive : styles.langText}>
                  {t(`a11y.profile_${prof}`)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Text Size / Scaling */}
          <Text style={styles.fieldLabel}>{t("a11y.text_size")}</Text>
          <View style={styles.langContainer}>
            {(['SMALL', 'STANDARD', 'LARGE', 'EXTRA_LARGE'] as TextSizePreference[]).map((sz) => (
              <TouchableOpacity
                key={sz}
                style={[styles.langChip, textSizePreference === sz && styles.langChipActive]}
                onPress={() => updatePreferences({ textSizePreference: sz })}
              >
                <Text style={textSizePreference === sz ? styles.langTextActive : styles.langText}>
                  {t(`a11y.size_${sz}`)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* High Contrast Toggle */}
          <View style={[styles.voiceToggleRow, { marginTop: 12 }]}>
            <Text style={styles.voiceToggleLabel}>{t("a11y.high_contrast")}</Text>
            <TouchableOpacity
              style={[styles.toggleBtn, highContrastEnabled ? styles.toggleBtnOn : styles.toggleBtnOff]}
              onPress={() => updatePreferences({ highContrastEnabled: !highContrastEnabled })}
            >
              <Text style={styles.toggleBtnText}>{highContrastEnabled ? "ON" : "OFF"}</Text>
            </TouchableOpacity>
          </View>

          {/* Reduce Motion Toggle */}
          <View style={[styles.voiceToggleRow, { marginTop: 8 }]}>
            <Text style={styles.voiceToggleLabel}>{t("a11y.reduce_motion")}</Text>
            <TouchableOpacity
              style={[styles.toggleBtn, reduceMotionEnabled ? styles.toggleBtnOn : styles.toggleBtnOff]}
              onPress={() => updatePreferences({ reduceMotionEnabled: !reduceMotionEnabled })}
            >
              <Text style={styles.toggleBtnText}>{reduceMotionEnabled ? "ON" : "OFF"}</Text>
            </TouchableOpacity>
          </View>

          {/* Guided Voice Navigation Toggle */}
          <View style={[styles.voiceToggleRow, { marginTop: 8 }]}>
            <Text style={styles.voiceToggleLabel}>{t("a11y.voice_nav")}</Text>
            <TouchableOpacity
              style={[styles.toggleBtn, voiceNavigationEnabled ? styles.toggleBtnOn : styles.toggleBtnOff]}
              onPress={() => updatePreferences({ voiceNavigationEnabled: !voiceNavigationEnabled })}
            >
              <Text style={styles.toggleBtnText}>{voiceNavigationEnabled ? "ON" : "OFF"}</Text>
            </TouchableOpacity>
          </View>

          {/* Sequential Presentation Toggle */}
          <View style={[styles.voiceToggleRow, { marginTop: 8 }]}>
            <Text style={styles.voiceToggleLabel}>{t("a11y.seq_nav")}</Text>
            <TouchableOpacity
              style={[styles.toggleBtn, sequentialNavigationEnabled ? styles.toggleBtnOn : styles.toggleBtnOff]}
              onPress={() => updatePreferences({ sequentialNavigationEnabled: !sequentialNavigationEnabled })}
            >
              <Text style={styles.toggleBtnText}>{sequentialNavigationEnabled ? "ON" : "OFF"}</Text>
            </TouchableOpacity>
          </View>
        </View>


        {/* PERSONALIZATION SETTINGS */}

        {profile && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>🎯 {t("personalization.title")}</Text>
            <Text style={styles.cardSubtitle}>{t("personalization.subtitle")}</Text>

            {/* Age */}
            <Text style={styles.fieldLabel}>Age</Text>
            <TextInput
              style={styles.textInput}
              value={personAge}
              onChangeText={setPersonAge}
              placeholder="e.g. 25"
              keyboardType="numeric"
              accessibilityLabel="Age"
              accessible
            />

            {/* Monthly Savings */}
            <Text style={styles.fieldLabel}>Monthly Savings (₹)</Text>
            <TextInput
              style={styles.textInput}
              value={personMonthlySavings}
              onChangeText={setPersonMonthlySavings}
              placeholder="e.g. 25000"
              keyboardType="numeric"
              accessibilityLabel="Monthly Savings"
              accessible
            />

            {/* Total Savings */}
            <Text style={styles.fieldLabel}>Total Accumulated Savings (₹)</Text>
            <TextInput
              style={styles.textInput}
              value={personTotalSavings}
              onChangeText={setPersonTotalSavings}
              placeholder="e.g. 300000"
              keyboardType="numeric"
              accessibilityLabel="Total Accumulated Savings"
              accessible
            />


            {/* Education Level */}
            <Text style={styles.fieldLabel}>{t("personalization.education_label")}</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 10 }}>
              {(["PRIMARY_OR_BELOW","SECONDARY","HIGHER_SECONDARY","DIPLOMA","UNDERGRADUATE","POSTGRADUATE","DOCTORATE","OTHER","PREFER_NOT_TO_SAY"] as EducationLevel[]).map((val) => (
                <Pressable
                  key={val}
                  onPress={() => setPersonEdu(val)}
                  accessibilityRole="button"
                  accessibilityLabel={t(`edu.${val}`)}
                  accessibilityState={{ selected: personEdu === val }}
                  style={[styles.chip, personEdu === val && styles.chipActive]}
                >
                  <Text style={[styles.chipText, personEdu === val && styles.chipTextActive]}>{t(`edu.${val}`)}</Text>
                  {personEdu === val && <Text style={styles.chipCheck}> ✓</Text>}
                </Pressable>
              ))}
            </ScrollView>

            {/* Financial Knowledge Level */}
            <Text style={styles.fieldLabel}>{t("personalization.knowledge_label")}</Text>
            <View style={styles.grid}>
              {(["BEGINNER","BASIC","INTERMEDIATE","ADVANCED"] as FinancialKnowledgeLevel[]).map((val) => (
                <Pressable
                  key={val}
                  onPress={() => setPersonKnowledge(val)}
                  accessibilityRole="button"
                  accessibilityLabel={`${t(`fk.${val}`)}: ${t(`fk.${val}_DESC`)}`}
                  accessibilityState={{ selected: personKnowledge === val }}
                  style={[styles.chip, personKnowledge === val && styles.chipActive]}
                >
                  <Text style={[styles.chipText, personKnowledge === val && styles.chipTextActive]}>{t(`fk.${val}`)}</Text>
                  {personKnowledge === val && <Text style={styles.chipCheck}> ✓</Text>}
                </Pressable>
              ))}
            </View>

            {/* Explanation Level */}
            <Text style={styles.fieldLabel}>{t("personalization.explanation_label")}</Text>
            <View style={styles.grid}>
              {(["SIMPLE","BALANCED","DETAILED"] as ExplanationLevel[]).map((val) => (
                <Pressable
                  key={val}
                  onPress={() => setPersonExplain(val)}
                  accessibilityRole="button"
                  accessibilityLabel={`${t(`exp.${val}`)}: ${t(`exp.${val}_DESC`)}`}
                  accessibilityState={{ selected: personExplain === val }}
                  style={[styles.chip, personExplain === val && styles.chipActive]}
                >
                  <Text style={[styles.chipText, personExplain === val && styles.chipTextActive]}>{t(`exp.${val}`)}</Text>
                  {personExplain === val && <Text style={styles.chipCheck}> ✓</Text>}
                </Pressable>
              ))}
            </View>

            {/* Occupation Status */}
            <Text style={styles.fieldLabel}>{t("personalization.occupation_label")}</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 10 }}>
              {(["STUDENT","SALARIED","SELF_EMPLOYED","BUSINESS_OWNER","FARMER","HOMEMAKER","RETIRED","UNEMPLOYED","OTHER","PREFER_NOT_TO_SAY"] as OccupationStatus[]).map((val) => (
                <Pressable
                  key={val}
                  onPress={() => setPersonOcc(val)}
                  accessibilityRole="button"
                  accessibilityLabel={t(`occ.${val}`)}
                  accessibilityState={{ selected: personOcc === val }}
                  style={[styles.chip, personOcc === val && styles.chipActive]}
                >
                  <Text style={[styles.chipText, personOcc === val && styles.chipTextActive]}>{t(`occ.${val}`)}</Text>
                  {personOcc === val && <Text style={styles.chipCheck}> ✓</Text>}
                </Pressable>
              ))}
            </ScrollView>

            {personError && <Text style={styles.errorText}>{personError}</Text>}
            {personSaved && <Text style={styles.savedText}>{t("personalization.saved")}</Text>}

            <TouchableOpacity
              style={[styles.saveBtn, personSaving && styles.saveBtnDisabled]}
              onPress={savePersonalization}
              disabled={personSaving}
              accessibilityRole="button"
              accessibilityLabel={t("personalization.save")}
              accessibilityHint="Save your personalization preferences"
            >
              <Text style={styles.saveBtnText}>{personSaving ? "Saving…" : t("personalization.save")}</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* CAPABILITY DOMAINS */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t("more.capability_domains")}</Text>
          {domainLinks.map((item) => (
            <Pressable
              key={item.path}
              style={styles.menuItem}
              onPress={() => router.push(item.path as any)}
              accessibilityRole="button"
              accessibilityLabel={`${item.title}, ${item.sub}`}
            >
              <View style={{ marginRight: 12 }}>
                <DomainIconBadge domain={item.domainId} size="small" />
              </View>
              <View style={styles.menuTextContainer}>
                <Text style={styles.menuTitle}>{item.title}</Text>
                <Text style={styles.menuSub}>{item.sub}</Text>
              </View>
              <Text style={styles.menuChevron}>→</Text>
            </Pressable>
          ))}

        </View>

        <View style={styles.actionSection}>

          <Button title={t("auth.logout")} onPress={handleSignOut} />
        </View>

        {/* BRAND FOOTER */}
        <View style={styles.brandFooter}>
          <BrandLogo variant="footer" style={{ marginBottom: 6 }} />
          <Text style={styles.brandFooterTitle}>Dhan Saarthi</Text>
          <Text style={styles.brandFooterSub}>AI-Powered Financial Companion</Text>
          <Text style={styles.brandFooterVersion}>Version 0.1.0 (Expo SDK 52)</Text>
        </View>
      </ScrollView>
    </Screen>
  );
}


const styles = StyleSheet.create({
  header: {
    marginTop: 8,
    marginBottom: 20,
  },
  title: {
    fontSize: 26,
    fontWeight: "800",
    color: colors.ink,
  },
  subtitle: {
    fontSize: 14,
    color: colors.muted,
    marginTop: 4,
  },
  userCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 16,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.purple,
    justifyContent: "center",
    alignItems: "center",
    marginRight: 14,
  },
  avatarText: {
    color: "#FFFFFF",
    fontSize: 20,
    fontWeight: "800",
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.ink,
  },
  userEmail: {
    fontSize: 13,
    color: colors.muted,
    marginTop: 2,
  },
  userMeta: {
    fontSize: 12,
    color: colors.purple,
    marginTop: 4,
    fontWeight: "600",
  },
  card: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: colors.ink,
    marginBottom: 4,
  },
  cardSubtitle: {
    fontSize: 13,
    color: colors.muted,
    marginBottom: 12,
  },
  langContainer: {
    flexDirection: "row",
    gap: 10,
  },
  langChip: {
    flex: 1,
    backgroundColor: "#f8fafc",
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#cbd5e1",
  },
  langChipActive: {
    backgroundColor: colors.purple,
    borderColor: colors.purple,
  },
  langText: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.ink,
  },
  langTextActive: {
    color: "#FFFFFF",
  },
  voiceToggleRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  voiceToggleLabel: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.ink,
  },
  toggleBtn: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  toggleBtnOn: {
    backgroundColor: "#16a34a",
  },
  toggleBtnOff: {
    backgroundColor: "#94a3b8",
  },
  toggleBtnText: {
    color: "#FFFFFF",
    fontWeight: "800",
    fontSize: 13,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: colors.ink,
    marginBottom: 12,
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 10,
  },
  menuIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  menuTextContainer: {
    flex: 1,
  },
  menuTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.ink,
  },
  menuSub: {
    fontSize: 12,
    color: colors.muted,
    marginTop: 2,
  },
  menuChevron: {
    fontSize: 18,
    color: colors.muted,
    fontWeight: "600",
  },
  actionSection: {
    marginTop: 10,
    marginBottom: 30,
  },
  // --- Personalization styles ---
  fieldLabel: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.ink,
    marginTop: 10,
    marginBottom: 6,
  },
  textInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    padding: 12,
    fontSize: 15,
    color: colors.ink,
    backgroundColor: "#fff",
    marginBottom: 4,
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 6,
  },
  chip: {
    flexDirection: "row",
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 7,
    marginRight: 8,
    marginBottom: 6,
    backgroundColor: "#f8fafc",
  },
  chipActive: {
    backgroundColor: colors.lavender,
    borderColor: colors.purple,
  },
  chipText: {
    fontSize: 13,
    color: colors.ink,
    fontWeight: "600",
  },
  chipTextActive: {
    color: colors.purple,
  },
  chipCheck: {
    fontSize: 12,
    color: colors.purple,
    fontWeight: "800",
  },
  saveBtn: {
    backgroundColor: colors.purple,
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: "center",
    marginTop: 12,
  },
  saveBtnDisabled: {
    backgroundColor: "#94a3b8",
  },
  saveBtnText: {
    color: "#FFFFFF",
    fontWeight: "800",
    fontSize: 15,
  },
  errorText: {
    color: "#dc2626",
    fontSize: 13,
    marginTop: 6,
  },
  savedText: {
    color: "#16a34a",
    fontSize: 13,
    fontWeight: "700",
    marginTop: 6,
  },
  brandFooter: {
    alignItems: "center",
    justifyContent: "center",
    marginTop: 24,
    marginBottom: 32,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  brandFooterTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: colors.purpleDark,
  },
  brandFooterSub: {
    fontSize: 12,
    color: colors.muted,
    marginTop: 2,
  },
  brandFooterVersion: {
    fontSize: 11,
    color: colors.muted,
    marginTop: 4,
    fontWeight: "600",
  },
});


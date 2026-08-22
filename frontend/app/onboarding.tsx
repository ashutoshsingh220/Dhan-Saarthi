import { useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Button, ErrorText, Field } from "@/components/Form";
import { colors } from "@/constants/theme";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/i18n/LanguageContext";
import { api } from "@/services/api";
import {
  EducationLevel,
  ExplanationLevel,
  FinancialKnowledgeLevel,
  OccupationStatus,
  ProfilePayload,
} from "@/types/api";

const languages = ["English", "Hindi", "Marathi", "Tamil", "Telugu", "Bengali", "Gujarati", "Punjabi", "Malayalam", "Kannada"];

const EDUCATION_OPTIONS: { value: EducationLevel; labelKey: string }[] = [
  { value: "PRIMARY_OR_BELOW", labelKey: "edu.PRIMARY_OR_BELOW" },
  { value: "SECONDARY", labelKey: "edu.SECONDARY" },
  { value: "HIGHER_SECONDARY", labelKey: "edu.HIGHER_SECONDARY" },
  { value: "DIPLOMA", labelKey: "edu.DIPLOMA" },
  { value: "UNDERGRADUATE", labelKey: "edu.UNDERGRADUATE" },
  { value: "POSTGRADUATE", labelKey: "edu.POSTGRADUATE" },
  { value: "DOCTORATE", labelKey: "edu.DOCTORATE" },
  { value: "OTHER", labelKey: "edu.OTHER" },
  { value: "PREFER_NOT_TO_SAY", labelKey: "edu.PREFER_NOT_TO_SAY" },
];

const KNOWLEDGE_OPTIONS: { value: FinancialKnowledgeLevel; labelKey: string; descKey: string }[] = [
  { value: "BEGINNER", labelKey: "fk.BEGINNER", descKey: "fk.BEGINNER_DESC" },
  { value: "BASIC", labelKey: "fk.BASIC", descKey: "fk.BASIC_DESC" },
  { value: "INTERMEDIATE", labelKey: "fk.INTERMEDIATE", descKey: "fk.INTERMEDIATE_DESC" },
  { value: "ADVANCED", labelKey: "fk.ADVANCED", descKey: "fk.ADVANCED_DESC" },
];

const EXPLANATION_OPTIONS: { value: ExplanationLevel; labelKey: string; descKey: string }[] = [
  { value: "SIMPLE", labelKey: "exp.SIMPLE", descKey: "exp.SIMPLE_DESC" },
  { value: "BALANCED", labelKey: "exp.BALANCED", descKey: "exp.BALANCED_DESC" },
  { value: "DETAILED", labelKey: "exp.DETAILED", descKey: "exp.DETAILED_DESC" },
];

const OCCUPATION_OPTIONS: { value: OccupationStatus; labelKey: string }[] = [
  { value: "STUDENT", labelKey: "occ.STUDENT" },
  { value: "SALARIED", labelKey: "occ.SALARIED" },
  { value: "SELF_EMPLOYED", labelKey: "occ.SELF_EMPLOYED" },
  { value: "BUSINESS_OWNER", labelKey: "occ.BUSINESS_OWNER" },
  { value: "FARMER", labelKey: "occ.FARMER" },
  { value: "HOMEMAKER", labelKey: "occ.HOMEMAKER" },
  { value: "RETIRED", labelKey: "occ.RETIRED" },
  { value: "UNEMPLOYED", labelKey: "occ.UNEMPLOYED" },
  { value: "OTHER", labelKey: "occ.OTHER" },
  { value: "PREFER_NOT_TO_SAY", labelKey: "occ.PREFER_NOT_TO_SAY" },
];

const initial = {
  age: "",
  gender: "",
  occupation: "",
  city: "",
  monthly_income: "",
  monthly_expenses: "",
  savings: "",
  financial_goal: "",
  risk_preference: "moderate" as "low" | "moderate" | "high",
  preferred_language: "English",
  accessibility_mode: "standard" as "standard" | "voice_first",
};

const initialPersonalization = {
  date_of_birth: "",
  education_level: null as EducationLevel | null,
  financial_knowledge_level: null as FinancialKnowledgeLevel | null,
  preferred_explanation_level: null as ExplanationLevel | null,
  occupation_status: null as OccupationStatus | null,
};

export default function Onboarding() {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState(initial);
  const [personalization, setPersonalization] = useState(initialPersonalization);
  const [error, setError] = useState<string>();
  const [busy, setBusy] = useState(false);
  const { token, setTwin } = useAuth();
  const { t } = useLanguage();

  const patch = (key: keyof typeof form, value: string) => setForm({ ...form, [key]: value });
  const patchP = <K extends keyof typeof initialPersonalization>(key: K, value: (typeof initialPersonalization)[K]) =>
    setPersonalization({ ...personalization, [key]: value });

  const toProfile = () => {
    if (!form.preferred_language) return setError("Choose a language.");
    setError(undefined);
    setStep(2);
  };

  const review = () => {
    if (!form.age || !form.occupation || !form.monthly_income || !form.monthly_expenses || !form.savings || !form.financial_goal)
      return setError("Please complete the required financial profile fields.");
    setError(undefined);
    setStep(3); // → Date of birth step
  };

  const generate = async () => {
    if (!token) return;
    setBusy(true);
    setError(undefined);
    try {
      const payload: ProfilePayload = {
        ...form,
        age: Number(form.age),
        monthly_income: Number(form.monthly_income),
        monthly_expenses: Number(form.monthly_expenses),
        savings: Number(form.savings),
        gender: form.gender || undefined,
        city: form.city || undefined,
        // personalization fields
        date_of_birth: personalization.date_of_birth || null,
        education_level: personalization.education_level || null,
        financial_knowledge_level: personalization.financial_knowledge_level || null,
        preferred_explanation_level: personalization.preferred_explanation_level || null,
        occupation_status: personalization.occupation_status || null,
      };
      await api.saveProfile(payload, token);
      setTwin(await api.generateTwin(token));
      router.replace("/twin");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to build your financial view.");
    } finally {
      setBusy(false);
    }
  };

  // Step 0: Accessibility
  if (step === 0)
    return (
      <Screen>
        <Title text="Choose your experience" sub="You can change this preference later." />
        <Choice label="Standard Experience" selected={form.accessibility_mode === "standard"} onPress={() => patch("accessibility_mode", "standard")} />
        <Choice label="Voice-First Experience" selected={form.accessibility_mode === "voice_first"} onPress={() => patch("accessibility_mode", "voice_first")} />
        <Button title="Continue" onPress={() => setStep(1)} />
      </Screen>
    );

  // Step 1: Language
  if (step === 1)
    return (
      <Screen>
        <Title text="Choose your language" sub="We will use this preference for clearer guidance later." />
        <View style={styles.grid}>{languages.map((language) => <Choice key={language} label={language} selected={form.preferred_language === language} onPress={() => patch("preferred_language", language)} />)}</View>
        <ErrorText text={error} />
        <Button title="Continue" onPress={toProfile} />
      </Screen>
    );

  // Step 2: Financial profile
  if (step === 2)
    return (
      <Screen>
        <Title text="Your financial profile" sub="This information creates your initial Financial Twin." />
        <ErrorText text={error} />
        <Field label="Age" value={form.age} onChangeText={(v) => patch("age", v)} keyboardType="numeric" />
        <Field label="Gender (optional)" value={form.gender} onChangeText={(v) => patch("gender", v)} />
        <Field label="Occupation" value={form.occupation} onChangeText={(v) => patch("occupation", v)} />
        <Field label="City (optional)" value={form.city} onChangeText={(v) => patch("city", v)} />
        <Field label="Monthly income (₹)" value={form.monthly_income} onChangeText={(v) => patch("monthly_income", v)} keyboardType="numeric" />
        <Field label="Monthly expenses (₹)" value={form.monthly_expenses} onChangeText={(v) => patch("monthly_expenses", v)} keyboardType="numeric" />
        <Field label="Current savings (₹)" value={form.savings} onChangeText={(v) => patch("savings", v)} keyboardType="numeric" />
        <Field label="Primary financial goal" value={form.financial_goal} onChangeText={(v) => patch("financial_goal", v)} placeholder="e.g. Buy a home" />
        <Text style={styles.label}>Risk preference</Text>
        <View style={styles.grid}>
          {(["low", "moderate", "high"] as const).map((risk) => (
            <Choice key={risk} label={risk[0].toUpperCase() + risk.slice(1)} selected={form.risk_preference === risk} onPress={() => patch("risk_preference", risk)} />
          ))}
        </View>
        <Button title="Continue" onPress={review} />
      </Screen>
    );

  // Step 3: Date of birth
  if (step === 3)
    return (
      <Screen>
        <Title text={t("onboarding.personalization_title")} sub={t("onboarding.personalization_sub")} />
        <Text style={styles.label}>{t("personalization.dob_label")}</Text>
        <TextInput
          style={styles.textInput}
          value={personalization.date_of_birth}
          onChangeText={(v) => patchP("date_of_birth", v)}
          placeholder={t("personalization.dob_placeholder")}
          keyboardType="numeric"
          accessibilityLabel={t("personalization.dob_label")}
          accessibilityHint="Enter your date of birth in YYYY-MM-DD format"
          accessibilityRole="none"
          accessible
        />
        <ErrorText text={error} />
        <Button title="Continue" onPress={() => { setError(undefined); setStep(4); }} />
        <Button title={t("onboarding.skip")} onPress={() => { patchP("date_of_birth", ""); setStep(4); }} />
      </Screen>
    );

  // Step 4: Education level
  if (step === 4)
    return (
      <Screen>
        <Title text={t("personalization.education_label")} sub={t("personalization.optional_note")} />
        <ScrollView style={{ maxHeight: 400 }}>
          {EDUCATION_OPTIONS.map((opt) => (
            <Choice
              key={opt.value}
              label={t(opt.labelKey)}
              selected={personalization.education_level === opt.value}
              onPress={() => patchP("education_level", opt.value)}
              accessibilityLabel={t(opt.labelKey)}
              accessibilityHint={`Select ${t(opt.labelKey)} as your education level`}
            />
          ))}
        </ScrollView>
        <Button title="Continue" onPress={() => setStep(5)} />
        <Button title={t("onboarding.skip")} onPress={() => { patchP("education_level", null); setStep(5); }} />
      </Screen>
    );

  // Step 5: Financial knowledge
  if (step === 5)
    return (
      <Screen>
        <Title text={t("personalization.knowledge_label")} sub={t("personalization.optional_note")} />
        {KNOWLEDGE_OPTIONS.map((opt) => (
          <DescChoice
            key={opt.value}
            label={t(opt.labelKey)}
            desc={t(opt.descKey)}
            selected={personalization.financial_knowledge_level === opt.value}
            onPress={() => patchP("financial_knowledge_level", opt.value)}
            accessibilityLabel={`${t(opt.labelKey)}: ${t(opt.descKey)}`}
          />
        ))}
        <Button title="Continue" onPress={() => setStep(6)} />
        <Button title={t("onboarding.skip")} onPress={() => { patchP("financial_knowledge_level", null); setStep(6); }} />
      </Screen>
    );

  // Step 6: Explanation level
  if (step === 6)
    return (
      <Screen>
        <Title text={t("personalization.explanation_label")} sub={t("personalization.optional_note")} />
        {EXPLANATION_OPTIONS.map((opt) => (
          <DescChoice
            key={opt.value}
            label={t(opt.labelKey)}
            desc={t(opt.descKey)}
            selected={personalization.preferred_explanation_level === opt.value}
            onPress={() => patchP("preferred_explanation_level", opt.value)}
            accessibilityLabel={`${t(opt.labelKey)}: ${t(opt.descKey)}`}
          />
        ))}
        <Button title="Continue" onPress={() => setStep(7)} />
        <Button title={t("onboarding.skip")} onPress={() => { patchP("preferred_explanation_level", null); setStep(7); }} />
      </Screen>
    );

  // Step 7: Occupation
  if (step === 7)
    return (
      <Screen>
        <Title text={t("personalization.occupation_label")} sub={t("personalization.optional_note")} />
        <ScrollView style={{ maxHeight: 400 }}>
          {OCCUPATION_OPTIONS.map((opt) => (
            <Choice
              key={opt.value}
              label={t(opt.labelKey)}
              selected={personalization.occupation_status === opt.value}
              onPress={() => patchP("occupation_status", opt.value)}
              accessibilityLabel={t(opt.labelKey)}
              accessibilityHint={`Select ${t(opt.labelKey)} as your occupation`}
            />
          ))}
        </ScrollView>
        <Button title="Continue" onPress={() => setStep(8)} />
        <Button title={t("onboarding.skip")} onPress={() => { patchP("occupation_status", null); setStep(8); }} />
      </Screen>
    );

  // Step 8: Review and submit
  return (
    <Screen>
      <Title text="Review your financial view" sub="Check the information before we build your Financial Twin." />
      <View style={styles.review}>
        {Object.entries(form).filter(([key]) => !["gender", "city"].includes(key)).map(([key, value]) => (
          <View key={key} style={styles.row}>
            <Text style={styles.key}>{key.replaceAll("_", " ")}</Text>
            <Text style={styles.value}>{value || "—"}</Text>
          </View>
        ))}
        {personalization.date_of_birth ? (
          <View style={styles.row}>
            <Text style={styles.key}>date of birth</Text>
            <Text style={styles.value}>{personalization.date_of_birth}</Text>
          </View>
        ) : null}
        {personalization.education_level ? (
          <View style={styles.row}>
            <Text style={styles.key}>education</Text>
            <Text style={styles.value}>{personalization.education_level}</Text>
          </View>
        ) : null}
        {personalization.financial_knowledge_level ? (
          <View style={styles.row}>
            <Text style={styles.key}>financial knowledge</Text>
            <Text style={styles.value}>{personalization.financial_knowledge_level}</Text>
          </View>
        ) : null}
        {personalization.preferred_explanation_level ? (
          <View style={styles.row}>
            <Text style={styles.key}>explanation style</Text>
            <Text style={styles.value}>{personalization.preferred_explanation_level}</Text>
          </View>
        ) : null}
        {personalization.occupation_status ? (
          <View style={styles.row}>
            <Text style={styles.key}>occupation</Text>
            <Text style={styles.value}>{personalization.occupation_status}</Text>
          </View>
        ) : null}
      </View>
      <ErrorText text={error} />
      <Button
        title={busy ? "Building your personalized financial view…" : t("onboarding.finish")}
        onPress={generate}
        disabled={busy}
      />
      <Button title="Edit financial info" onPress={() => setStep(2)} disabled={busy} />
    </Screen>
  );
}

import { BrandLogo } from "@/components/branding/BrandLogo";

function Title({ text, sub }: { text: string; sub: string }) {
  return (
    <>
      <View style={{ alignItems: "center", marginBottom: 12, marginTop: 4 }}>
        <BrandLogo variant="onboarding" />
      </View>
      <Text style={styles.title}>{text}</Text>
      <Text style={styles.sub}>{sub}</Text>
    </>
  );
}


function Choice({
  label,
  selected,
  onPress,
  accessibilityLabel,
  accessibilityHint,
}: {
  label: string;
  selected: boolean;
  onPress: () => void;
  accessibilityLabel?: string;
  accessibilityHint?: string;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel || label}
      accessibilityHint={accessibilityHint}
      accessibilityState={{ selected }}
      onPress={onPress}
      style={[styles.choice, selected && styles.selected]}
    >
      <Text style={[styles.choiceText, selected && styles.selectedText]}>{label}</Text>
      {selected && <Text style={styles.selectedBadge}> ✓ Selected</Text>}
    </Pressable>
  );
}

function DescChoice({
  label,
  desc,
  selected,
  onPress,
  accessibilityLabel,
}: {
  label: string;
  desc: string;
  selected: boolean;
  onPress: () => void;
  accessibilityLabel?: string;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel || `${label}: ${desc}`}
      accessibilityState={{ selected }}
      onPress={onPress}
      style={[styles.choice, selected && styles.selected]}
    >
      <Text style={[styles.choiceText, selected && styles.selectedText]}>{label}</Text>
      <Text style={[styles.choiceDesc, selected && styles.selectedDescText]}>{desc}</Text>
      {selected && <Text style={styles.selectedBadge}>✓ Selected</Text>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 27, fontWeight: "800", color: colors.ink, marginTop: 20 },
  sub: { color: colors.muted, marginVertical: 10, lineHeight: 22 },
  choice: {
    borderWidth: 1,
    borderColor: colors.border,
    padding: 15,
    borderRadius: 13,
    marginBottom: 10,
  },
  selected: { backgroundColor: colors.lavender, borderColor: colors.purple },
  choiceText: { color: colors.ink, fontWeight: "600" },
  selectedText: { color: colors.purple },
  choiceDesc: { color: colors.muted, fontSize: 13, marginTop: 2 },
  selectedDescText: { color: colors.purple },
  selectedBadge: { color: colors.purple, fontSize: 12, marginTop: 4, fontWeight: "700" },
  grid: { marginTop: 8 },
  label: { color: colors.ink, fontWeight: "600", marginVertical: 10 },
  textInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: 14,
    fontSize: 16,
    color: colors.ink,
    marginBottom: 12,
    backgroundColor: "#fff",
  },
  review: { backgroundColor: colors.lavender, borderRadius: 16, padding: 16, marginVertical: 16 },
  row: { marginBottom: 12 },
  key: { color: colors.muted, textTransform: "capitalize", fontSize: 12 },
  value: { color: colors.ink, fontSize: 16, fontWeight: "600", marginTop: 2 },
});


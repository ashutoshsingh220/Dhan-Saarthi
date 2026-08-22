import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Linking,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { colors } from "@/constants/theme";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/i18n/LanguageContext";
import { api } from "@/services/api";
import type { GovernmentScheme, SchemeRecommendation, SupportContextPayload } from "@/types/api";

const QUICK_PATHS = [
  { key: "FARMER_SUPPORT", labelKey: "qp.farmer_support", icon: "🌾" },
  { key: "AGRICULTURE_LOAN", labelKey: "qp.agriculture_loan", icon: "🚜" },
  { key: "DAIRY_AND_LIVESTOCK", labelKey: "qp.dairy_livestock", icon: "🐄" },
  { key: "FISHERIES", labelKey: "qp.fisheries", icon: "🐟" },
  { key: "SMALL_BUSINESS", labelKey: "qp.start_business", icon: "🏪" },
  { key: "ENTREPRENEURSHIP", labelKey: "qp.grow_business", icon: "📈" },
  { key: "SELF_EMPLOYMENT", labelKey: "qp.self_employment", icon: "💼" },
];

function getRankStyle(rank: string) {
  switch (rank) {
    case "HIGHLY_RELEVANT":
      return styles.rank_HIGHLY_RELEVANT;
    case "RELEVANT":
      return styles.rank_RELEVANT;
    case "EXPLORE":
      return styles.rank_EXPLORE;
    default:
      return styles.rank_NEEDS_MORE_INFORMATION;
  }
}

export default function SchemesScreen() {

  const { token } = useAuth();
  const { t } = useLanguage();

  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState<SchemeRecommendation[]>([]);
  const [catalog, setCatalog] = useState<GovernmentScheme[]>([]);
  const [activeFilter, setActiveFilter] = useState<string>("ALL");
  const [selectedScheme, setSelectedScheme] = useState<GovernmentScheme | null>(null);

  // Support context setup state
  const [showSetup, setShowSetup] = useState(false);
  const [stateName, setStateName] = useState("");
  const [districtName, setDistrictName] = useState("");
  const [areaType, setAreaType] = useState<"RURAL" | "URBAN" | "SEMI_URBAN">("RURAL");
  const [farmInterest, setFarmInterest] = useState(true);
  const [bizInterest, setBizInterest] = useState(true);
  const [savingContext, setSavingContext] = useState(false);

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (token) {
        const recs = await api.getSchemeRecommendations(token);
        setRecommendations(recs);
      }
      const cat = await api.getSchemes();
      setCatalog(cat);
    } catch (err) {
      console.warn("Failed to load scheme data", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSupportContext = async () => {
    if (!token) return;
    setSavingContext(true);
    try {
      const payload: SupportContextPayload = {
        state: stateName || null,
        district: districtName || null,
        rural_or_urban: areaType,
        farming_interest: farmInterest,
        business_interest: bizInterest,
      };
      await api.updateSupportContext(payload, token);
      setShowSetup(false);
      await loadData();
    } catch (err) {
      console.warn("Failed to update support context", err);
    } finally {
      setSavingContext(false);
    }
  };

  const handleAskSaarthi = (scheme: GovernmentScheme) => {
    setSelectedScheme(null);
    router.push({
      pathname: "/(tabs)/saarthi" as any,
      params: {
        initialQuery: `Explain the government scheme '${scheme.name}' (${scheme.short_name}) to me in simple language. Tell me why it may be relevant to my situation and what I should verify next.`,
      },
    });
  };

  const openOfficialUrl = (url: string) => {
    if (url) {
      Linking.openURL(url).catch((err) => console.warn("Cannot open URL", err));
    }
  };

  const filteredCatalog = catalog.filter((s) => {
    if (activeFilter === "ALL") return true;
    if (activeFilter === "FARMER") return ["FARMER_SUPPORT", "AGRICULTURE_LOAN", "CROP_INSURANCE", "AGRICULTURAL_INFRASTRUCTURE", "FARM_EQUIPMENT", "IRRIGATION", "DAIRY_AND_LIVESTOCK", "FISHERIES"].includes(s.category);
    if (activeFilter === "BUSINESS") return ["SMALL_BUSINESS", "MICRO_ENTERPRISE", "SELF_EMPLOYMENT", "ENTREPRENEURSHIP", "RURAL_ENTERPRISE"].includes(s.category);
    if (activeFilter === "WOMEN") return s.category === "WOMEN_ENTREPRENEURSHIP" || s.tags.includes("WOMEN_ENTREPRENEURSHIP");
    if (activeFilter === "RURAL") return s.category === "RURAL_ENTERPRISE" || s.tags.includes("RURAL_ENTERPRISE");
    return s.category === activeFilter || s.tags.includes(activeFilter);
  });

  return (
    <Screen>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 40 }}>
        {/* HEADER */}
        <View style={styles.header}>
          <Text style={styles.title}>🏛️ {t("schemes.title")}</Text>
          <Text style={styles.subtitle}>{t("schemes.subtitle")}</Text>

          {token && (
            <TouchableOpacity
              style={styles.setupBtn}
              onPress={() => setShowSetup(!showSetup)}
              accessibilityRole="button"
              accessibilityLabel={t("schemes.setup_context")}
            >
              <Text style={styles.setupBtnText}>⚙️ {t("schemes.setup_context")}</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* SUPPORT CONTEXT FORM (COLLAPSIBLE) */}
        {showSetup && (
          <View style={styles.setupCard}>
            <Text style={styles.setupTitle}>{t("schemes.setup_context")}</Text>
            <Text style={styles.setupSub}>{t("schemes.setup_context_sub")}</Text>

            <Text style={styles.label}>{t("schemes.state_label")}</Text>
            <TextInput
              style={styles.input}
              value={stateName}
              onChangeText={setStateName}
              placeholder="e.g. Maharashtra, Rajasthan, Uttar Pradesh"
              accessible
              accessibilityLabel={t("schemes.state_label")}
            />

            <Text style={styles.label}>{t("schemes.area_label")}</Text>
            <View style={styles.rowGrid}>
              {(["RURAL", "URBAN", "SEMI_URBAN"] as const).map((a) => (
                <Pressable
                  key={a}
                  style={[styles.chipBtn, areaType === a && styles.chipBtnActive]}
                  onPress={() => setAreaType(a)}
                  accessibilityRole="button"
                  accessibilityState={{ selected: areaType === a }}
                >
                  <Text style={[styles.chipText, areaType === a && styles.chipTextActive]}>
                    {t(`schemes.area_${a.toLowerCase().replace("_semi", "_semi")}`)}
                  </Text>
                </Pressable>
              ))}
            </View>

            <View style={styles.checkRow}>
              <Pressable
                style={[styles.checkbox, farmInterest && styles.checkboxActive]}
                onPress={() => setFarmInterest(!farmInterest)}
                accessibilityRole="checkbox"
                accessibilityState={{ checked: farmInterest }}
              >
                <Text style={styles.checkIcon}>{farmInterest ? "✓" : ""}</Text>
              </Pressable>
              <Text style={styles.checkLabel}>{t("schemes.farm_interest")}</Text>
            </View>

            <View style={styles.checkRow}>
              <Pressable
                style={[styles.checkbox, bizInterest && styles.checkboxActive]}
                onPress={() => setBizInterest(!bizInterest)}
                accessibilityRole="checkbox"
                accessibilityState={{ checked: bizInterest }}
              >
                <Text style={styles.checkIcon}>{bizInterest ? "✓" : ""}</Text>
              </Pressable>
              <Text style={styles.checkLabel}>{t("schemes.business_interest")}</Text>
            </View>

            <TouchableOpacity
              style={[styles.saveBtn, savingContext && styles.btnDisabled]}
              onPress={handleSaveSupportContext}
              disabled={savingContext}
              accessibilityRole="button"
              accessibilityLabel={t("schemes.save_context")}
            >
              <Text style={styles.saveBtnText}>{savingContext ? "Saving…" : t("schemes.save_context")}</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* QUICK PATHS SECTION */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t("schemes.quick_paths")}</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginHorizontal: -4 }}>
            {QUICK_PATHS.map((qp) => (
              <TouchableOpacity
                key={qp.key}
                style={[styles.quickCard, activeFilter === qp.key && styles.quickCardActive]}
                onPress={() => setActiveFilter(activeFilter === qp.key ? "ALL" : qp.key)}
                accessibilityRole="button"
                accessibilityLabel={t(qp.labelKey)}
                accessibilityState={{ selected: activeFilter === qp.key }}
              >
                <Text style={styles.quickIcon}>{qp.icon}</Text>
                <Text style={[styles.quickLabel, activeFilter === qp.key && styles.quickLabelActive]}>
                  {t(qp.labelKey)}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {loading ? (
          <ActivityIndicator size="large" color={colors.purple} style={{ marginVertical: 30 }} />
        ) : (
          <>
            {/* RECOMMENDED SCHEMES SECTION */}
            {recommendations.length > 0 && activeFilter === "ALL" && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>🎯 {t("schemes.recommended")}</Text>
                <Text style={styles.sectionSub}>{t("schemes.recommended_sub")}</Text>

                {recommendations.map((rec) => (
                  <View key={rec.scheme.scheme_id} style={styles.recCard}>
                    <View style={styles.cardHeaderRow}>
                      <Text style={styles.schemeName}>{rec.scheme.name}</Text>
                      <View style={[styles.rankBadge, getRankStyle(rec.relevance_rank)]}>
                        <Text style={styles.rankBadgeText}>{t(`rank.${rec.relevance_rank}`)}</Text>
                      </View>

                    </View>

                    <Text style={styles.schemeDesc}>{rec.scheme.benefits_summary}</Text>

                    <View style={styles.whyBox}>
                      <Text style={styles.whyTitle}>💡 {t("schemes.why_recommended")}:</Text>
                      <Text style={styles.whyText}>{rec.why_recommended}</Text>
                    </View>

                    <View style={styles.cardActionRow}>
                      <TouchableOpacity
                        style={styles.detailBtn}
                        onPress={() => setSelectedScheme(rec.scheme)}
                        accessibilityRole="button"
                        accessibilityLabel={`View details for ${rec.scheme.short_name}`}
                      >
                        <Text style={styles.detailBtnText}>View Details</Text>
                      </TouchableOpacity>

                      <TouchableOpacity
                        style={styles.askBtn}
                        onPress={() => handleAskSaarthi(rec.scheme)}
                        accessibilityRole="button"
                        accessibilityLabel={`Ask AI Saarthi to explain ${rec.scheme.short_name}`}
                      >
                        <Text style={styles.askBtnText}>🤖 Ask Saarthi</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                ))}
              </View>
            )}

            {/* CATALOG EXPLORER SECTION */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>📋 {t("schemes.all_schemes")}</Text>

              {/* Filter Tabs */}
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 14 }}>
                {[
                  { key: "ALL", label: t("schemes.filter_all") },
                  { key: "FARMER", label: t("schemes.filter_farmer") },
                  { key: "BUSINESS", label: t("schemes.filter_business") },
                  { key: "WOMEN", label: t("schemes.filter_women") },
                  { key: "RURAL", label: t("schemes.filter_rural") },
                ].map((f) => (
                  <Pressable
                    key={f.key}
                    style={[styles.filterChip, activeFilter === f.key && styles.filterChipActive]}
                    onPress={() => setActiveFilter(f.key)}
                    accessibilityRole="button"
                    accessibilityState={{ selected: activeFilter === f.key }}
                  >
                    <Text style={[styles.filterChipText, activeFilter === f.key && styles.filterChipTextActive]}>
                      {f.label}
                    </Text>
                  </Pressable>
                ))}
              </ScrollView>

              {filteredCatalog.map((s) => (
                <View key={s.scheme_id} style={styles.catCard}>
                  <Text style={styles.catCardTitle}>{s.name}</Text>
                  <Text style={styles.catCardAuthority}>🏢 {s.official_authority}</Text>
                  <Text style={styles.catCardDesc} numberOfLines={2}>{s.description}</Text>

                  <View style={styles.cardActionRow}>
                    <TouchableOpacity
                      style={styles.detailBtn}
                      onPress={() => setSelectedScheme(s)}
                      accessibilityRole="button"
                      accessibilityLabel={`View details for ${s.short_name}`}
                    >
                      <Text style={styles.detailBtnText}>View Details & Eligibility</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.askBtn}
                      onPress={() => handleAskSaarthi(s)}
                      accessibilityRole="button"
                      accessibilityLabel={`Ask Saarthi about ${s.short_name}`}
                    >
                      <Text style={styles.askBtnText}>🤖 Ask Saarthi</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              ))}
            </View>
          </>
        )}

        {/* SCHEME DETAIL MODAL */}
        <Modal visible={selectedScheme !== null} animationType="slide" transparent>
          <View style={styles.modalOverlay}>
            <View style={styles.modalContainer}>
              {selectedScheme && (
                <ScrollView showsVerticalScrollIndicator={false}>
                  <View style={styles.modalHeader}>
                    <Text style={styles.modalTitle}>{selectedScheme.name}</Text>
                    <TouchableOpacity onPress={() => setSelectedScheme(null)} accessibilityRole="button" accessibilityLabel="Close modal">
                      <Text style={styles.closeText}>✕</Text>
                    </TouchableOpacity>
                  </View>

                  <Text style={styles.authorityText}>🏛️ {selectedScheme.official_authority}</Text>
                  <Text style={styles.targetText}>👥 Target Groups: {selectedScheme.target_groups}</Text>

                  <View style={styles.detailBox}>
                    <Text style={styles.detailBoxTitle}>📌 About the Scheme</Text>
                    <Text style={styles.detailBoxBody}>{selectedScheme.description}</Text>
                  </View>

                  <View style={styles.detailBox}>
                    <Text style={styles.detailBoxTitle}>🎁 Key Benefits</Text>
                    <Text style={styles.detailBoxBody}>{selectedScheme.benefits_summary}</Text>
                  </View>

                  {selectedScheme.required_documents.length > 0 && (
                    <View style={styles.detailBox}>
                      <Text style={styles.detailBoxTitle}>📄 Documents Required</Text>
                      {selectedScheme.required_documents.map((doc, idx) => (
                        <Text key={idx} style={styles.bulletText}>• {doc}</Text>
                      ))}
                    </View>
                  )}

                  {selectedScheme.how_to_apply.length > 0 && (
                    <View style={styles.detailBox}>
                      <Text style={styles.detailBoxTitle}>📝 How to Apply</Text>
                      {selectedScheme.how_to_apply.map((step, idx) => (
                        <Text key={idx} style={styles.bulletText}>{idx + 1}. {step}</Text>
                      ))}
                    </View>
                  )}

                  <Text style={styles.disclaimerText}>⚠️ {t("schemes.disclaimer")}</Text>
                  <Text style={styles.verifiedText}>Last verified: {selectedScheme.source_last_verified_at.split("T")[0]}</Text>

                  <View style={styles.modalBtnRow}>
                    <TouchableOpacity
                      style={styles.portalBtn}
                      onPress={() => openOfficialUrl(selectedScheme.official_url)}
                      accessibilityRole="button"
                      accessibilityLabel="Open Official Government Portal"
                    >
                      <Text style={styles.portalBtnText}>🔗 {t("schemes.official_source")}</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.modalAskBtn}
                      onPress={() => handleAskSaarthi(selectedScheme)}
                      accessibilityRole="button"
                      accessibilityLabel="Ask AI Saarthi to explain this scheme"
                    >
                      <Text style={styles.modalAskBtnText}>🤖 {t("schemes.ask_saarthi")}</Text>
                    </TouchableOpacity>
                  </View>
                </ScrollView>
              )}
            </View>
          </View>
        </Modal>
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { marginTop: 12, marginBottom: 16 },
  title: { fontSize: 26, fontWeight: "800", color: colors.ink },
  subtitle: { fontSize: 14, color: colors.muted, marginTop: 4 },
  setupBtn: { marginTop: 10, alignSelf: "flex-start", backgroundColor: colors.lavender, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20 },
  setupBtnText: { color: colors.purple, fontWeight: "700", fontSize: 13 },

  setupCard: { backgroundColor: "#ffffff", borderRadius: 16, padding: 16, borderWidth: 1, borderColor: colors.border, marginBottom: 16 },
  setupTitle: { fontSize: 16, fontWeight: "800", color: colors.ink },
  setupSub: { fontSize: 13, color: colors.muted, marginBottom: 12 },
  label: { fontSize: 13, fontWeight: "700", color: colors.ink, marginTop: 8, marginBottom: 4 },
  input: { borderWidth: 1, borderColor: colors.border, borderRadius: 10, padding: 10, fontSize: 14, color: colors.ink, backgroundColor: "#fff" },
  rowGrid: { flexDirection: "row", gap: 8, marginVertical: 6 },
  chipBtn: { flex: 1, paddingVertical: 8, borderWidth: 1, borderColor: colors.border, borderRadius: 10, alignItems: "center", backgroundColor: "#f8fafc" },
  chipBtnActive: { backgroundColor: colors.purple, borderColor: colors.purple },
  chipText: { fontSize: 12, fontWeight: "700", color: colors.ink },
  chipTextActive: { color: "#ffffff" },
  checkRow: { flexDirection: "row", alignItems: "center", marginTop: 10 },
  checkbox: { width: 22, height: 22, borderWidth: 1, borderColor: colors.border, borderRadius: 6, justifyContent: "center", alignItems: "center", marginRight: 10, backgroundColor: "#fff" },
  checkboxActive: { backgroundColor: colors.purple, borderColor: colors.purple },
  checkIcon: { color: "#ffffff", fontWeight: "800", fontSize: 14 },
  checkLabel: { fontSize: 13, color: colors.ink, fontWeight: "600" },
  saveBtn: { backgroundColor: colors.purple, borderRadius: 10, paddingVertical: 10, alignItems: "center", marginTop: 14 },
  saveBtnText: { color: "#ffffff", fontWeight: "800", fontSize: 14 },
  btnDisabled: { backgroundColor: "#94a3b8" },

  section: { marginBottom: 24 },
  sectionTitle: { fontSize: 18, fontWeight: "800", color: colors.ink, marginBottom: 4 },
  sectionSub: { fontSize: 13, color: colors.muted, marginBottom: 12 },

  quickCard: { backgroundColor: "#ffffff", borderRadius: 14, padding: 12, marginHorizontal: 4, width: 130, borderWidth: 1, borderColor: colors.border, alignItems: "center" },
  quickCardActive: { backgroundColor: colors.lavender, borderColor: colors.purple },
  quickIcon: { fontSize: 24, marginBottom: 6 },
  quickLabel: { fontSize: 12, fontWeight: "700", color: colors.ink, textAlign: "center" },
  quickLabelActive: { color: colors.purple },

  recCard: { backgroundColor: "#ffffff", borderRadius: 16, padding: 16, borderWidth: 1, borderColor: colors.border, marginBottom: 14 },
  cardHeaderRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 },
  schemeName: { flex: 1, fontSize: 16, fontWeight: "800", color: colors.ink, marginRight: 8 },
  rankBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  rank_HIGHLY_RELEVANT: { backgroundColor: "#dcfce7" },
  rank_RELEVANT: { backgroundColor: "#e0f2fe" },
  rank_EXPLORE: { backgroundColor: "#fef3c7" },
  rank_NEEDS_MORE_INFORMATION: { backgroundColor: "#f3f4f6" },
  rankBadgeText: { fontSize: 10, fontWeight: "800", color: colors.ink },
  schemeDesc: { fontSize: 14, color: colors.ink, lineHeight: 20, marginBottom: 10 },
  whyBox: { backgroundColor: "#f8fafc", borderRadius: 10, padding: 10, marginBottom: 12, borderWidth: 1, borderColor: "#e2e8f0" },
  whyTitle: { fontSize: 12, fontWeight: "800", color: colors.purple, marginBottom: 2 },
  whyText: { fontSize: 13, color: colors.ink, lineHeight: 18 },

  catCard: { backgroundColor: "#ffffff", borderRadius: 14, padding: 14, borderWidth: 1, borderColor: colors.border, marginBottom: 12 },
  catCardTitle: { fontSize: 15, fontWeight: "800", color: colors.ink },
  catCardAuthority: { fontSize: 12, color: colors.purple, fontWeight: "600", marginTop: 2, marginBottom: 6 },
  catCardDesc: { fontSize: 13, color: colors.muted, lineHeight: 18, marginBottom: 10 },

  cardActionRow: { flexDirection: "row", gap: 10, marginTop: 4 },
  detailBtn: { flex: 1, backgroundColor: "#f1f5f9", paddingVertical: 9, borderRadius: 10, alignItems: "center" },
  detailBtnText: { color: colors.ink, fontWeight: "700", fontSize: 13 },
  askBtn: { flex: 1, backgroundColor: colors.lavender, paddingVertical: 9, borderRadius: 10, alignItems: "center" },
  askBtnText: { color: colors.purple, fontWeight: "800", fontSize: 13 },

  filterChip: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: colors.border, marginRight: 8, backgroundColor: "#fff" },
  filterChipActive: { backgroundColor: colors.purple, borderColor: colors.purple },
  filterChipText: { fontSize: 13, fontWeight: "700", color: colors.ink },
  filterChipTextActive: { color: "#fff" },

  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "flex-end" },
  modalContainer: { backgroundColor: "#fff", borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 20, maxHeight: "85%" },
  modalHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 8 },
  modalTitle: { flex: 1, fontSize: 18, fontWeight: "800", color: colors.ink, marginRight: 10 },
  closeText: { fontSize: 20, color: colors.muted, fontWeight: "800", padding: 4 },
  authorityText: { fontSize: 13, color: colors.purple, fontWeight: "700", marginBottom: 2 },
  targetText: { fontSize: 12, color: colors.muted, marginBottom: 14 },
  detailBox: { backgroundColor: "#f8fafc", borderRadius: 12, padding: 12, marginBottom: 12, borderWidth: 1, borderColor: "#e2e8f0" },
  detailBoxTitle: { fontSize: 14, fontWeight: "800", color: colors.ink, marginBottom: 6 },
  detailBoxBody: { fontSize: 14, color: colors.ink, lineHeight: 20 },
  bulletText: { fontSize: 13, color: colors.ink, lineHeight: 19, marginTop: 3 },
  disclaimerText: { fontSize: 12, color: colors.muted, fontStyle: "italic", marginTop: 8, lineHeight: 17 },
  verifiedText: { fontSize: 11, color: colors.muted, marginTop: 4, marginBottom: 16 },
  modalBtnRow: { flexDirection: "row", gap: 10, marginBottom: 20 },
  portalBtn: { flex: 1, backgroundColor: colors.purple, paddingVertical: 12, borderRadius: 12, alignItems: "center" },
  portalBtnText: { color: "#fff", fontWeight: "800", fontSize: 13 },
  modalAskBtn: { flex: 1, backgroundColor: colors.lavender, paddingVertical: 12, borderRadius: 12, alignItems: "center" },
  modalAskBtnText: { color: colors.purple, fontWeight: "800", fontSize: 13 },
});

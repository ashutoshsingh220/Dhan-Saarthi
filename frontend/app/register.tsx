import { useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { Button, ErrorText, Field } from "@/components/Form";
import { Screen } from "@/components/Screen";
import { BrandLogo } from "@/components/branding/BrandLogo";
import { colors } from "@/constants/theme";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/services/api";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string>();
  const [busy, setBusy] = useState(false);
  const { authenticate } = useAuth();

  const submit = async () => {
    setError(undefined);
    const cleanName = name.trim();
    const cleanEmail = email.trim();
    if (!cleanName || !cleanEmail || password.length < 8)
      return setError("Enter your name, email, and a password of at least 8 characters.");
    if (password !== confirm) return setError("Passwords do not match.");
    setBusy(true);
    try {
      await authenticate(await api.register(cleanName, cleanEmail, password));
      router.replace("/onboarding");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to create your account.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Screen>
      <View style={styles.brandHeader}>
        <BrandLogo variant="header" />
      </View>
      <Text style={{ fontSize: 28, fontWeight: "800", marginBottom: 8 }}>Create your account</Text>
      <Text style={{ marginBottom: 20, color: "#64748B" }}>Start building your personalized financial view.</Text>

      {error && error.includes("already exists") ? (
        <View style={styles.existBanner}>
          <Text style={styles.existText}>An account with this email already exists.</Text>
          <Pressable style={styles.existBtn} onPress={() => router.push("/login")}>
            <Text style={styles.existBtnText}>Log In Instead ➡️</Text>
          </Pressable>
        </View>
      ) : (
        <ErrorText text={error} />
      )}

      <Field label="Full name" value={name} onChangeText={setName} />
      <Field label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" />
      <Field label="Password" value={password} onChangeText={setPassword} secureTextEntry />
      <Field label="Confirm password" value={confirm} onChangeText={setConfirm} secureTextEntry />
      <Button title={busy ? "Creating account…" : "Create account"} onPress={submit} disabled={busy} />

      <Pressable onPress={() => router.push("/login")} style={styles.linkRow}>
        <Text style={styles.linkLabel}>Already have an account? <Text style={styles.linkBold}>Log in</Text></Text>
      </Pressable>
    </Screen>
  );
}

const styles = StyleSheet.create({
  brandHeader: {
    alignItems: "center",
    marginBottom: 20,
    marginTop: 10,
  },
  existBanner: {
    backgroundColor: "#FEE2E2",
    borderColor: "#FCA5A5",
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    marginBottom: 16,
  },
  existText: {
    color: "#991B1B",
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 8,
  },
  existBtn: {
    backgroundColor: colors.purple,
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
    alignSelf: "flex-start",
  },
  existBtnText: {
    color: "#FFFFFF",
    fontSize: 13,
    fontWeight: "700",
  },
  linkRow: {
    marginTop: 20,
    alignItems: "center",
    paddingVertical: 8,
  },
  linkLabel: {
    fontSize: 14,
    color: "#64748B",
  },
  linkBold: {
    color: colors.purple,
    fontWeight: "700",
  },
});

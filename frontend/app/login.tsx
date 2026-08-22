import { useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { Button, ErrorText, Field } from "@/components/Form";
import { Screen } from "@/components/Screen";
import { BrandLogo } from "@/components/branding/BrandLogo";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/services/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string>();
  const [busy, setBusy] = useState(false);
  const { authenticate } = useAuth();

  const submit = async () => {
    setError(undefined);
    if (!email || !password) return setError("Enter your email and password.");
    setBusy(true);
    try {
      const result = await api.login(email, password);
      await authenticate(result);
      router.replace(result.onboarding_complete ? "/dashboard" : "/onboarding");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to log in.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Screen>
      <View style={styles.brandHeader}>
        <BrandLogo variant="header" />
      </View>
      <Text style={{ fontSize: 28, fontWeight: "800", marginBottom: 8 }}>Welcome back</Text>
      <Text style={{ marginBottom: 24, color: "#64748B" }}>Log in to continue your financial journey.</Text>
      <ErrorText text={error} />
      <Field label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" />
      <Field label="Password" value={password} onChangeText={setPassword} secureTextEntry />
      <Button title={busy ? "Logging in…" : "Log in"} onPress={submit} disabled={busy} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  brandHeader: {
    alignItems: "center",
    marginBottom: 20,
    marginTop: 10,
  },
});

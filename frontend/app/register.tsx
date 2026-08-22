import { useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { Button, ErrorText, Field } from "@/components/Form";
import { Screen } from "@/components/Screen";
import { BrandLogo } from "@/components/branding/BrandLogo";
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
      <Text style={{ marginBottom: 24, color: "#64748B" }}>Start building your personalized financial view.</Text>
      <ErrorText text={error} />
      <Field label="Full name" value={name} onChangeText={setName} />
      <Field label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" />
      <Field label="Password" value={password} onChangeText={setPassword} secureTextEntry />
      <Field label="Confirm password" value={confirm} onChangeText={setConfirm} secureTextEntry />
      <Button title={busy ? "Creating account…" : "Create account"} onPress={submit} disabled={busy} />
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

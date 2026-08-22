import { StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { Button } from "@/components/Form";
import { Screen } from "@/components/Screen";
import { BrandLogo } from "@/components/branding/BrandLogo";
import { colors } from "@/constants/theme";

export default function Welcome() {
  return (
    <Screen>
      <View style={styles.hero}>
        <BrandLogo variant="full" style={{ marginBottom: 12 }} />
        <Text style={styles.tagline}>Guiding Dreams. Empowering Futures.</Text>
      </View>
      <Text style={styles.copy}>
        Your personal financial companion, built around your goals and your financial journey.
      </Text>
      <Button title="Log in" onPress={() => router.push("/login")} />
      <Button title="Create account" onPress={() => router.push("/register")} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  hero: { marginTop: 30, marginBottom: 24, alignItems: "center" },
  tagline: { color: colors.purpleDark, fontWeight: "700", marginTop: 4, fontSize: 14 },
  copy: { color: colors.ink, fontSize: 16, lineHeight: 24, marginBottom: 28, textAlign: "center" },
});

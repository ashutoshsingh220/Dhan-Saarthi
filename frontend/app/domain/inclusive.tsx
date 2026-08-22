import { StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Button } from "@/components/Form";
import { colors } from "@/constants/theme";

export default function InclusiveFinanceScreen() {
  return (
    <Screen style={styles.center}>
      <Text style={styles.icon}>🤝</Text>
      <Text style={styles.kicker}>CAPABILITY DOMAIN 5</Text>
      <Text style={styles.title}>Inclusive Finance</Text>
      <Text style={styles.description}>
        Voice-first interaction, regional language support, government scheme discovery, and accessible financial tools.
      </Text>
      <View style={styles.badge}>
        <Text style={styles.badgeText}>Coming in the next development phase</Text>
      </View>
      <View style={styles.buttonContainer}>
        <Button title="Back to Dashboard" onPress={() => router.push("/(tabs)/" as any)} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  center: {
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 40,
  },
  icon: {
    fontSize: 56,
    marginBottom: 16,
  },
  kicker: {
    fontSize: 12,
    fontWeight: "800",
    color: colors.purple,
    letterSpacing: 1.2,
    marginBottom: 6,
  },
  title: {
    fontSize: 28,
    fontWeight: "800",
    color: colors.ink,
    marginBottom: 12,
    textAlign: "center",
  },
  description: {
    fontSize: 15,
    color: colors.muted,
    textAlign: "center",
    lineHeight: 22,
    marginBottom: 24,
  },
  badge: {
    backgroundColor: colors.lavender,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.purple + "33",
    marginBottom: 32,
  },
  badgeText: {
    color: colors.purple,
    fontWeight: "700",
    fontSize: 13,
  },
  buttonContainer: {
    width: "100%",
  },
});

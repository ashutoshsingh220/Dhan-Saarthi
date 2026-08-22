import { useEffect } from "react";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { useAuth } from "@/context/AuthContext";
import { colors } from "@/constants/theme";

export default function Index() {
  const { token, onboardingComplete, twin, loading } = useAuth();

  useEffect(() => {
    if (!loading) {
      if (!token) {
        router.replace("/welcome");
      } else if (!onboardingComplete) {
        router.replace("/onboarding");
      } else if (!twin) {
        router.replace("/twin");
      } else {
        router.replace("/(tabs)/" as any);
      }
    }
  }, [loading, token, onboardingComplete, twin]);

  return (
    <View style={styles.center}>
      <ActivityIndicator size="large" color={colors.purple} />
      <Text style={styles.text}>Preparing Dhan Saarthi...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.white,
  },
  text: {
    marginTop: 16,
    color: colors.muted,
    fontSize: 15,
    fontWeight: "500",
  },
});

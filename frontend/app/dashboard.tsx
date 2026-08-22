import { useEffect } from "react";
import { ActivityIndicator, StyleSheet, View } from "react-native";
import { router } from "expo-router";
import { colors } from "@/constants/theme";

export default function DashboardRedirect() {
  useEffect(() => {
    router.replace("/(tabs)/" as any);
  }, []);

  return (
    <View style={styles.center}>
      <ActivityIndicator size="large" color={colors.purple} />
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
});

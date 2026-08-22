import { ReactElement, ReactNode } from "react";
import { SafeAreaView, ScrollView, StyleProp, StyleSheet, ViewStyle } from "react-native";
import { colors } from "@/constants/theme";

export function Screen({
  children,
  style,
  refreshControl,
}: {
  children: ReactNode;
  style?: StyleProp<ViewStyle>;
  refreshControl?: ReactElement;
}) {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView
        contentContainerStyle={[styles.content, style]}
        keyboardShouldPersistTaps="handled"
        refreshControl={refreshControl}
        showsVerticalScrollIndicator={false}
      >
        {children}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.white },
  content: { padding: 24, flexGrow: 1 },
});

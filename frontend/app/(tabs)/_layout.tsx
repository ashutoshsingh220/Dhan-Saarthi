import { Tabs } from "expo-router";
import { StyleSheet, Text, View } from "react-native";
import { colors } from "@/constants/theme";
import { useLanguage } from "@/i18n/LanguageContext";

function TabIcon({ name, focused }: { name: string; focused: boolean }) {
  let symbol = "🏠";
  if (name === "saarthi") symbol = "🤖";
  if (name === "learn") symbol = "📚";
  if (name === "more") symbol = "⚙️";

  return (
    <View style={styles.iconContainer}>
      <Text style={{ fontSize: 18, opacity: focused ? 1 : 0.6 }}>{symbol}</Text>
    </View>
  );
}

export default function TabsLayout() {
  const { t } = useLanguage();

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.purple,
        tabBarInactiveTintColor: colors.muted,
        tabBarStyle: {
          backgroundColor: "#FFFFFF",
          borderTopColor: colors.border,
          height: 62,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: "600",
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: t("nav.home"),
          tabBarIcon: ({ focused }) => <TabIcon name="home" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="saarthi"
        options={{
          title: t("nav.saarthi"),
          tabBarIcon: ({ focused }) => <TabIcon name="saarthi" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="learn"
        options={{
          title: t("nav.learn"),
          tabBarIcon: ({ focused }) => <TabIcon name="learn" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="more"
        options={{
          title: t("nav.more"),
          tabBarIcon: ({ focused }) => <TabIcon name="more" focused={focused} />,
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  iconContainer: {
    alignItems: "center",
    justifyContent: "center",
  },
});

import { Tabs } from "expo-router";
import { StyleSheet, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "@/constants/theme";
import { useLanguage } from "@/i18n/LanguageContext";

function TabIcon({ name, focused }: { name: string; focused: boolean }) {
  let iconName: keyof typeof Ionicons.glyphMap = "home-sharp";
  if (name === "saarthi") iconName = "chatbubbles-sharp";
  if (name === "learn") iconName = "school-sharp";
  if (name === "more") iconName = "grid-sharp";

  return (
    <View style={[styles.iconContainer, focused && styles.focusedContainer]}>
      <Ionicons
        name={iconName}
        size={22}
        color={focused ? colors.purple : "#94a3b8"}
      />
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
        tabBarInactiveTintColor: "#64748b",
        tabBarStyle: {
          backgroundColor: "#FFFFFF",
          borderTopColor: "#e2e8f0",
          height: 64,
          paddingBottom: 8,
          paddingTop: 8,
          shadowColor: "#000",
          shadowOffset: { width: 0, height: -2 },
          shadowOpacity: 0.04,
          shadowRadius: 4,
          elevation: 4,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: "700",
          marginTop: 2,
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
    width: 40,
    height: 32,
    borderRadius: 16,
  },
  focusedContainer: {
    backgroundColor: colors.lavender + "55",
  },
});

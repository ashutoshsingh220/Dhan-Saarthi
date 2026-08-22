import React from "react";
import { StyleSheet, View } from "react-native";
import { Ionicons, MaterialCommunityIcons } from "@expo/vector-icons";

export type DomainId =
  | "saarthi"
  | "learn"
  | "recommendations"
  | "planning"
  | "market"
  | "schemes"
  | "scam"
  | "twin"
  | "more";

interface DomainIconBadgeProps {
  domain: DomainId;
  size?: "small" | "medium" | "large";
}

const DOMAIN_CONFIG: Record<
  DomainId,
  {
    bg: string;
    border: string;
    iconColor: string;
    iconName: keyof typeof Ionicons.glyphMap;
  }
> = {
  saarthi: {
    bg: "#EEF2FF",
    border: "#C7D2FE",
    iconColor: "#4F46E5",
    iconName: "chatbubbles-sharp",
  },
  learn: {
    bg: "#ECFDF5",
    border: "#A7F3D0",
    iconColor: "#059669",
    iconName: "school-sharp",
  },
  recommendations: {
    bg: "#FFFBEB",
    border: "#FDE68A",
    iconColor: "#D97706",
    iconName: "compass-sharp",
  },
  planning: {
    bg: "#F3E8FF",
    border: "#DDD6FE",
    iconColor: "#7C3AED",
    iconName: "flag-sharp",
  },
  market: {
    bg: "#E0F2FE",
    border: "#BAE6FD",
    iconColor: "#0284C7",
    iconName: "trending-up-sharp",
  },
  schemes: {
    bg: "#FEFCE8",
    border: "#FEF08A",
    iconColor: "#CA8A04",
    iconName: "business-sharp",
  },
  scam: {
    bg: "#FEE2E2",
    border: "#FCA5A5",
    iconColor: "#DC2626",
    iconName: "shield-checkmark-sharp",
  },
  twin: {
    bg: "#FCE7F3",
    border: "#FBCFE8",
    iconColor: "#DB2777",
    iconName: "sparkles-sharp",
  },
  more: {
    bg: "#F1F5F9",
    border: "#CBD5E1",
    iconColor: "#475569",
    iconName: "grid-sharp",
  },
};

export function DomainIconBadge({ domain, size = "medium" }: DomainIconBadgeProps) {
  const config = DOMAIN_CONFIG[domain] || DOMAIN_CONFIG.saarthi;

  let containerSize = 46;
  let iconSize = 22;
  let borderRadius = 14;

  if (size === "small") {
    containerSize = 34;
    iconSize = 16;
    borderRadius = 10;
  } else if (size === "large") {
    containerSize = 56;
    iconSize = 28;
    borderRadius = 18;
  }

  return (
    <View
      style={[
        styles.badge,
        {
          width: containerSize,
          height: containerSize,
          borderRadius: borderRadius,
          backgroundColor: config.bg,
          borderColor: config.border,
        },
      ]}
    >
      <Ionicons name={config.iconName} size={iconSize} color={config.iconColor} />
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 2,
    elevation: 1,
  },
});

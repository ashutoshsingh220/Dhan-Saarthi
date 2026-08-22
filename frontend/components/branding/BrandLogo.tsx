import React from "react";
import { Image, ImageStyle, StyleProp, StyleSheet, View } from "react-native";

export type BrandLogoVariant = "full" | "header" | "compact" | "onboarding" | "chat" | "footer";

interface BrandLogoProps {
  variant?: BrandLogoVariant;
  style?: StyleProp<ImageStyle>;
  accessibilityLabel?: string;
}

export const BrandLogo: React.FC<BrandLogoProps> = ({
  variant = "full",
  style,
  accessibilityLabel = "Dhan Saarthi Logo",
}) => {
  const variantStyle = styles[variant] || styles.full;

  return (
    <View style={styles.container}>
      <Image
        source={require("../../assets/branding/dhan-saarthi-logo.png")}
        style={[variantStyle, style]}
        resizeMode="contain"
        accessibilityRole="image"
        accessibilityLabel={accessibilityLabel}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
  },
  full: {
    width: 220,
    height: 155,
  },
  header: {
    width: 150,
    height: 50,
  },
  compact: {
    width: 120,
    height: 40,
  },
  onboarding: {
    width: 140,
    height: 45,
  },
  chat: {
    width: 110,
    height: 36,
  },
  footer: {
    width: 130,
    height: 42,
  },
});

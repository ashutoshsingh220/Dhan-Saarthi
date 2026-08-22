from typing import Any

ACCESSIBILITY_PROFILES = {"STANDARD", "VISUAL_ASSIST", "VOICE_ASSIST", "LOW_LITERACY", "ELDERLY_FRIENDLY"}
TEXT_SIZE_PREFERENCES = {"SMALL", "STANDARD", "LARGE", "EXTRA_LARGE"}


class AccessibilityService:
    @staticmethod
    def build_accessibility_context(profile: Any) -> dict[str, Any]:
        """
        Deterministically evaluates accessibility preferences and interaction rules.
        Does NOT infer disability or literacy ability from age, education, or occupation.
        Explicit user preferences ALWAYS take highest priority.
        """
        mode_enabled = getattr(profile, "accessibility_mode_enabled", False) or False
        raw_profile = getattr(profile, "accessibility_profile", "STANDARD") or "STANDARD"
        acc_profile = raw_profile if raw_profile in ACCESSIBILITY_PROFILES else "STANDARD"

        text_size = getattr(profile, "text_size_preference", "STANDARD") or "STANDARD"
        if text_size not in TEXT_SIZE_PREFERENCES:
            text_size = "STANDARD"

        high_contrast = getattr(profile, "high_contrast_enabled", False) or False
        reduce_motion = getattr(profile, "reduce_motion_enabled", False) or False
        simplified_iface = getattr(profile, "simplified_interface_enabled", False) or False
        voice_nav = getattr(profile, "voice_navigation_enabled", False) or False
        auto_speak = getattr(profile, "auto_speak_important_results", False) or False
        seq_nav = getattr(profile, "sequential_navigation_enabled", False) or False

        # Derived flags per accessibility profile rules
        prefer_voice = acc_profile in ("VOICE_ASSIST", "VISUAL_ASSIST") or voice_nav
        prefer_short_responses = acc_profile in ("LOW_LITERACY", "VOICE_ASSIST")
        prefer_step_by_step = acc_profile in ("VISUAL_ASSIST", "LOW_LITERACY", "ELDERLY_FRIENDLY") or seq_nav
        require_explicit_confirmation = True  # Safety rule: always active
        avoid_visual_only_references = acc_profile == "VISUAL_ASSIST"
        describe_important_results = mode_enabled or auto_speak

        rules = []

        if acc_profile == "VISUAL_ASSIST":
            rules.extend([
                "DO NOT say 'look at the graph', 'click the green button', 'see chart above', or 'the red section indicates'. Always state exact numerical values and text labels verbally.",
                "Provide step-by-step verbal explanations for all important financial figures.",
                "State key metrics clearly: 'Your financial health score is 72 out of 100.', 'Your monthly surplus is ₹8,000.'",
            ])
        elif acc_profile == "LOW_LITERACY":
            rules.extend([
                "Use short, everyday sentences and plain spoken language.",
                "Explain one financial concept at a time using concrete real-life examples.",
                "Avoid dense financial terminology, long paragraphs, and complex multi-part instructions.",
                "Provide one clear primary action recommendation before presenting alternatives.",
            ])
        elif acc_profile == "ELDERLY_FRIENDLY":
            rules.extend([
                "Use a calm, patient, slower-paced explanation style.",
                "Repeat important financial numbers clearly (e.g. 'Fifty thousand rupees (₹50,000)').",
                "Provide clear confirmation questions before moving forward to next steps.",
                "Avoid rushed multi-step instructions.",
            ])
        elif acc_profile == "VOICE_ASSIST":
            rules.extend([
                "Format responses for optimal audio listening: give a 1-sentence short answer first, key numerical fact second, and offer to explain further.",
                "Avoid reading long bulleted lists aloud.",
            ])
        else:
            rules.append("Standard interaction mode. Provide clear, supportive financial guidance.")

        if require_explicit_confirmation:
            rules.append("REQUIRE explicit user confirmation before saving or modifying any financial values (income, expenses, savings, goal targets).")

        return {
            "accessibility_mode_enabled": mode_enabled,
            "accessibility_profile": acc_profile,
            "text_size_preference": text_size,
            "high_contrast_enabled": high_contrast,
            "reduce_motion_enabled": reduce_motion,
            "simplified_interface_enabled": simplified_iface,
            "voice_navigation_enabled": voice_nav,
            "auto_speak_important_results": auto_speak,
            "sequential_navigation_enabled": seq_nav,
            "prefer_voice": prefer_voice,
            "prefer_short_responses": prefer_short_responses,
            "prefer_step_by_step": prefer_step_by_step,
            "require_explicit_confirmation": require_explicit_confirmation,
            "avoid_visual_only_references": avoid_visual_only_references,
            "describe_important_results": describe_important_results,
            "navigation_style": "SEQUENTIAL" if seq_nav or acc_profile in ("VISUAL_ASSIST", "LOW_LITERACY") else "STANDARD",
            "response_rules": rules,
        }

    @classmethod
    def build_accessibility_prompt_block(cls, profile: Any) -> list[str]:
        """
        Formats the === ACCESSIBILITY CONTEXT === block for ContextBuilder.
        """
        ctx = cls.build_accessibility_context(profile)
        lines = [
            "",
            "=== ACCESSIBILITY CONTEXT ===",
            f"Accessibility Mode: {'ENABLED' if ctx['accessibility_mode_enabled'] else 'DISABLED'}",
            f"Accessibility Profile: {ctx['accessibility_profile']}",
            f"Text Size Preference: {ctx['text_size_preference']}",
            f"High Contrast Mode: {'ENABLED' if ctx['high_contrast_enabled'] else 'DISABLED'}",
            f"Reduce Motion: {'ENABLED' if ctx['reduce_motion_enabled'] else 'DISABLED'}",
            f"Preferred Interaction: {'Voice-First' if ctx['prefer_voice'] else 'Standard'}",
            f"Navigation Style: {ctx['navigation_style']}",
            f"Avoid Visual-Only References: {'YES (CRITICAL: Do NOT mention graphs, buttons by color, or visual positions)' if ctx['avoid_visual_only_references'] else 'NO'}",
            "AI Accessibility Rules (these rules take top priority for speech & response generation):",
        ]
        for rule in ctx["response_rules"]:
            lines.append(f"  - {rule}")

        return lines

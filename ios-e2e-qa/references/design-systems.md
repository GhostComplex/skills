# Design Systems Reference

Evaluation criteria per design system. Use the section matching the project's `DESIGN_SYSTEM` config.

## Apple Liquid Glass (iOS 26+)

**Materials:** All card/container surfaces use `.ultraThinMaterial`, `.thinMaterial`, or `.regularMaterial`. No opaque solid color backgrounds on interactive elements.

**Borders:** Hairline only — `lineWidth: 0.5`, border color at `opacity(0.6)`. Never `lineWidth: 1` or full opacity.

**Shadows:** Soft, consistent depth — `opacity: 0.06+`, `radius: 4+`, slight `y` offset (1-2pt). Every floating card must have a shadow. Shadow values must be identical for cards at the same visual hierarchy level.

**Corner radius:** Use design tokens (`radiusSm: 8`, `radiusMd: 12`, `radiusLg: 16`). Never mix radii on same-level components.

**Typography:** SF Pro. Section headers with letter-spacing/tracking. Monospaced for code/paths.

**Interactions:** Spring animations for modals. Progressive disclosure for loading states (show more info as wait time increases). `.glassEffect()` on iOS 26+ with material fallback.

**Anti-patterns:**
- Opaque white/colored backgrounds on cards → use materials
- Hard 1px borders → soften to 0.5px at reduced opacity
- Custom blur overlays on system navigation → let NavigationBar handle it
- Inconsistent shadow values between same-type cards
- `Color(hex: ...)` for backgrounds that should be materials

## Apple Human Interface Guidelines (HIG, pre-iOS 26)

**Materials:** `UIBlurEffect` styles (`.systemMaterial`, `.systemUltraThinMaterial`). `Color(.systemBackground)` for standard surfaces.

**Borders:** Prefer separators (`Divider`) over strokes. If strokes needed, `Color(.separator)` at default opacity.

**Shadows:** Subtle — shadows are secondary to hierarchy established by blur and layering.

**Corner radius:** Follow system defaults (10pt for cards, continuous corners via `RoundedRectangle(cornerRadius:, style: .continuous)`).

**Anti-patterns:**
- Custom shadows that conflict with system elevation
- Non-continuous corner styles (`style: .circular`)
- Manual blur views instead of system materials

## Material Design 3 (cross-reference for hybrid apps)

**Surfaces:** Tonal surface colors from dynamic color scheme. Elevation via tonal shift, not shadow.

**Borders:** Outline variant uses `outline` color at 1pt. No heavy borders.

**Shadows:** Only for elevated components (FAB, cards, dialogs). Follows elevation system (1-5 levels).

**Corner radius:** Shape scale (Extra Small: 4, Small: 8, Medium: 12, Large: 16, Extra Large: 28, Full: 50%).

## Custom Design System

When using a custom design system:
1. Ask the user for a design spec doc or style guide
2. Extract: color tokens, border rules, shadow values, corner radii, typography scale, spacing grid
3. Create a checklist from those tokens
4. During QA, grep source files for violations of the token system (hardcoded colors, inconsistent radii, etc.)

---
name: Vian Premium Dark
colors:
  surface: '#13131b'
  surface-dim: '#13131b'
  surface-bright: '#393841'
  surface-container-lowest: '#0e0d15'
  surface-container-low: '#1b1b23'
  surface-container: '#1f1f27'
  surface-container-high: '#2a2932'
  surface-container-highest: '#34343d'
  on-surface: '#e4e1ed'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#e4e1ed'
  inverse-on-surface: '#302f38'
  outline: '#918fa0'
  outline-variant: '#464554'
  surface-tint: '#c2c1ff'
  primary: '#c2c1ff'
  on-primary: '#1800a7'
  primary-container: '#5e5ce6'
  on-primary-container: '#f4f1ff'
  inverse-primary: '#4d4ad5'
  secondary: '#c8c6c8'
  on-secondary: '#303032'
  secondary-container: '#474649'
  on-secondary-container: '#b6b4b7'
  tertiary: '#ffb786'
  on-tertiary: '#502400'
  tertiary-container: '#ae5600'
  on-tertiary-container: '#ffefe7'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c2c1ff'
  on-primary-fixed: '#0c006b'
  on-primary-fixed-variant: '#332dbc'
  secondary-fixed: '#e4e2e4'
  secondary-fixed-dim: '#c8c6c8'
  on-secondary-fixed: '#1b1b1d'
  on-secondary-fixed-variant: '#474649'
  tertiary-fixed: '#ffdcc6'
  tertiary-fixed-dim: '#ffb786'
  on-tertiary-fixed: '#311300'
  on-tertiary-fixed-variant: '#723600'
  background: '#13131b'
  on-background: '#e4e1ed'
  surface-variant: '#34343d'
typography:
  display-lg:
    fontFamily: SF Pro Display
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  h1:
    fontFamily: SF Pro Display
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  h2:
    fontFamily: SF Pro Display
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: manrope
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: manrope
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-md:
    fontFamily: manrope
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.05em
  caption:
    fontFamily: manrope
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px
  container-margin: 24px
  gutter: 16px
---

## Brand & Style
This design system embodies a "High-Tech Minimalist" aesthetic, drawing heavy inspiration from Heads-Up Displays (HUD) and premium automotive interfaces. The personality is sophisticated, precise, and utilitarian, designed for power users who value information density without visual clutter. 

The emotional response should be one of "calm control." By eliminating borders and relying on subtle tonal shifts, the UI feels expansive and seamless. The high-tech nature is reinforced through precise typography and a strict adherence to a dark, monochromatic foundation punctuated by vivid, functional accents.

## Colors
The color palette is rooted in deep blacks and charcoal grays to minimize eye strain and maximize the vibrance of the functional accents. 

- **Foundation:** The `#111111` background provides a true-dark canvas, while `#1c1c1e` is reserved for elevated containers and interactive cards.
- **Accents:** The Primary Accent (`#5e5ce6`) is used sparingly for call-to-actions and active states to maintain the HUD aesthetic.
- **Status:** Success, Warning, and Error colors utilize high-vibrance hues to ensure critical information pierces through the dark interface immediately. 
- **Grayscale:** Pure white is used for primary headings, while a muted silver-gray is used for body text to establish a clear information hierarchy.

## Typography
The typography strategy leverages a dual-font approach to balance authority with readability. 

- **Headlines:** SF Pro Display provides a clean, San Francisco-inspired precision. Use tight letter-spacing for large display sizes to create a "compact" tech feel.
- **Body & Interface:** Manrope is utilized for all functional text and body copy due to its modern geometric construction and excellent legibility at small scales. 
- **Localization:** Noto Sans KR is integrated as the fallback for Korean support, ensuring weight-matching remains consistent with the Latin characters.
- **Labels:** Use uppercase for small labels and metadata to reinforce the HUD-centric style.

## Layout & Spacing
The layout relies on a strict 8px grid system. Spacing should be used to group related elements logically without the need for visible dividers.

- **Grid:** Use a 12-column fluid grid for web views and a 4-column grid for mobile.
- **Rhythm:** Standardize horizontal and vertical padding to `16px` (md) for cards and `24px` (lg) for section spacing.
- **Negative Space:** Embrace generous margins between distinct functional groups to maintain a "minimalist" feel, even when data density is high.

## Elevation & Depth
Depth in this design system is achieved through "Tonal Layering" rather than traditional drop shadows. This creates a flat, high-tech appearance that feels like software integrated into glass.

- **Level 0 (Base):** `#111111` - The root background for the entire application.
- **Level 1 (Surface):** `#1c1c1e` - Used for primary cards, sidebars, and navigation bars.
- **Level 2 (Overlay):** `#2c2c2e` - Used for hover states, tooltips, and nested elements within Level 1 containers.
- **Interaction:** Depth is communicated by brightening the background color of an element. Do not use borders; let the contrast between `#111111` and `#1c1c1e` define the boundaries.

## Shapes
The shape language is defined by two specific radii that create a "nested" or "organic" hierarchy.

- **8px (Small):** Use for internal components such as buttons, input fields, tags, and small utility chips.
- **16px (Large):** Reserved for primary containers, cards, and modal windows.
- **Consistency:** When a small component is placed inside a large container, the difference in radii creates a balanced, modern nested effect. No elements should be sharp-edged (0px) or fully pill-shaped unless specifically used for circular profile icons.

## Components
- **Buttons:** Primary buttons use the `#5e5ce6` accent with white text. Secondary buttons are semi-transparent versions of the accent or simple Level 2 surface colors. No borders.
- **Cards:** Cards must use the `#1c1c1e` background and `16px` border-radius. Padding should be a minimum of `24px`.
- **Inputs:** Input fields should be `#1c1c1e` with an `8px` radius. On focus, change the background to a slightly lighter `#2c2c2e` rather than adding a stroke.
- **Chips & Tags:** Small, subtle elements with `8px` radius. Use muted background colors with high-contrast text for status indicators (e.g., a dark green background for Success text).
- **Lists:** List items should not have separators. Use a `16px` vertical padding and a subtle Level 2 background change on hover to indicate interactivity.
- **HUD Elements:** Incorporate small, monospaced data points or "scanlines" (subtle horizontal patterns) in the background of headers to lean into the high-tech narrative.
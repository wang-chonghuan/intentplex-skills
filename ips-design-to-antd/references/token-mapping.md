# Token mapping

How the declaration table feeds Ant Design's `ThemeConfig`. Written against Ant Design 5 and 6. Check token names against the installed version's docs (the component page's "Design Token" section) before relying on one; a misspelled component token is ignored without an error.

The examples assume a table named `S` with these entries: `primary` (theme colour), `button` (button colour), `ink`, `inkSecondary`, `inkMuted`, `tagBg`, `tagText`, `canvas` (page background), `surface` (cards, header), `border`, `borderSoft`, `fill`, `radiusCard`, `radiusPill` (999).

## Global tokens

| Token | Value | Note |
| --- | --- | --- |
| `colorPrimary` | `S.primary` | The theme colour. Ant derives hover, active and light backgrounds from it. |
| `colorLink` | `S.primary` | Set it explicitly. Left out, links stay Ant's default blue `#1677FF` even after `colorPrimary` changes. |
| `colorInfo` | `S.primary` | Same: info alerts, badges and progress stay `#1677FF` otherwise. |
| `colorText` | `S.ink` | |
| `colorTextSecondary`, `colorTextTertiary` | `S.inkSecondary` | Must pass 4.5:1 on both `surface` and `canvas`. |
| `colorTextQuaternary`, `colorTextPlaceholder` | `S.inkMuted` | |
| `colorBgLayout` | `S.canvas` | The page under the cards. |
| `colorBgContainer`, `colorBgElevated` | `S.surface` | Cards, inputs, dropdowns, modals. |
| `colorBorder` | `S.border` | Input and control borders; 3:1 against the surface. |
| `colorBorderSecondary` | `S.borderSoft` | Dividers and table rules. |
| `colorFillSecondary` | `S.fill` | Tracks such as a segmented control's. |
| `borderRadiusLG` | `S.radiusCard` | Cards, tables and panels read the large radius. Leave the base `borderRadius` alone; menus, tooltips and dropdowns use it. |
| `fontFamily` | unchanged | Only when the user chose to change the font. |

## Component tokens

### Button

```ts
Button: {
  algorithm: true,            // derive hover and pressed shades from the colorPrimary below
  colorPrimary: S.button,     // buttons alone take the button colour
  borderRadius: S.radiusPill,
  borderRadiusLG: S.radiusPill,
  borderRadiusSM: S.radiusPill,
  primaryShadow: 'none',
  defaultShadow: 'none',
  dangerShadow: 'none',
},
```

Without `algorithm: true`, a component-level `colorPrimary` changes only the resting colour; hover and pressed keep the global theme colour's shades. Keep Ant's default control heights.

### Tag

```ts
Tag: {
  defaultBg: S.tagBg,
  defaultColor: S.tagText,
  colorBorder: 'transparent',
  borderRadiusSM: S.radiusPill,
},
```

This restyles tags without a `color` prop. Tags with a preset or status colour (`success`, `red`, …) keep Ant's presets; check each one after the change.

### Card

```ts
Card: {
  colorBgContainer: S.surface,
  headerBg: S.surface,
  colorBorderSecondary: 'transparent',   // a borderless white card on the canvas
},
```

### Inputs and segmented controls

```ts
Input: { borderRadius: S.radiusPill, borderRadiusLG: S.radiusPill, borderRadiusSM: S.radiusPill },
Segmented: { borderRadius: S.radiusPill, borderRadiusLG: S.radiusPill, borderRadiusSM: S.radiusPill, borderRadiusXS: S.radiusPill },
```

Apply the pill radius to `Select`, `InputNumber` and `DatePicker` too when the reference site rounds its fields, so the controls in one form match.

### Layout, Table, Tabs, Menu

```ts
Layout: { bodyBg: S.canvas, footerBg: S.canvas, headerBg: S.surface, siderBg: S.surface },
Table: { headerBg: S.surface, borderColor: S.borderSoft, rowHoverBg: S.canvas },
Tabs: { itemColor: S.inkSecondary },
Menu: { itemColor: S.inkSecondary },
```

Unselected tabs and menu items take the secondary text colour; the selected one takes the theme colour through `colorPrimary`.

## Things the theme does not reach

- Inline styles that read `token.colorBgContainer` or a literal colour. Change them to the right token (`colorBgLayout` for page areas).
- CSS files that paint backgrounds or text. Point them at Ant's CSS variables rather than hex values (set `cssVar` in the theme if the installed version does not emit them).
- SVG and raster brand assets. These change only through the brand pipeline, and only when the user asks.
- A `ConfigProvider` nested inside the app with its own `theme`. Search for it; it overrides the root theme for its subtree.

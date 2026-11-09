---
name: ui-design-a11y
description: Build and review user interfaces for accessibility (WCAG 2.2 AA), responsive layout, design-token consistency, Tailwind CSS usage, motion and performance, framework-agnostic with Angular examples. Use when creating or reviewing components, forms, navigation, dialogs, tables, themes, dark mode, animations, or when asked about accessibility, ARIA, keyboard support, contrast, responsive design or UI polish.
license: MIT
metadata:
  version: "1.0.0"
---

# UI design & accessibility

Pairs with `angular-developer` (framework mechanics; its `references/angular-aria.md`, `tailwind-css.md`, `angular-animations.md` go deeper) and `angular-security` (sanitization). This skill is the quality bar for what the user sees and touches.

## 1. Semantics first
- Use the native element before ARIA: `button`, `a`, `input`, `select`, `dialog`, `details`, `nav`, `main`, `table`. First rule of ARIA: no ARIA is better than wrong ARIA.
- One `h1`; headings descend without skipping. Landmarks: `header`, `nav`, `main`, `footer`; label repeated landmarks.
- Click handlers belong on buttons/links, never on `div`/`span`. Links navigate; buttons act.
- Every form control has a visible `label` bound by `for`/`id`. Placeholders are not labels. Group with `fieldset`/`legend`.

## 2. Keyboard & focus
- Everything operable by keyboard in a logical order; no positive `tabindex`.
- Focus is always visible (>= 3:1 contrast, 2px+ outline). Never `outline: none` without a replacement.
- Dialogs/menus: move focus in on open, trap while modal, restore to the trigger on close, close on `Esc`.
- Route changes: move focus to the new page's `h1` or main region and update the document title.
- Targets are at least 24x24 CSS px (WCAG 2.2 2.5.8); aim for 44x44 on touch.

## 3. Color, type, motion
- Contrast: text 4.5:1 (3:1 for 18pt+/14pt bold), UI components and focus indicators 3:1. Verify in both themes.
- Never rely on color alone for state (add icon/text). Errors use text + `aria-invalid` + `aria-describedby`.
- Respect `prefers-reduced-motion` (remove parallax and large movement, keep opacity fades) and `prefers-color-scheme`.
- Nothing flashes more than 3 times per second. Auto-playing motion longer than 5s needs a pause control.
- Layout must work at 320 px width and 200% zoom without two-axis scroll; use `rem`/`clamp()`, not fixed px for text.

## 4. Live regions & feedback
- Async results, toasts and validation summaries: `role="status"` (polite) or `role="alert"` (urgent, sparingly).
- Loading states show a skeleton or spinner with an accessible name; disabled buttons explain why or stay enabled and validate on submit.
- Provide empty, loading, error and success states for every data view.

## 5. Design tokens & Tailwind
- Define color, spacing, radius, shadow, type scale and z-index as tokens (CSS variables or Tailwind theme); no magic values in components.
- Semantic names (`--color-surface`, `--color-danger`) over literal ones (`--red-500`) so themes swap cleanly.
- Tailwind: extract repeated class clusters into components, not `@apply` sprawl; keep variants (`hover:`, `focus-visible:`, `dark:`, `motion-reduce:`) explicit; purge via correct `content` globs.
- Mobile-first breakpoints; test at 320, 768, 1280.

## 6. Performance that users feel
- Reserve space for images/embeds (width/height or aspect-ratio) to avoid layout shift; lazy-load below-the-fold media; modern formats.
- Animate `transform` and `opacity` only; avoid layout-triggering properties and long main-thread tasks.
- Defer non-critical UI (Angular `@defer`), virtualize long lists, debounce expensive inputs.

## 7. Review checklist (output as findings with file:line)
1. Keyboard-only walkthrough of the primary flow succeeds.
2. Screen-reader names/roles/states are correct for custom widgets.
3. Contrast and focus visible in light + dark.
4. Reflow at 320 px / 200% zoom; reduced-motion honored.
5. Forms: labels, errors, autocomplete attributes (`autocomplete="email"` etc.), no paste blocking.
6. No unsanitized HTML sinks (`innerHTML`, `bypassSecurityTrust*`) without justification.
7. Tokens used; no one-off colors or spacing.

Tools to cite (run them when available, do not claim a result you did not obtain): axe-core / `@axe-core/playwright`, Lighthouse accessibility, `eslint-plugin-jsx-a11y` or `@angular-eslint/template` a11y rules, Pa11y.

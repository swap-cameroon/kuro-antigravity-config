---
name: mobile-engineering
description: "Build cross-platform and native mobile apps (Flutter, React Native, iOS, Android): architecture, offline, performance, security, store release. Use for mobile app design, implementation or review."
license: MIT
metadata:
  version: "1.0.0"
---

# Mobile engineering

## Choose the stack (Njoya decides with Bouba; record an ADR)
| Need | Pick |
| :-- | :-- |
| One codebase, custom UI, strong perf | Flutter |
| Web team, shared TS/React code, native widgets | React Native (Expo) |
| Deep platform APIs, max performance, platform-specific UX | Native Swift/SwiftUI + Kotlin/Compose |
| Content/forms app, no store need | PWA |
Decide on team skills, required native features, offline needs, release cadence, and long-term maintenance.

## Architecture
- Layers: UI -> state/view-model -> repository -> data sources (remote API, local DB). Unidirectional data flow. Flutter: Riverpod/Bloc; RN: React Query + Zustand/Redux Toolkit; Android: MVVM + Hilt + Room; iOS: SwiftUI + async/await + SwiftData/Core Data.
- API client generated from the OpenAPI spec (`api-design`); typed models; central error mapping; certificate-aware networking.

## Offline & sync
Local DB as source of truth for lists; optimistic updates with a retry queue; idempotency keys on writes; conflict policy defined (last-write-wins vs merge); background sync respecting battery/network (WorkManager / BGTaskScheduler); show stale-while-revalidate and clear offline states.

## Performance
Cold start budget (<2 s target) - avoid heavy work in `main`/`onCreate` - lazy-load features - virtualized lists (`ListView.builder`, `FlatList`/FlashList, `LazyColumn`) - image caching and downscaling - 60/120 fps: no work on the UI thread (isolates, JSI/worklets, coroutines) - profile with DevTools / Flipper / Instruments / Android Studio Profiler - keep app size and memory in check.

## Security (OWASP MASVS)
Tokens/secrets in Keychain/Keystore (never SharedPreferences/AsyncStorage plain) - TLS only, optional pinning with rotation plan - no secrets in the binary - biometric auth via platform APIs - deep links and intents validated - disable screenshots/clipboard on sensitive screens - root/jailbreak signals as risk input, not sole defense - obfuscation (R8/ProGuard) as defense in depth - logs scrubbed in release builds. Audit with `security-auditor` + MobSF.

## UX & accessibility
Platform conventions (back gesture, navigation patterns, haptics), touch targets >= 44x44 pt/48 dp, dynamic type/font scaling, screen-reader labels (TalkBack/VoiceOver), dark mode, safe areas, localization and RTL (`ui-design-a11y` principles).

## Release
CI builds (Fastlane/EAS/Codemagic), signing keys in a secret store, versionCode/buildNumber automation, internal -> beta (TestFlight/Play internal) -> staged rollout, crash reporting + analytics (Crashlytics/Sentry) with privacy consent, force-update mechanism and remote config/feature flags for emergencies. Follow store policies (privacy labels, data safety, review guidelines).

## Testing
Unit (logic), widget/component tests, integration/E2E (Patrol/integration_test, Detox/Maestro, XCUITest/Espresso) on real-device cloud (Firebase Test Lab/BrowserStack), golden/screenshot tests, test on low-end devices and poor networks.

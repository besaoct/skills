# Firebase Crashlytics — Cross-Platform Setup

Read this when wiring up crash/error reporting for a Flutter app. Covers all three layers that need configuration: Dart-level error boundaries, Android Gradle, and iOS Xcode build phases.

```
                  ┌──────────────────────┐
                  │ Flutter Client Code  │
                  └──────────┬───────────┘
                             │ (firebase_crashlytics SDK)
                             ▼
         ┌─────────────────────────────────────────┐
         │       Firebase Core Initialization      │
         └───────────┬─────────────────┬───────────┘
                     │                 │
      (Android Gradle build-plugin)   (iOS Run Script Build Phase)
                     ▼                 ▼
             ┌──────────────┐   ┌──────────────┐
             │ Google Play  │   │ Apple dSYMs  │
             │ Console/APIs │   │ Symbolication│
             └──────────────┘   └──────────────┘
```

## 1. Dart-Level Error Boundaries

Capture both framework-level and async-level uncaught errors — missing either leaves a real gap in crash coverage:

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

  // 1. Framework uncaught errors (widget build errors, etc.)
  FlutterError.onError = (errorDetails) {
    FirebaseCrashlytics.instance.recordFlutterFatalError(errorDetails);
  };

  // 2. Asynchronous uncaught errors (futures, streams, isolates)
  PlatformDispatcher.instance.onError = (error, stack) {
    FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
    return true;
  };
}
```

## 2. Android Build Plugins (Kotlin DSL)

In **`settings.gradle.kts`**, declare the plugin without applying it at the root:

```kotlin
plugins {
    id("com.google.firebase.crashlytics") version "3.0.2" apply false
}
```

Then apply it in **`app/build.gradle.kts`**:

```kotlin
plugins {
    id("com.google.firebase.crashlytics")
}
```

(Verify the plugin version against current releases — pinned versions age quickly.)

## 3. iOS Xcode Build Phases (`project.pbxproj`)

iOS needs a **Run Script** build phase placed **last** in the build phase order, so dSYMs are fully generated before the script runs. This compresses and uploads dSYM files needed for crash symbolication (without this, native iOS crashes show unreadable memory addresses instead of stack traces).

**Run Script command:**
```bash
"${PODS_ROOT}/FirebaseCrashlytics/run"
```

**Input paths** (all four matter — omitting the `GoogleService-Info.plist` or executable path can cause silent symbolication failures):
```
${DWARF_DSYM_FOLDER_PATH}/${DWARF_DSYM_FILE_NAME}
${DWARF_DSYM_FOLDER_PATH}/${DWARF_DSYM_FILE_NAME}/Contents/Resources/DWARF/${PRODUCT_NAME}
${DWARF_DSYM_FOLDER_PATH}/${DWARF_DSYM_FILE_NAME}/Contents/Info.plist
$(TARGET_BUILD_DIR)/$(UNLOCALIZED_RESOURCES_FOLDER_PATH)/GoogleService-Info.plist
$(TARGET_BUILD_DIR)/$(EXECUTABLE_PATH)
```

# Android Client Insights

## Permissions Required
- `INTERNET` — For C2 communication
- `ACCESS_NETWORK_STATE` — To check connectivity
- `READ_PHONE_STATE` — For device ID (Build.SERIAL)
- `FOREGROUND_SERVICE` — To keep the service alive

## Background Limitations (Android 8+)
- Foreground service with notification is required for long-running tasks
- Use `startForeground()` to avoid being killed by the system

## Testing
- Use Android Studio Emulator with API 24+
- Test on real devices for network and battery behavior
- Use `adb logcat` to monitor service output

## Future Improvements
- Add GPS exfiltration via `android.location`
- Add SMS reading via `ContentResolver`
- Add camera capture via `Camera2 API`
- Add microphone recording via `MediaRecorder`
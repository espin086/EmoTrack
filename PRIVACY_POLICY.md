# EmoTrack Privacy Policy

**Last Updated:** April 2026

## Overview

EmoTrack is a real-time emotion detection application that analyzes facial expressions using your device's camera. Your privacy is important to us.

## Data Collection

### Camera Data
- EmoTrack uses your device's camera to detect facial expressions in real-time.
- **All processing happens entirely on your device.** No images or video data are sent to any server, cloud service, or third party.
- Camera frames are processed in memory and immediately discarded after emotion detection.

### Emotion Data
- Detected emotions (e.g., "HAPPY", "SAD") are stored locally on your device in a SQLite database.
- This data never leaves your device.
- You can export or delete all stored emotion data at any time from the Settings tab.

## Data Storage

- All data is stored locally in `~/Library/Application Support/EmoTrack/` on macOS.
- No data is transmitted over the network.
- No analytics, telemetry, or crash reporting data is collected.

## Third-Party Services

EmoTrack does **not** use any third-party services, APIs, or SDKs that collect user data. Emotion detection is performed using an on-device machine learning model.

## Data Deletion

You can delete all stored emotion data at any time:
1. Open EmoTrack
2. Go to the Settings tab
3. Click "Clear All Data" in the Danger Zone section

Uninstalling the application will remove the app but may leave the database file. To fully remove all data, delete the `~/Library/Application Support/EmoTrack/` directory.

## Children's Privacy

EmoTrack does not knowingly collect data from children under 13.

## Changes to This Policy

We may update this privacy policy from time to time. Changes will be reflected in the "Last Updated" date above.

## Contact

For questions about this privacy policy, please open an issue on the EmoTrack GitHub repository.

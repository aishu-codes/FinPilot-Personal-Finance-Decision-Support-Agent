# FinPilot Mobile Android SMS Listener Setup

This directory contains the Android Kotlin implementation for listening to incoming SMS messages on a user's device and securely posting them to FinPilot.

## Android Integration Setup

1. **Add Permissions to `AndroidManifest.xml`**:
   ```xml
   <uses-permission android.permission.RECEIVE_SMS />
   <uses-permission android.permission.READ_SMS />
   <uses-permission android.permission.INTERNET />
   ```

2. **Register the BroadcastReceiver in `AndroidManifest.xml`**:
   ```xml
   <receiver
       android.name=".sms.SMSBroadcastReceiver"
       android.permission="android.permission.BROADCAST_SMS"
       android.exported="true">
       <intent-filter android:priority="999">
           <action android:name="android.provider.Telephony.SMS_RECEIVED" />
       </intent-filter>
   </receiver>
   ```

3. **Configure Backend URL**:
   In `SMSBroadcastReceiver.kt`, update `serverUrl`:
   - Android Emulator: `http://10.0.2.2:8000/api/sms/process`
   - Real Physical Device on Wi-Fi: `http://<YOUR_LOCAL_IP>:8000/api/sms/process`

4. **Request Runtime SMS Permission**:
   ```kotlin
   ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECEIVE_SMS), 101)
   ```

5. **How It Works**:
   - When an SMS arrives on the user's phone, `SMSBroadcastReceiver` intercepts the payload.
   - It sends a JSON POST request to `POST /api/sms/process`.
   - FinPilot automatically sanitizes OTPs/PINs, runs scam/fraud detection, extracts amounts and merchants, checks for duplicates, and updates the financial dashboard.

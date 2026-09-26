package com.finpilot.app.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

/**
 * FinPilot Mobile Android SMS Listener
 * Captures incoming SMS messages and securely posts them to the FinPilot FastAPI Backend.
 * 
 * Required Permissions in AndroidManifest.xml:
 * <uses-permission android.permission.RECEIVE_SMS />
 * <uses-permission android.permission.READ_SMS />
 * <uses-permission android.permission.INTERNET />
 */
class SMSBroadcastReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
            val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
            for (sms in messages) {
                val sender = sms.displayOriginatingAddress ?: "UNKNOWN_SENDER"
                val body = sms.displayMessageBody ?: continue

                Log.d("FinPilotSMS", "Received SMS from $sender: $body")

                // Forward incoming SMS payload to FinPilot Backend Server
                sendSmsToFinPilotBackend(sender, body)
            }
        }
    }

    private fun sendSmsToFinPilotBackend(sender: String, smsText: String) {
        thread {
            try {
                // Change to your server IP/host (e.g. http://192.168.1.100:8000/api/sms/process)
                val serverUrl = URL("http://10.0.2.2:8000/api/sms/process")
                val conn = serverUrl.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                conn.doOutput = true

                val jsonPayload = JSONObject().apply {
                    put("sms_text", smsText)
                    put("sender", sender)
                    put("timestamp", System.currentTimeMillis().toString())
                }

                val writer = OutputStreamWriter(conn.outputStream)
                writer.write(jsonPayload.toString())
                writer.flush()
                writer.close()

                val responseCode = conn.responseCode
                Log.d("FinPilotSMS", "Server response code: $responseCode")
            } catch (e: Exception) {
                Log.e("FinPilotSMS", "Failed to send SMS to FinPilot backend", e)
            }
        }
    }
}

import resend
import os
from django.conf import settings

resend.api_key = os.environ.get('RESEND_API_KEY')

def send_otp_email(to_email: str, username: str, otp: str) -> bool:
    try:
        params = {
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": "Your Login OTP - RAG SQL Assistant",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #1a1a2e; padding: 30px; border-radius: 10px;">
                    <h1 style="color: #ffffff; text-align: center;">🧠 RAG SQL Assistant</h1>
                    <div style="background: #16213e; padding: 20px; border-radius: 8px; margin-top: 20px;">
                        <p style="color: #9ca3af;">Hello <strong style="color: #ffffff;">{username}</strong>,</p>
                        <p style="color: #9ca3af;">Your One-Time Password (OTP) is:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <span style="background: #3b82f6; color: white; font-size: 32px; 
                                         font-weight: bold; padding: 15px 30px; border-radius: 8px; 
                                         letter-spacing: 8px;">
                                {otp}
                            </span>
                        </div>
                        <p style="color: #9ca3af;">This OTP expires in <strong style="color: #ffffff;">10 minutes</strong>.</p>
                        <p style="color: #6b7280; font-size: 12px;">
                            If you didn't request this, please ignore this email.
                        </p>
                    </div>
                </div>
            </div>
            """,
        }
        resend.Emails.send(params)
        print(f"✅ OTP email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        return False
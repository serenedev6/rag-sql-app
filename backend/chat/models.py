from django.db import models
from django.contrib.auth.models import User


class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    mode = models.CharField(max_length=10, default='rag')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.question[:50]}"
    

import random
import string
from django.utils import timezone
from datetime import timedelta

class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self):
        # OTP valid for 10 minutes
        expiry = self.created_at + timedelta(minutes=10)
        return not self.is_used and timezone.now() < expiry

    @classmethod
    def generate_otp(cls, user):
        # Delete old OTPs for this user
        cls.objects.filter(user=user).delete()
        # Generate new 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        return cls.objects.create(user=user, otp=otp)

    def __str__(self):
        return f"{self.user.username} - {self.otp}"
    
import pyotp

class TOTPDevice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_key = models.CharField(max_length=32)
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - TOTP {'enabled' if self.is_enabled else 'disabled'}"

    @classmethod
    def generate_secret(cls):
        return pyotp.random_base32()

    def get_totp(self):
        return pyotp.TOTP(self.secret_key)

    def verify_token(self, token):
        totp = self.get_totp()
        return totp.verify(token, valid_window=1)

    def get_qr_code_url(self):
        totp = self.get_totp()
        return totp.provisioning_uri(
            name=self.user.email or self.user.username,
            issuer_name="RAG SQL Assistant"
        )
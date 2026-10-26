"""
Email Delivery Service for SuchnaSetu AI.
Supports:
- "console" backend: Development and test mode (safe, logs dispatch without network transmission)
- "smtp" backend: Production delivery with STARTTLS, timeout handling, and MIME formatting
"""

import asyncio
import smtplib
import ssl
import socket
import email.utils
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from notice2action.config import config

logger = logging.getLogger("notice2action.auth.email")


class EmailDeliveryResult:
    def __init__(self, success: bool, message: str, backend: str):
        self.success = success
        self.message = message
        self.backend = backend


def _mask_email(addr: str) -> str:
    if not addr or "@" not in addr:
        return "unknown"
    user, domain = addr.split("@", 1)
    masked_user = user[:2] + "***" if len(user) > 2 else "***"
    return f"{masked_user}@{domain}"


class EmailService:
    """Civic notice platform email service supporting configurable SMTP and safe development console delivery."""

    @property
    def backend(self) -> str:
        return getattr(config, "auth_email_backend", "console").lower()

    @property
    def from_email(self) -> str:
        from_env = getattr(config, "smtp_from_email", "SuchnaSetu AI <notifications@example.com>")
        smtp_user = getattr(config, "smtp_username", None)
        if from_env and "example.com" not in from_env:
            return from_env
        if smtp_user and "@" in smtp_user:
            return f"SuchnaSetu AI <{smtp_user}>"
        return from_env

    @property
    def app_url(self) -> str:
        return getattr(config, "auth_public_app_url", "http://localhost:5173").rstrip("/")

    def _render_base_html(self, title: str, subtitle: str, body_html: str, action_url: Optional[str] = None, action_label: Optional[str] = None) -> str:
        """Render responsive, accessible, branded SuchnaSetu AI HTML email."""
        action_button = ""
        if action_url and action_label:
            action_button = f"""
            <div style="margin: 28px 0; text-align: center;">
                <a href="{action_url}" style="background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; padding: 12px 28px; font-size: 15px; font-weight: 600; text-decoration: none; border-radius: 8px; display: inline-block; box-shadow: 0 4px 12px rgba(4, 120, 87, 0.25);">
                    {action_label}
                </a>
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #0f172a;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 32px 16px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" style="max-width: 580px; background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #064e3b; padding: 24px 32px; text-align: left;">
                            <div style="font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                                SuchnaSetu AI <span style="font-size: 14px; font-weight: 500; color: #a7f3d0; margin-left: 6px;">सूचना + सेतु</span>
                            </div>
                            <div style="font-size: 12px; color: #6ee7b7; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">
                                Citizen Notice Accessibility Platform
                            </div>
                        </td>
                    </tr>
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 32px;">
                            <h1 style="font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 0; margin-bottom: 8px;">
                                {title}
                            </h1>
                            <p style="font-size: 14px; color: #475569; margin-top: 0; margin-bottom: 24px; line-height: 1.5;">
                                {subtitle}
                            </p>
                            <div style="font-size: 14px; line-height: 1.6; color: #334155;">
                                {body_html}
                            </div>
                            {action_button}
                            <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 28px 0 20px;" />
                            <p style="font-size: 12px; color: #64748b; line-height: 1.5; margin: 0;">
                                If you did not make this request or have questions, you can safely ignore this email. This is an automated notification from SuchnaSetu AI.
                            </p>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 16px 32px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 12px; color: #94a3b8;">
                            SuchnaSetu AI &bull; PS 02 Notice-to-Action Accessibility Assistant &bull; Open Governance
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    async def _send_smtp(self, recipient: str, subject: str, text_content: str, html_content: str) -> EmailDeliveryResult:
        """Send email via configured SMTP server using thread executor to avoid blocking event loop."""
        if hasattr(config, "validate_smtp_config"):
            is_valid, err_msg = config.validate_smtp_config()
            if not is_valid:
                logger.error(f"SMTP configuration error: {err_msg}")
                return EmailDeliveryResult(False, f"SMTP delivery failed: {err_msg}", "smtp")

        smtp_host = getattr(config, "smtp_host", "localhost")
        smtp_port = int(getattr(config, "smtp_port", 587))
        smtp_user = getattr(config, "smtp_username", None)
        smtp_pass = getattr(config, "smtp_password", None)
        smtp_tls = getattr(config, "smtp_use_tls", True)

        def _do_send():
            logger.info(f"Rendering MIME email: subject='{subject}', recipient={_mask_email(recipient)}")
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = recipient
            msg["Date"] = email.utils.formatdate(localtime=True)

            parsed_from = email.utils.parseaddr(self.from_email)[1]
            from_domain = parsed_from.split("@")[-1] if "@" in parsed_from else "suchnasetu.gov.in"
            msg["Message-ID"] = email.utils.make_msgid(domain=from_domain)
            msg["Auto-Submitted"] = "auto-generated"
            msg["X-Auto-Response-Suppress"] = "All"

            part1 = MIMEText(text_content, "plain", "utf-8")
            part2 = MIMEText(html_content, "html", "utf-8")
            msg.attach(part1)
            msg.attach(part2)

            envelope_from = parsed_from
            if smtp_user and "@" in smtp_user:
                envelope_from = smtp_user

            logger.info(f"Connecting to SMTP {smtp_host}:{smtp_port} (timeout=20s)...")
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                server.ehlo()
                if smtp_tls:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                    server.ehlo()

                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)

                refused = server.sendmail(envelope_from, [recipient], msg.as_string())
                if refused:
                    raise smtplib.SMTPRecipientsRefused(refused)

        try:
            await asyncio.to_thread(_do_send)
            logger.info(f"Email successfully delivered via SMTP to recipient={_mask_email(recipient)}")
            return EmailDeliveryResult(True, "Email accepted by mail server for delivery", "smtp")
        except smtplib.SMTPAuthenticationError:
            logger.error(f"SMTP authentication failure to {smtp_host}:{smtp_port}")
            return EmailDeliveryResult(False, "Mail server authentication failed.", "smtp")
        except smtplib.SMTPRecipientsRefused:
            logger.error(f"SMTP recipient refused by server: {_mask_email(recipient)}")
            return EmailDeliveryResult(False, "Recipient address refused by mail server.", "smtp")
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, socket.timeout, TimeoutError, OSError) as e:
            logger.error(f"SMTP connection failure to {smtp_host}:{smtp_port}: {e}")
            return EmailDeliveryResult(False, "Temporary connection failure to mail server.", "smtp")
        except Exception as e:
            logger.error(f"SMTP transmission error: {type(e).__name__} - {e}")
            return EmailDeliveryResult(False, f"SMTP transmission failed: {type(e).__name__}", "smtp")

    async def _send_console(self, recipient: str, subject: str, text_content: str) -> EmailDeliveryResult:
        """
        Console development adapter.
        Safely logs message delivery in development so developers and local users can inspect verification links and OTP codes.
        """
        logger.info(
            f"[DEV CONSOLE EMAIL] Dispatch to {recipient} | Subject: '{subject}'\n"
            f"--------------------------------------------------\n"
            f"{text_content.strip()}\n"
            f"--------------------------------------------------"
        )
        return EmailDeliveryResult(
            True,
            "Email dispatched to development console logger (no external network transmission)",
            "console"
        )

    async def send_email(self, recipient: str, subject: str, text_content: str, html_content: str) -> EmailDeliveryResult:
        """Dispatch email according to configured backend."""
        if self.backend == "smtp":
            return await self._send_smtp(recipient, subject, text_content, html_content)
        return await self._send_console(recipient, subject, text_content)

    async def send_verification_email(self, email: str, name: str, token: str, code: str) -> EmailDeliveryResult:
        """Send email verification link and one-time code to activate account."""
        verify_url = f"{self.app_url}/verify-email?token={token}&email={email}"
        subject = "Verify your SuchnaSetu AI account"

        body_html = f"""
        <p>Namaste {name},</p>
        <p>Thank you for registering on <strong>SuchnaSetu AI</strong>. To access official notice intelligence and citizen action roadmaps, please verify your email address.</p>
        <p>You can verify your account by clicking the button below:</p>
        <div style="background-color: #ecfdf5; border-left: 4px solid #059669; padding: 14px 18px; margin: 20px 0; border-radius: 0 8px 8px 0;">
            <p style="margin: 0; font-size: 13px; color: #065f46; font-weight: 600;">Or enter this 6-digit verification code on the verification page:</p>
            <p style="margin: 8px 0 0; font-size: 26px; font-weight: 800; letter-spacing: 6px; color: #047857;">{code}</p>
        </div>
        <p style="font-size: 13px; color: #64748b;">This verification code will expire in 24 hours.</p>
        """

        text_content = f"""Namaste {name},

Thank you for registering on SuchnaSetu AI.
Please verify your email address to activate your account.

Verification Link:
{verify_url}

Or enter your 6-digit verification code:
{code}

This code will expire in 24 hours.

— SuchnaSetu AI Team
"""

        html_content = self._render_base_html(
            title="Verify Your Email Address",
            subtitle="Complete your registration to unlock citizen notice intelligence",
            body_html=body_html,
            action_url=verify_url,
            action_label="Verify Email Address"
        )

        return await self.send_email(email, subject, text_content, html_content)

    async def send_password_reset_link(self, email: str, name: str, token: str) -> EmailDeliveryResult:
        """Send secure password reset link."""
        reset_url = f"{self.app_url}/reset-password?token={token}&email={email}"
        subject = "Reset your SuchnaSetu AI password"

        body_html = f"""
        <p>Hello {name},</p>
        <p>We received a request to reset your password for your <strong>SuchnaSetu AI</strong> account.</p>
        <p>Click the button below to choose a new password. This single-use link expires in <strong>15 minutes</strong>:</p>
        """

        text_content = f"""Hello {name},

We received a request to reset your password for your SuchnaSetu AI account.
Click or copy the link below to choose a new password:

{reset_url}

This single-use link expires in 15 minutes.
If you did not request a password reset, please ignore this email.

— SuchnaSetu AI Team
"""

        html_content = self._render_base_html(
            title="Password Reset Request",
            subtitle="Instructions to choose a new secure password",
            body_html=body_html,
            action_url=reset_url,
            action_label="Reset Password"
        )

        return await self.send_email(email, subject, text_content, html_content)

    async def send_password_reset_code(self, email: str, name: str, code: str) -> EmailDeliveryResult:
        """Send secure one-time 6-digit recovery code."""
        subject = "Your SuchnaSetu AI password recovery code"

        body_html = f"""
        <p>Hello {name},</p>
        <p>We received a request to recover your password for your <strong>SuchnaSetu AI</strong> account using a one-time recovery code.</p>
        <p>Use the following 6-digit code on the reset password screen:</p>
        <div style="background-color: #f0fdf4; border: 2px dashed #10b981; padding: 16px; margin: 20px 0; border-radius: 8px; text-align: center;">
            <div style="font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #065f46;">{code}</div>
        </div>
        <p style="font-size: 13px; color: #64748b;">
            This recovery code expires in <strong>15 minutes</strong> and is strictly single-use.
        </p>
        """

        text_content = f"""Hello {name},

We received a request to recover your password for your SuchnaSetu AI account.
Your 6-digit one-time recovery code is:

{code}

This code expires in 15 minutes and can only be used once.
If you did not request this code, please ignore this email.

— SuchnaSetu AI Team
"""

        html_content = self._render_base_html(
            title="One-Time Recovery Code",
            subtitle="Enter this code to set a new password",
            body_html=body_html
        )

        return await self.send_email(email, subject, text_content, html_content)

    async def send_password_changed_notification(self, email: str, name: str) -> EmailDeliveryResult:
        """Send notification confirming that the account password was successfully updated."""
        subject = "Your SuchnaSetu AI password has been changed"

        body_html = f"""
        <p>Hello {name},</p>
        <p>This is a confirmation that your password for your <strong>SuchnaSetu AI</strong> account was recently changed.</p>
        <p>All previous active sessions have been securely signed out. You can now log in with your new password.</p>
        <div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px 16px; margin: 18px 0; border-radius: 0 6px 6px 0; font-size: 13px; color: #92400e;">
            If you did not authorize this change, please contact support or reset your password immediately.
        </div>
        """

        text_content = f"""Hello {name},

This is a confirmation that your password for your SuchnaSetu AI account was recently changed.
All existing sessions have been signed out. You can now log in with your new password.

If you did not authorize this change, please reset your password immediately.

— SuchnaSetu AI Team
"""

        html_content = self._render_base_html(
            title="Password Changed Successfully",
            subtitle="Security update for your account",
            body_html=body_html
        )

        return await self.send_email(email, subject, text_content, html_content)


email_service = EmailService()

import html


def verification_email_html(full_name: str, verification_link: str, expire_hours: int) -> str:
    safe_name = html.escape(full_name)
    return f"""\
<!DOCTYPE html>
<html>
  <body style="font-family: sans-serif; color: #1a1a1a;">
    <p>Hi {safe_name},</p>
    <p>Thanks for signing up for APISense. Please verify your email address to activate your account:</p>
    <p>
      <a href="{verification_link}" style="background:#2563eb;color:#fff;padding:10px 20px;
         border-radius:6px;text-decoration:none;display:inline-block;">
        Verify email
      </a>
    </p>
    <p>Or copy and paste this link into your browser:<br>{verification_link}</p>
    <p>This link expires in {expire_hours} hours. If you didn't create an account, you can ignore this email.</p>
  </body>
</html>
"""


def password_reset_email_html(full_name: str, reset_link: str, expire_minutes: int) -> str:
    safe_name = html.escape(full_name)
    return f"""\
<!DOCTYPE html>
<html>
  <body style="font-family: sans-serif; color: #1a1a1a;">
    <p>Hi {safe_name},</p>
    <p>We received a request to reset your APISense account password. Click below to choose a new one:</p>
    <p>
      <a href="{reset_link}" style="background:#2563eb;color:#fff;padding:10px 20px;
         border-radius:6px;text-decoration:none;display:inline-block;">
        Reset password
      </a>
    </p>
    <p>Or copy and paste this link into your browser:<br>{reset_link}</p>
    <p>This link expires in {expire_minutes} minutes. If you didn't request a password reset, you can safely ignore this email — your password will not be changed.</p>
  </body>
</html>
"""

# Email Setup for Contact Form

The contact form sends messages to **v2s.millexa@gmail.com**.

## Enable sending via Gmail SMTP:

1. Go to https://myaccount.google.com → Security → 2-Step Verification (enable it)
2. Then go to → App Passwords → create an app password for "Mail"
3. Copy the 16-character app password

## Set environment variables before running:

```bash
# Windows (PowerShell)
$env:GMAIL_USER = "v2s.millexa@gmail.com"
$env:GMAIL_APP_PASSWORD = "v2smillexa2026"

# Linux/Mac
export GMAIL_USER="v2s.millexa@gmail.com"
export GMAIL_APP_PASSWORD="v2smillexa2026"
```

Then run:
```bash
uvicorn main:app --reload
```

## Notes:
- Without the app password set, the form still shows "success" to the user but the email is logged as an error. No crash.
- The form captures: Name, Email, Phone, Subject, Message — all sent as a formatted HTML email.

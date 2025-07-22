# 📧 Gmail Resume Sender with Google Sheets Integration

This Python script automates personalized resume emails by reading contact names and email addresses from a Google Sheet and sending them via Gmail with your resume attached.

---

## 🔧 Features

- ✅ Reads contacts (First Name, Email) from Google Sheets
- ✅ Sends personalized emails using Gmail API
- ✅ Attaches a PDF resume to each message
- ✅ Handles OAuth2 authentication securely
- ✅ Includes error handling and basic logging

---

## 🔐 Requirements

- Python 3.7+
- A Google Cloud project with:
  - Gmail API enabled
  - Google Sheets API enabled
- `credentials.json` OAuth2 file from Google Cloud Console

---

## 📁 File Structure

```bash
📂 project-directory
│
├── credentials.json         # OAuth2 credentials (keep safe)
├── token.json               # Auto-generated OAuth token
├── resume.pdf               # Your resume (PDF)
├── main.py                  # Main script (this repo)
├── README.md                # This file

import base64
import os
import mimetypes
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ------------ CONFIGURATION ------------

# Google API scopes required for Gmail and Sheets access
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/spreadsheets.readonly']

# Google Sheets ID and range to fetch contacts (masking sensitive ID for public use)
SHEET_ID = 'YOUR_SHEET_ID_HERE'  # Replace with your actual Google Sheet ID
RANGE_NAME = 'Sheet1!A2:B'       # Assumes first row is header

# Resume file attachment path (PDF file should be in same directory)
ATTACHMENT_PATH = os.path.join(os.path.dirname(__file__), 'resume.pdf')

# Email subject and body template (personalized per contact)
EMAIL_SUBJECT = "Experienced Data Engineer Seeking Opportunities"

EMAIL_BODY_TEMPLATE = """Dear {{First name}},

As a certified Data Engineer with over 5 years of experience building secure, scalable data platforms across AWS, Azure, and GCP, I bring a proven track record of developing automated, high-performance ETL/ELT pipelines that drive business value in healthcare, insurance, and retail sectors. ...

Sincerely,<br>
Asish Madduri<br>
716-444-5231<br>
asishmadduri10@gmail.com<br>
<a href="https://www.linkedin.com/in/asish-madduri/">LinkedIn Profile</a>
"""

# ------------ AUTHENTICATE GMAIL & SHEETS ------------
def authenticate_gmail_and_sheets():
    """Authenticate user and return credentials for Gmail & Sheets APIs."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # credentials.json is the OAuth2 file downloaded from Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for future runs
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# ------------ READ CONTACTS FROM GOOGLE SHEET ------------
def get_contacts(service):
    """Read first name and email columns from Google Sheet."""
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    return result.get('values', [])  # Each row: [First name, Email]

# ------------ COMPOSE EMAIL WITH ATTACHMENT ------------
def create_message_with_attachment(to, subject, body_text, attachment_path):
    """Create email message with HTML body and attached PDF."""
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body_text.replace("\n", "<br>"), 'html'))

    if not os.path.exists(attachment_path):
        raise FileNotFoundError(f"Attachment not found: {attachment_path}")

    content_type, encoding = mimetypes.guess_type(attachment_path)
    content_type = content_type or 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)

    with open(attachment_path, 'rb') as f:
        file_part = MIMEBase(main_type, sub_type)
        file_part.set_payload(f.read())
        encoders.encode_base64(file_part)
        file_part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
        message.attach(file_part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

# ------------ MAIN FUNCTION TO SEND EMAILS ------------
def send_emails():
    """Main function to authenticate, fetch contacts, and send emails."""
    creds = authenticate_gmail_and_sheets()
    gmail_service = build('gmail', 'v1', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)

    rows = get_contacts(sheets_service)

    for row in rows:
        if len(row) < 2:
            continue  # Skip incomplete rows
        first_name, email = row
        try:
            capitalized_name = first_name.strip().capitalize()
            personalized_body = EMAIL_BODY_TEMPLATE.replace("{{First name}}", capitalized_name)
            message = create_message_with_attachment(email, EMAIL_SUBJECT, personalized_body, ATTACHMENT_PATH)
            gmail_service.users().messages().send(userId='me', body=message).execute()
            print(f"✅ Email sent to {capitalized_name} at {email}")
        except Exception as e:
            print(f"❌ Failed to send to {email}: {e}")
        time.sleep(2)  # Sleep to prevent API rate limits

# ------------ RUN SCRIPT ------------
if __name__ == '__main__':
    send_emails()

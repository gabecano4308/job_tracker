import base64
import os
from datetime import datetime
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scope for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailService():
    def __init__(self, to, message_text):
        self.service = gmail_service()
        self.sender = "me"
        self.subject = "Job Search Results: " + datetime.now().strftime("%Y-%m-%d")
        self.to = to
        self.message_text = message_text
        
    def create_and_send_message(self):
        msg = self.create_message(self.sender, self.to, self.subject, self.message_text)
        self.send_message(self.service, self.sender, msg)
    
    def create_message(self, sender, to, subject, message_text):
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw}
    
    def send_message(self, service, user_id, message):
        return service.users().messages().send(userId=user_id, body=message).execute()


def gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

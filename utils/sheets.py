import os
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
load_dotenv()

def authenticate_google_sheets():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        os.getenv('GOOGLE_SHEETS_CREDENTIALS'),
        ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    )
    return gspread.authorize(creds)

def get_worksheet():
    client = authenticate_google_sheets()
    return client.open_by_key(os.getenv('SPREADSHEET_ID')).worksheet(os.getenv('SHEET_NAME'))
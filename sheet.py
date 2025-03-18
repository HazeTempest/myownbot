import os
import gspread
import dotenv
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
dotenv.load_dotenv()

# Authenticate with Google Sheets API
def authenticate_google_sheets():
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client

# Get the last message from the sheet
def post_from_spreadsheet():
    # Authenticate
    client = authenticate_google_sheets()

    # Open the spreadsheet
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    spreadsheet = client.open_by_key(spreadsheet_id)

    # Print all worksheet names for debugging
    worksheets = spreadsheet.worksheets()
    print("Worksheets in the spreadsheet:")
    for ws in worksheets:
        print(ws.title)

    # Try to access the specific worksheet
    sheet_name = os.getenv('SHEET_NAME')
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        print(f"Worksheet '{sheet_name}' not found!")
        return

    # Find the last row with data in column B
    column_b_data = worksheet.col_values(2)  # Get all values in column B
    last_row_with_data = len(column_b_data)  # Last row with data

    # Get the value of the cell in column A of the next row
    message_cell = worksheet.cell(last_row_with_data + 1, 1)  # Column A is index 1
    current_message = message_cell.value

    print(current_message)

# Run the function
if __name__ == "__main__":
    post_from_spreadsheet()
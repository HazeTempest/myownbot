## Simple Discord Bot for Reminder and Google Sheet Integration

### Installation
> ```bash
> git clone https://github.com/ghostselfbot/ghost
> python3 -m venv .venv
> source .venv/bin/activate
> pip install -r requirements.txt
> python3 bot.py
> ```
> _requires Python 3.10+_
### How to Get Values for .env
- **Discord Token**: Create a bot in the Discord Developer Portal and copy the token.
- **Google Credentials**: Set up a Service Account in Google Cloud, enable Sheets API, and download the JSON key.
- **Spreadsheet ID**: Extract from the URL of your Google Sheet (e.g., `https://docs.google.com/spreadsheets/d/[ID]/edit`).
- **User IDs**: Enable Developer Mode in Discord, right-click a user, and copy their ID.

> [!WARNING]  
> Using this bot can and will result in account termination if not used carefully! To avoid termination do not use any commands within big servers especially ones moderated by Discord staff and do not abuse commands. I would also recommend using this bot on phone verified accounts!
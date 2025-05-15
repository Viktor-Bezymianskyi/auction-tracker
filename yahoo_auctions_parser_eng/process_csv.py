import csv
from datetime import datetime
from googletrans import Translator
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from parse_auctions import convert_to_zenmarket_url
import re
import os
import argparse
import time
import shutil
from search_config.quantity_extractor import extract_quantity
from search_config.status_extractor import extract_status
from search_config.excluded_words import is_excluded
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Settings (now taken from .env)
CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
YEN_TO_EUR = float(os.getenv('YEN_TO_EUR', '165'))
RESULTS_DIR = "results"
ARCHIVE_DIR = "results_archive"


def create_new_spreadsheet():
    """Creates a new spreadsheet with current date"""
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE, scope)
    gc = gspread.authorize(creds)

    # Generate spreadsheet name
    spreadsheet_name = f"yahoo_{datetime.now().strftime('%Y%m%d_%H%M')}"

    try:
        spreadsheet = gc.create(spreadsheet_name)
        # Grant access to your email (replace with yours)
        spreadsheet.share(os.getenv('GOOGLE_SHEETS_EMAIL'),
                          perm_type='user', role='writer')
        print(f"New spreadsheet created: {spreadsheet_name}")
        return spreadsheet
    except Exception as e:
        print(f"Error creating spreadsheet: {e}")
        raise


def archive_file(filepath):
    """Moves file to archive directory"""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    try:
        shutil.move(filepath, os.path.join(
            ARCHIVE_DIR, os.path.basename(filepath)))
        print(f"File moved to archive: {ARCHIVE_DIR}")
    except Exception as e:
        print(f"Error archiving file: {e}")


def process_all_results(date_override=None):
    """Processes all CSV files from results directory"""
    if not os.path.exists(RESULTS_DIR):
        print(f"Directory {RESULTS_DIR} not found")
        return

    try:
        # Create new spreadsheet
        spreadsheet = create_new_spreadsheet()
        time.sleep(5)  # Wait for spreadsheet creation
    except Exception:
        return

    # Google Sheets authorization
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE, scope)
    gc = gspread.authorize(creds)

    for filename in os.listdir(RESULTS_DIR):
        if filename.endswith('.csv'):
            filepath = os.path.join(RESULTS_DIR, filename)
            print(f"\nProcessing file: {filename}")

            # Generate sheet name (remove date and limit length)
            sheet_name = re.sub(r'_\d{8}_\d{4}\.csv$', '', filename)[:100]

            try:
                # Create new worksheet
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name, rows="1000", cols="20")
                time.sleep(2)

                # Prepare data
                translator = Translator()
                batch_data = []

                with open(filepath, mode='r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        try:
                            title = row['Item Title']
                            if is_excluded(title):
                                continue

                            qty = extract_quantity(title)
                            status = extract_status(title)

                            try:
                                title_en = translator.translate(
                                    title, src='ja', dest='en').text
                            except Exception as e:
                                print(f"Translation error: {e}")
                                title_en = title

                            add_date = date_override if date_override else datetime.now().strftime('%Y-%m-%d %H:%M')

                            batch_data.append([
                                title_en or '',
                                round(int(row['Price (¥)']) / YEN_TO_EUR, 2),
                                qty,
                                convert_to_zenmarket_url(row['URL']),
                                row['End Time'],
                                add_date,
                                status or '',
                                row['Price (¥)']
                            ])
                        except Exception as e:
                            print(f"Error processing row: {e}")
                            continue

                # Write headers
                headers = [
                    'Title', 'Price (EUR)', 'Quantity', 'URL',
                    'End Time', 'Added Date', 'Status', 'Price (JPY)'
                ]
                worksheet.append_row(headers)
                time.sleep(1)

                # Batch insert data
                batch_size = 100
                for i in range(0, len(batch_data), batch_size):
                    chunk = batch_data[i:i + batch_size]
                    worksheet.append_rows(chunk)
                    print(f"Added {len(chunk)} rows...")
                    time.sleep(2)

                print(
                    f"File {filename} processed successfully. Total rows added: {len(batch_data)}")

                # Archive file after successful processing
                archive_file(filepath)

            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process auction CSV files')
    parser.add_argument(
        '--date', help='Override date in YYYY-MM-DD format')

    args = parser.parse_args()

    # Parse date if provided
    date_override = None
    if args.date:
        try:
            date_override = datetime.strptime(
                args.date, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M')
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")
            exit(1)

    # Process all files in results directory
    process_all_results(date_override=date_override)

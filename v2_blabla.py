import json
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread

def get_dns_records_from_cloudflare():
    vars_file_path = '/home/sashaa/python/vars.json'

    with open(vars_file_path) as config_file:
        config = json.load(config_file)
    CLOUDFLARE_TOKEN = config['CLOUDFLARE_TOKEN']
    ZONE_ID = config['ZONE_ID']

    headers = {
        'Authorization': f'Bearer {CLOUDFLARE_TOKEN}',
        'Content-Type': 'application/json'
    }

    response = requests.get(f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records', headers=headers)

    return response.json()['result']

def write_records_to_sheet(dns_records):
    vars_file_path = '/home/sashaa/python/vars.json'

    with open(vars_file_path) as config_file:
        config = json.load(config_file)
    google_keyfile = config['google_keyfile']
    sheet_name = config['sheet_name']

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(google_keyfile, scope)
    gc = gspread.authorize(credentials)

    spreadsheet = gc.open(sheet_name)

    domain = dns_records[0]['name']

    try:
        worksheet = spreadsheet.worksheet(domain)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=domain, rows="100", cols="5")

    worksheet.clear()

    for record in dns_records:
        row = [record['name'], record['type'], record['content'], record['ttl'], record.get('comment', '')]
        worksheet.append_row(row)

def main():
    dns_records = get_dns_records_from_cloudflare()
    write_records_to_sheet(dns_records)

if __name__ == "__main__":
    main()

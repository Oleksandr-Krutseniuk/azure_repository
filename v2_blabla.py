import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_dns_records_from_cloudflare(zone_id, api_token):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()['result']

def write_records_to_sheet(records, domain, spreadsheet):
    # Если лист с именем домена уже существует, то выберем его, иначе создадим новый
    try:
        worksheet = spreadsheet.worksheet(domain)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=domain, rows="100", cols="20")
        
    # Предполагается, что все записи имеют одинаковые поля, поэтому мы используем поля первой записи в качестве заголовков
    headers = list(records[0].keys())
    worksheet.append_row(headers)
    for record in records:
        row = [record[header] for header in headers]
        worksheet.append_row(row)

def main():
    api_token = "your_cloudflare_api_token"
    google_keyfile = "your_service_account_key.json"

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(google_keyfile, scope)
    gc = gspread.authorize(credentials)
    
    spreadsheet = gc.open("DNS Records")
    domains = ["example1.com", "example2.com"]

    for domain in domains:
        zone_id = ...  # Здесь нужно получить ID зоны для домена
        dns_records = get_dns_records_from_cloudflare(zone_id, api_token)
        write_records_to_sheet(dns_records, domain, spreadsheet)

if __name__ == "__main__":
    main()

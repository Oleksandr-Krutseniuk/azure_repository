import json
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread


# файл зі змінними
vars_file_path = '/home/sashaa/python/vars.json'

# відкрити файл зі змінними та вивантажити JSON-вміст
with open(vars_file_path) as config_file:
  config = json.load(config_file)
# запис змінних через доступ до значень JSON-ключів 
CLOUDFLARE_TOKEN = config['CLOUDFLARE_TOKEN']
ZONE_ID = config['ZONE_ID']
google_keyfile = config['google_keyfile']
sheet_name = config['sheet_name']


# хедери для запиту до АРІ
headers = {
    'Authorization': f'Bearer {CLOUDFLARE_TOKEN}',
    'Content-Type': 'application/json'
}

# запит до АРІ типу "дай записи ДНС-зони"
response = requests.get(f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records', headers=headers)

# вивантаження відповіді в JSON.для екстракції ДНС-записів весь output не потрібен - тільки тей, 
# що дає частина словника "result". для наглядності-приклад відповіді АРІ - 
# https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-list-dns-records
data = response.json()['result']

# Аутентификация и инициализация клиента gspread
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(google_keyfile, scope)
gc = gspread.authorize(credentials)

# Откройте лист и очистите его
worksheet = gc.open(sheet_name).sheet1
worksheet.clear()

# Запись данных DNS в лист
for record in data:
    row = [record['name'], record['type'], record['content'], record['ttl'], record.get('comment', '')]
    worksheet.append_row(row)

 # row = [record['name'], record['type'], record['content'], record['ttl'], record.get('comment', '')]
import json
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread


# variables upload
vars_file_path = '/home/sashaa/python/vars.json'

with open(vars_file_path) as config_file:
  config = json.load(config_file)
  #print(config)
 #print(config_)



# Используйте значения переменных из файла config.json
CLOUDFLARE_TOKEN = config['CLOUDFLARE_TOKEN']
ZONE_ID = config['ZONE_ID']
google_keyfile = config['google_keyfile']
sheet_name = config['sheet_name']

# Получить DNS-записи из Cloudflare
headers = {
    'Authorization': f'Bearer {CLOUDFLARE_TOKEN}',
    'Content-Type': 'application/json'
}

response = requests.get(f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records', headers=headers)

# Извлечь данные из ответа
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
    row = [record['name'], record['type'], record['content'], record['ttl']]
    worksheet.append_row(row)

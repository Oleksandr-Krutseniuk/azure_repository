import sys # повинен бути імпортований щоб зупинити скрипт при обробці перевірки наявності модулів
modules = [
    "json",
    "requests",
    "oauth2client",
    "gspread"
]

for module_name in modules:
  try:
    __import__(module_name)
# тут "try" імпортує модуль якщо він встановлений. однак "__import__" не дозволяє  використовувати 
# модуль по імені в коді (наприклад, так: config = json.load(config_file)).тому після перевірки наявності всіх
# модулів вони імпортуються окремо через команду "import"   
  except ImportError:
    print(f"Module \'{module_name}\' isn\'t installed though could be intalled with:\n\
sudo pip install {module_name}")
    sys.exit()

##
import json # handles json-files.
import requests # allows for the cloudflare dns-records request
from oauth2client.service_account import ServiceAccountCredentials # needed to extract credentials from within ->
# -> json-service account key
import gspread # needed for google sheets API interaction

# this function extracts dns-records from a particular zone
def get_dns_records_from_cloudflare(): 
    vars_file_path = '/home/sashaa/python/vars.json'# file where vars are stored

    with open(vars_file_path) as config_file:  # retrieve variables from external file.
      config = json.load(config_file)
    CLOUDFLARE_TOKEN = config['CLOUDFLARE_TOKEN']
    ZONE_ID = config['ZONE_ID']

    headers = {
        'Authorization': f'Bearer {CLOUDFLARE_TOKEN}',
        'Content-Type': 'application/json'
    }
# request for a DNS-records
    response = requests.get(f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records', headers=headers)

    return response.json()['result'] # 'result' is a subkey taken from 'response' var where DNS-records are located

def write_records_to_sheet(dns_records):
    vars_file_path = '/home/sashaa/python/vars.json' # file where vars are stored

    with open(vars_file_path) as config_file: # retrieve variables from external file
        config = json.load(config_file)
    google_keyfile = config['google_keyfile'] # extract path to the service account key
    sheet_name = config['sheet_name'] 

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(google_keyfile, scope)
    gc = gspread.authorize(credentials)

    try: # перевірка існування таблиці
      spreadsheet = gc.open(sheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
      print(f'Table "{sheet_name}" doesn\'t exist or access for service account hasn\'t been granted by spreadsheet owner!')
      sys.exit()

     
    domain = dns_records[0]['zone_name'] # змінна для присвоєння назви листку в таблиці
    try: # <-перевірка існування листа таблиці
        worksheet = spreadsheet.worksheet(domain)
    except gspread.WorksheetNotFound:# <-якщо лист не існує - створюю,а цифри в параметрах є розміром полей таблиці
        worksheet = spreadsheet.add_worksheet(title=domain, rows="100", cols="5")

    worksheet.clear() # очистка листа таблиці перед записом даних. функція "get_dns_records_from_cloudflare"
    # отримує живі дані від Cloudflare API - тому контент листа видаляється та заповнюється 
    # актуальними записами

# вивід з ДНС-записами складається з списку, а кожен елемент списку-це словник.тому кожний елемент списку буде давати 
# значення ключів ['name'], ['type'],['content'],['ttl'] і 'comment' та поміщати його в змінну,яка буде дописана в таблицю
    for record in dns_records:
        row = [record['name'], record['type'], record['content'], record['ttl'], record.get('comment', '')]
        worksheet.append_row(row)

def main():
    dns_records = get_dns_records_from_cloudflare()

# that's a debug part.it allows for dns.records.json contents research
#    with open('dns_records.json', 'w') as file:
#        json.dump(dns_records, file, indent=4)

    write_records_to_sheet(dns_records)

if __name__ == "__main__":
    main()
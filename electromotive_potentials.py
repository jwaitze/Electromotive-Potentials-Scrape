# Electromotive Potentials Scrape

filename_prefix = 'electromotive_potentials'

import sys, requests, openpyxl
from bs4 import BeautifulSoup

def download_raw_electromotive_potentials_data():
    result = []
    url = 'https://en.wikipedia.org/wiki/Standard_electrode_potential_(data_page)'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    trs = soup.find_all('table')[0].find_all('tr')
    for tr in trs:
        result.append([td.text for td in tr.find_all('td')])
    return result

def download_electromotive_potentials():
    raw_electromotive_potentials, electromotive_potentials = download_raw_electromotive_potentials_data(), []
    raw_electromotive_potentials = [a[:4] for a in raw_electromotive_potentials if len(a) >= 3]
    for row in raw_electromotive_potentials:
        electromotive_potentials.append([])
        row.pop(1)
        for entry in row:
            if entry[1:].replace('.', '').isdigit():
                electromotive_potentials[-1].append(float(entry.replace('−', '-')))
            elif type(entry) is str:
                electromotive_potentials[-1].append(entry.replace('\u200a', ''))
    #[print(row) for row in electromotive_potentials]
    return [['oxidant', 'reductant', 'potential']] + electromotive_potentials

def write_excel_file(filename, data):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = filename_prefix
    for row in data:
        ws.append(row)
    wb.save(filename)

def excel_workbook_to_list(filepath):
    retval = []
    wb = openpyxl.load_workbook(filepath)
    ws = wb.worksheets[0]
    for row in ws.iter_rows():
        retval.append([cell.value for cell in row])
    return retval

def get_json_from_excel_workbook(filepath):
    excel_data = excel_workbook_to_list(filepath)
    keys, j = excel_data[0], []
    for row in range(1, len(excel_data)):
        j.append({})
        for k in range(len(keys)):
            if excel_data[row][k] == None:
                excel_data[row][k] = 'n/a'
            j[-1].update( { keys[k] : excel_data[row][k] } )
    return j

def write_json_list_to_file(filepath, j):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        for row in j:
            outfile.write(str(row) + '\n')

def write_series_to_json_file(excel_filepath, json_filepath):
    j = get_json_from_excel_workbook(excel_filepath)
    write_json_list_to_file(json_filepath, j)

if __name__ == '__main__':
    electromotive_potentials = download_electromotive_potentials()
    write_excel_file(filename_prefix + '.xlsx', electromotive_potentials)
    write_series_to_json_file(filename_prefix + '.xlsx', filename_prefix + '.json')

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from time import sleep


def get_table(round, url=url):
    round_url = f'{url}/{round}'
    page = requests.get(round_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    rows = []
    for child in soup.find_all('table')[4].children:
        row = []
        for td in child:
            try:
                row.append(td.text.replace('\n', ''))
            except:
                continue
        if len(row) > 0:
            rows.append(row)

    df = pd.DataFrame(rows[1:], columns=rows[0])
    return df


for round in range(1, 39):
    table = get_table(round)
    table.to_csv(f'PL_table_matchweek_{round}.csv', index=False)
    sleep(np.random.randint(1, 10))

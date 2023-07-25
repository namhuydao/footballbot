import httpx
from selectolax.parser import HTMLParser
from datetime import datetime
import pandas as pd


def parse_html(html: str) -> list:
    html = HTMLParser(html)
    transfer_infos = html.css('tr.line')
    results = []
    for transfer_info in transfer_infos:
        if transfer_info.css_first('td.firstteam a') is not None:
            start = transfer_info.css_first('td.firstteam a').text(strip=True)
        elif transfer_info.css_first('td.firstteam') is not None:
            start = transfer_info.css_first('td.firstteam').text(strip=True)
        else:
            start = None

        if transfer_info.css_first('td.secondteam a') is not None:
            destination = transfer_info.css_first(
                'td.secondteam a').text(strip=True)
        else:
            destination = transfer_info.css_first(
                'td.secondteam').text(strip=True)
        transfer = {
            'player_name': transfer_info.css_first(
                'td.name a').text(strip=True),
            'start': start,
            'destination': destination,
            'amount': transfer_info.css_first(
                'td.transferamount').text(strip=True)}

        results.append(transfer)
    return results


def get_all_transfers(number_day_from_now: int, type: str) -> str:
    results = []

    if type == 'All':
        type = 'full'
    elif type == 'Major league':
        type = 'majorc'
    elif type == 'Top transfer':
        type = 'toptrans'

    i = 0
    while True:
        i = i + 1
        data = {
            'date': datetime.now(),
            'pid': number_day_from_now + 1,
            'page': i,
            'filter': type
        }

        with httpx.Client() as client:
            try:
                resp = client.post(
                    'https://www.footballdatabase.eu/ajax_transfers_show.php',
                    data=data)
            except httpx.TimeoutException as e:
                print('gottem' + e)
        if resp.status_code != 200:
            break
        if not resp.text.__contains__("<tr class='line"):
            break
        results.extend(parse_html(resp.text))
    results = transform_results(results)
    return results


def transform_results(results: list) -> pd.DataFrame:
    df = pd.DataFrame(results)
    if len(results) == 0:
        return df

    df['amount'] = df['amount'].apply(lambda x: x.replace('xa0', ''))
    df['amount'] = df['amount'].apply(
        lambda x: x.replace('Retour de prêt', 'Return from loan').replace(
            'Gratuit', 'Free').replace('Prêt', 'Loan'))
    df['start'] = df['start'].apply(lambda x: 'Free' if x == 'libre' else x)
    df['destination'] = df['destination'].apply(
        lambda x: 'Free' if x == 'libre' else x)
    df['destination'] = df['destination'].apply(
        lambda x: x.replace('xa0', ' '))

    return df


def main():
    # url = 'https://www.footballdatabase.eu/en/transfers'
    print(get_all_transfers(0, 'All'))


if __name__ == "__main__":
    main()

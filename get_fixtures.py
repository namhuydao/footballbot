import httpx
import pandas as pd


def get_all_fixtures(date_string: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    url = f'https://prod-public-api.livescore.com/v1/api/app/date/soccer/{date_string}/7?MD=1&countryCode=VN'
    results = []
    with httpx.Client() as client:
        try:
            resp = client.get(url, headers=headers)
        except httpx.TimeoutException as e:
            print(e)
    if resp.status_code == 200:
        results = resp.json()
        results = transform_result(results['Stages'])
    else:
        return 'Error trying to fetch api'
    return results


def transform_result(results: list) -> pd.DataFrame:
    datas = []
    for result in results:
        events = result['Events']

        for event in events:
            if 'Tr1OR' not in event.keys():
                home_score_all = None
            else:
                home_score_all = event['Tr1OR']

            if 'Tr2OR' not in event.keys():
                away_score_all = None
            else:
                away_score_all = event['Tr2OR']

            data = {
                'type': result['Snm'],
                'league': result['Cnm'],
                'home_team': event['T1'][0]['Nm'],
                'away_team': event['T2'][0]['Nm'],
                'status': event['Eps'],
                'start_time': event['Esd'],
                'home_score_all': home_score_all,
                'away_score_all': away_score_all,
            }
            datas.append(data)
    df = pd.DataFrame(datas)
    return df


def main():
    get_all_fixtures('20230725')


if __name__ == "__main__":
    main()

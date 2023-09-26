import httpx
import pandas as pd
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

competitions: dict = {
    'VIETNAM': 'aho73e5udydy96iun3tkzdzsi',
    'ENGLAND': '2kwbbcootiqqgmrzs6o5inle5',
    'FRANCE': 'dm5ka0os1e3dxcp3vh05kmp33',
    'NETHERLANDS': 'akmkihra9ruad09ljapsm84b3',
    'BELGIUM': '4zwgbb66rif2spcoeeol2motx',
    'GERMANY': '6by3h89i2eykc341oz7lv1ddd',
    'SPAIN': '34pl8szyvrbwcmfkuocjm3r6t',
    'ITALY': '1r097lpxe0xn03ihb7wi98kao',
    'CHAMPIONLEAGUE': '4oogyu6o156iphvdvphwpck10',
    'EUROPALEAGUE': '4c1nfi2j1m731hcay25fcgndq',
}


def get_standings(competition: str) -> tuple:
    useragent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)" \
                     " AppleWebKit/537.36 (KHTML, like Gecko)" \
                     " Chrome/39.0.2171.95 Safari/537.36"

    headers: dict = {
        "User-Agent": useragent
    }

    with httpx.Client() as client:
        try:
            resp_home = client.get(
                f'https://www.goal.com/api/competition/standings?edition=en-us&id={competitions.get(competition)}&type=HOME',
                headers=headers)
            resp_away = client.get(
                f'https://www.goal.com/api/competition/standings?edition=en-us&id={competitions.get(competition)}&type=AWAY',
                headers=headers)
        except httpx.TimeoutException as e:
            logger.error(f"Timeout Exception: {e}")

    if resp_home.status_code != 200:
        logger.error(
            f"No response received, status code: {resp_home.status_code}")
        return ()

    if resp_away.status_code != 200:
        logger.error(
            f"No response received, status code: {resp_away.status_code}")
        return ()

    home_results = resp_home.json()['tables'][0]['rankings']
    away_results = resp_away.json()['tables'][0]['rankings']

    (results, home, away) = transform_results(home_results, away_results)

    logger.info("Data crawled from goal.com successful!")

    return results, home, away


def transform_results(home_results: json, away_results: json) -> tuple:
    home = []
    away = []
    for result in home_results:
        team_name = result["team"]["long"]
        data = {
            "Team": team_name,
            "P": result["played"],
            "W": result["win"],
            "L": result["lose"],
            "D": result["draw"],
            "F": result["goalsFor"],
            "A": result["goalsAgainst"],
            "+/-": result["goalsDifference"],
            "PTS": result["points"],
        }
        home.append(data)

    for result in away_results:
        team_name = result["team"]['long']
        data = {
            "Team": team_name,
            "P": result["played"],
            "W": result["win"],
            "L": result["lose"],
            "D": result["draw"],
            "F": result["goalsFor"],
            "A": result["goalsAgainst"],
            "+/-": result["goalsDifference"],
            "PTS": result["points"],
        }
        away.append(data)

    home_df: pd.DataFrame = pd.DataFrame(home)
    home_df.index = home_df.index + 1
    away_df: pd.DataFrame = pd.DataFrame(away)
    away_df.index = away_df.index + 1

    df = pd.concat([home_df, away_df])
    df = df.groupby(by='Team').sum()
    df = df.sort_values(by=['PTS', '+/-'], ascending=False)
    df.reset_index(inplace=True)
    df.index = df.index + 1
    logger.info("Transforming results successful!")

    return df, home_df, away_df


def main():
    print(get_standings('ENGLAND'))


if __name__ == "__main__":
    main()

import httpx
import pandas as pd
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

competitions: dict = {
    'VIETNAM': '976bcjxmlyn7afvrrnk6qg9hw',
    'ENGLAND': 'c6fq6f5jb8xniw2tmam5pxo9g',
    'FRANCE': 'f1mc9cijvfv3ageg1ykljyl1w',
    'NETHERLANDS': '3yyw70zr66ia7huendgax0idw',
    'BELGIUM': '3niff29a2qgmtfvf477muzztg',
    'GERMANY': '',
    'SPAIN': '',
    'ITALY': '',
    'CHAMPIONLEAGUE': '',
    'EUROPALEAGUE': '',
}


def get_standings(competition: str) -> pd.DataFrame:
    useragent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)" \
                     " AppleWebKit/537.36 (KHTML, like Gecko)" \
                     " Chrome/39.0.2171.95 Safari/537.36"

    headers: dict = {
        "User-Agent": useragent
    }

    with httpx.Client() as client:
        try:
            resp = client.get(
                f'https://www.goal.com/en-us/ajax/match/standings?matchId={competitions.get(competition)}',
                headers=headers)
        except httpx.TimeoutException as e:
            logger.error(f"Timeout Exception: {e}")

    if resp.status_code != 200:
        logger.error(
            f"No response received, status code: {resp.status_code}")
        return pd.DataFrame()

    results = transform_results(resp.json()['standings'])
    logger.info("Data crawled from goal.com successful!")

    return results


def transform_results(results: json) -> pd.DataFrame:
    pd.set_option('display.max_columns', None)
    df: pd.DataFrame = pd.DataFrame(results)
    if len(results) == 0:
        return df

    df.drop(
        columns=['teamId', 'teamCode', 'teamCrest', 'rankStatus', 'rankChange', 'teamUrl', 'lastForm', 'isHighlighted',
                 'liveDetails'], inplace=True)

    df.rename(
        columns={'teamName': 'Team', 'rank': 'Pos', 'matchesPlayed': 'P', 'matchesWon': 'W', 'matchesLost': 'L',
                 'matchesDrawn': 'D', 'goalsFor': 'F', 'goalsAgainst': 'A', 'goalDifference': '+/-',
                 'points': 'PTS', }, inplace=True)

    logger.info("Transforming results successful!")
    return df.set_index('Pos')


def main():
    print(get_standings('ITALY'))


if __name__ == "__main__":
    main()

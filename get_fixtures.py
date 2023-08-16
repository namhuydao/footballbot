import httpx
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_fixtures(date_string: str) -> pd.DataFrame:
    useragent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)" \
        " AppleWebKit/537.36 (KHTML, like Gecko)" \
        " Chrome/39.0.2171.95 Safari/537.36"

    headers: dict = {
        "User-Agent": useragent
    }
    url: str = f"https://prod-public-api.livescore.com/v1/api" \
        f"/app/date/soccer/{date_string}/7?MD=1&countryCode=VN"

    with httpx.Client() as client:
        try:
            resp = client.get(url, headers=headers)
        except httpx.TimeoutException as e:
            logger.error(f"Timeout Exception: {e}")
    if resp.status_code == 200:
        results = resp.json()
        results = transform_results(results["Stages"])
        return results
    else:
        logger.error("Error trying to fetch api")
        return pd.DataFrame()


def transform_results(results: list) -> pd.DataFrame:
    datas: list = []
    if len(results) == 0:
        return pd.DataFrame(datas)

    for result in results:
        events = result["Events"]
        for event in events:
            home_score_all = event['Tr1'] if 'Tr1' in event.keys() else None
            away_score_all = event['Tr2'] if 'Tr2' in event.keys() else None
            home_score_pen = event['Trp1'] if 'Trp1' in event.keys() else None
            away_score_pen = event['Trp2'] if 'Trp2' in event.keys() else None

            data = {
                "type": result["Snm"],
                "league": result["Cnm"],
                "home_team": event["T1"][0]["Nm"],
                "away_team": event["T2"][0]["Nm"],
                "status": event["Eps"],
                "start_time": event["Esd"],
                "home_score_all": home_score_all,
                "away_score_all": away_score_all,
                "home_score_pen": home_score_pen,
                "away_score_pen": away_score_pen,
            }
            datas.append(data)
    df: pd.DataFrame = pd.DataFrame(datas)
    df["start_time"] = (
        df["start_time"].astype(str).str[-6:-4]
        + ":"
        + df["start_time"].astype(str).str[-4:-2]
    )

    logger.info("Transforming results successful!")

    return df


def main():
    get_all_fixtures("20230725")


if __name__ == "__main__":
    main()

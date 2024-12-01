import json
from datetime import datetime, timedelta
from pathlib import Path

import requests


def fetch_afisha(save_dir: Path):
    start = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    end = (datetime.now() + timedelta(weeks=2)).strftime("%Y-%m-%dT%H:%M:%S")

    request_url = "https://hack-it.yazzh.ru/afisha/all"

    page = 1

    while True:
        response = requests.get(request_url, params={"start_date": start, "end_date": end, "page": page}).json()
        if not response["data"]:
            return
        with open(save_dir / f"{page}.json", "w", encoding="utf-8") as f:
            json.dump(response["data"], f, ensure_ascii=False)

        page += 1


if __name__ == "__main__":
    fetch_afisha(Path("./yazzh/afisha"))

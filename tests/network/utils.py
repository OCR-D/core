from requests import get


def is_url_responsive(url: str, retries: int = 0) -> bool:
    while True:
        try:
            response = get(url)
            if response.status_code == 200:
                return True
        except Exception:
            if retries <= 0:
                return False
            retries -= 1

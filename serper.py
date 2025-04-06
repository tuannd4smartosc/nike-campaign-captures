import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def search_web(query: str, region: str):
    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": query,
        "gl": region,
        "tbs": "qdr:w"
    })
    headers = {
        'X-API-KEY':  os.environ['SERPER_API_KEY'],
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    results = data['organic']
    return results


def scrape_web_page(link: str):
    try:
        url = "https://scrape.serper.dev/"
        payload = json.dumps({"url": link, "includeMarkdown": True})
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()
    except Exception:
        return {
            "markdown": "*Not found*"
        }

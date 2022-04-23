import requests
import json

def route_to_clip(text, max_img_cnt, url):
    print(url)
    payload = json.dumps({
    "text": text,
    "max_img_cnt": max_img_cnt
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    return response.text


def get_unsplash_redirect(url):
    r = requests.get(url)
    return r.url
import json

import requests

urls = ["https://open.feishu.cn/open-apis/bot/v2/hook/b6872ac5-b285-4bee-a1e2-98bb3004b735"]


def send_msg(msg):
    if not msg:
        msg = "I'm IAOS."
    headers = {
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "msg_type": "text",
        "content": {
            "text": msg
        }
    })
    for url in urls:
        response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)

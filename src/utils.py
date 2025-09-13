import random
import time
import json
import requests

#Simulates typing by calling function while passing text given
def simTyping(element, text):
    for char in text:
        time.sleep(random.uniform(0.1, 0.3))
        element.send_keys(char)
        if random.random() < 0.1: # more randomness
            time.sleep(random.uniform(0.3, 0.7))

def sleepRand(min=0.1, max=0.3):
    time.sleep(random.uniform(min, max))

def dumpJsonToWebhook(channel, filedir):
    with open(filedir, "r", encoding="utf-8") as f:
        messages = json.load(f)  # list of message dicts

    url = "https://discord.com/api/webhooks/1416276378139230268/rdiZL2h4NEEFby622sHj2lQGv5PHDmnH3pj2zE-dmmoxh9dynN58AeMsY0t95nJjvECW"

    for v in messages:
        print(v)
        timedata = v["timedata"]
        description = "\n".join(v["message"]) if isinstance(v["message"], list) else v["message"]

        payload = {
            "username": "Messenger Scraper test",
            "avatar_url": "https://i.imgur.com/4M34hi2.png",
            #"content": "Showing scraped messages:",
            "embeds": [
                {
                    "author": {
                        "name": v["displayname"],
                        "icon_url": v["profilesrc"],
                    },
                    "title": f"{timedata['day']} at {timedata['time']} {timedata['hrform']}" if timedata["month"] == timedata["day"] else f"{timedata['month']} {timedata['day']} at {timedata['time']} {timedata['hrform']}",
                    "description": description,
                    "color": 28049,
                    "footer": {
                        "text": f"ThreadID: {channel}",
                    },
                }
            ],
        }

        time.sleep(1)
        response = requests.post(url, json=payload)

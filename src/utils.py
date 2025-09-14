import os

#Simulates typing by calling function while passing text given
def simTyping(element, text):
    import random, time
    for char in text:
        time.sleep(random.uniform(0.1, 0.3))
        element.send_keys(char)
        if random.random() < 0.1: # more randomness
            time.sleep(random.uniform(0.3, 0.7))

#Sleeps for a random time
def sleepRand(min=0.1, max=0.3):
    import random, time
    time.sleep(random.uniform(min, max))

#Target element using XPATH, returning False if not found.
def targetByXPATH(elem, xPath, timeout=0):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    time = WebDriverWait(elem, timeout)
    findElem = None

    try:
        findElem = time.until(EC.element_to_be_clickable((
            By.XPATH, xPath
        )))
    except:
        findElem = False

    return findElem

#Returns true if all passed args is false
def checkIfAllFalse(*args):
    for value in args:
        if value:
            return False
    return True

#Executes function if condition is True
def executeOnTrue(condition, func, *args, **kargs):
    if condition:
        func(*args, **kargs)

def hasClass(elem, className):
    try:
        return className in elem.get_attribute("class").split()
    except:
        return False

#Helper class for creating discord embeds
class DiscordEmbed:
    def __init__(self, username="neon-cat", avatar_url="https://i.imgur.com/v9BsQmo.png", content=None):
        self.embed = {
            "username": username,
            "avatar_url": avatar_url,
            "content": content,
            "embeds": []
        }
        self.embedauthor = None
        self.footer = None
        self.fields = []

    def setEmbedAuthor(self, name="author", url=None, icon_url=None):
        self.embedauthor = {
            "name": name,
            "url": url,
            "icon_url": icon_url
        }

    def clearFields(self):
        self.fields = []

    def pushField(self, name="Field", value="field_value", inline=False):
        self.fields.append({
            "name": name,
            "value": value,
            "inline": inline
        })

    def setFooter(self, text="bot", icon_url=None):
        self.footer = {
            "text": text,
            "icon_url": icon_url
        }

    def addEmbed(self, color=28049, title=None, url=None, description=None, thumbnail_url=None, image_url=None):
        
        if not thumbnail_url is None:
            thumbnail_url = {
                "url": thumbnail_url
            }
        if not image_url is None:
            image_url = {
                "url": image_url
            }
        
        self.embed['embeds'].append({
            "title": title,
            "url": url,
            "description": description,
            "thumbnail_url": thumbnail_url,
            "image_url": image_url,
            "author": self.embedauthor,
            "footer": self.footer,
            "color": color
        })

    def build(self, printBuild=False) -> dict:
        
        def clean_none(d):
            if isinstance(d, dict):
            # Make a copy of keys to avoid modifying while iterating
                keys_to_remove = []
                for k, v in d.items():
                    if v is None:
                        keys_to_remove.append(k)
                    else:
                        clean_none(v)
                for k in keys_to_remove:
                    del d[k]
            elif isinstance(d, list):
                for item in d:
                    clean_none(item)
            return d
        
        clean_none(self.embed)
        if printBuild:
            print(self.embed)
        return self.embed

#Sends a webhook to discord with passed embed data
def sendDiscordWebhook(embed, url=str(os.environ.get("WEBHOOKENDPOINT"))):
    import requests
    if url is None:
        print("Util Error: No WEBHOOKENDPOINT var given.")
        return 400

    response = requests.post(url, json=embed)
    return response.status_code

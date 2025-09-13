
#from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import utils
import json
import time
import re

import undetected_chromedriver as uc

class MessengerCrawler():
    def __init__(self, cookies, theme):
        self.cookies = cookies
        self.browserTheme = theme
        self.driver = None
        

    def inititalizeDrivers(self, flags=None):
        print("Setting up...")
        options = uc.ChromeOptions()
        if not flags is None:
            options.add_argument(flags)

        self.driver = uc.Chrome(options=options, use_subprocess=True)

    def loginMessenger(self):
        self.driver.get("https://www.messenger.com")
        wait = WebDriverWait(self.driver, 10)
        shortWait = WebDriverWait(self.driver, 3)

        wait.until(EC.element_to_be_clickable((
            By.XPATH, "//input[@name='email' and @id='email']"
        )))
        wait.until(EC.element_to_be_clickable((
            By.XPATH, "//input[@name='pass' and @id='pass']"
        )))
        wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@name='login' and @id='loginbutton']"
        )))
        # Login page mustve loaded already
        print("Logging cookies...")
        for cookie in self.cookies:
            # Check for sameSite dict
            if "sameSite" in cookie:
                cookie["sameSite"] = "None"
            print(cookie)
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        print("Waiting...")
        try:
            shortWait.until(EC.element_to_be_clickable((
                By.XPATH, "//input[@name='email' and @id='email']"
            )))
            shortWait.until(EC.element_to_be_clickable((
                By.XPATH, "//input[@name='pass' and @id='pass']"
            )))
            shortWait.until(EC.element_to_be_clickable((
                By.XPATH, "//button[@name='login' and @id='loginbutton']"
            )))
            print("Login page is still present. Cookies are invalid.")
            return False
        except:
            print("Passed login page.")


        chatPinElem = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[@aria-label='Close' and @role='button']"
        )))
        utils.sleepRand()
        chatPinElem.click()
        dontRestoreElem = wait.until(EC.element_to_be_clickable((
            By.XPATH, '''//div[@aria-label="Don't restore messages" and @role='button']'''
        )))
        utils.sleepRand()
        dontRestoreElem.click()
        utils.sleepRand(1, 1.5)
        return True

    def navigateToChannel(self, id):
        self.driver.get(f"https://www.messenger.com/t/{id}")

    def interfaceWithCurrentChannel(self):
        wait = WebDriverWait(self.driver, 30)
        self.main = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[@role='main']//div[@role='grid']/div/div[@role='none']"
        )))
        self.messages = self.main.find_element(By.XPATH, "./div")
    
    def listen(self):
        wait = WebDriverWait(self.driver, 9999999)

    def scrapeMessages(self, limit=10):
        def hasClass(elem, className):
            try:
                return className in elem.get_attribute('class').split()
            except:
                return False
            

        def findMessagesOnFrame():
            print("Waiting for page load....")
            time.sleep(10)
            print("Starting to scrape messages....")

            msgs = self.messages.find_elements(
                By.XPATH, ".//div[@role='row']"
            )
            # Drop first elem
            msgs.pop(0)

            currentDt = dict(
                month = 'NONE',
                day = 'NONE',
                time = 'NONE',
                hrform = 'NONE'
            )

            rawmsg = []
            chainedmsg = []

            print(f"Found ${str(len(msgs))} row elements to scrape.")

            for i, elem in enumerate(msgs):
                print(f"Processing element ${i} out of ${len(msgs)}")
                elemWait = WebDriverWait(elem, 10)
                if not hasClass(elem, self.browserTheme):
                    # Finding text data
                    try:
                        dateElem = elemWait.until(EC.presence_of_element_located((
                            By.XPATH, "./div/div/div/div/h4/div[not(@aria-hidden='true')]/span"
                        )))
                    except:
                        print("No date found.")
                        continue
                    elemText = self.driver.execute_script("return arguments[0].innerText || window.getComputedStyle(arguments[0], '::before').getPropertyValue('content') || window.getComputedStyle(arguments[0], '::after').getPropertyValue('content');",
                        dateElem).strip('"')
                    print("Raw text: ", elemText)
                    date = re.sub(r'\s+', '_', elemText).split('_')
                    print(f"Processing data: ${elemText} as ${date}")
                    if len(date) == 5:
                        currentDt['month'] = date[0]
                        currentDt['day'] = date[1]
                        currentDt['time'] = date[3]
                        currentDt['hrform'] = date[4]
                    elif len(date) == 4:
                        currentDt['month'] = date[0]
                        currentDt['day'] = date[0]
                        currentDt['time'] = date[2]
                        currentDt['hrform'] = date[3]
                    else:
                        print("invalid date format.")
                   
                    
                else:
                    # assume currentDT already exists
                    try:
                        msgElem = elemWait.until(EC.visibility_of_element_located((
                            By.XPATH, ".//div[@dir='auto']"
                        )))
                    except:
                        print("Invalid message type")
                        continue

                    try:
                        profileElem = elem.find_element(
                            By.XPATH, ".//div[@role='button']/img"
                        )
                        chainedmsg.append(msgElem.text)
                        print(f"Found text {msgElem.text}")
                        rawmsg.append({
                            'timedata': currentDt,
                            'message': chainedmsg,
                            'displayname': profileElem.get_attribute('alt'),
                            'profilesrc': profileElem.get_attribute('src')
                        })
                        chainedmsg = [] #Lose reference
                    except:
                        chainedmsg.append(msgElem.text)
                    
            return rawmsg

        return findMessagesOnFrame()

 

if __name__ == "__main__":
    CHANNEL = 1452226939361503

    crawler = MessengerCrawler(json.load(open("cookie.js", "r")), '__fb-light-mode') # Burner account
    crawler.inititalizeDrivers()
    crawler.loginMessenger()
    crawler.navigateToChannel(CHANNEL)
    crawler.interfaceWithCurrentChannel()

    with open(f"./results/{CHANNEL}{time.strftime("%Y-%m-%d@%H-%M-%S",time.localtime())}", "w", encoding="utf-8") as f:
        json.dump(crawler.scrapeMessages(), f, ensure_ascii=False, indent=2)

    input("Press Enter to end")
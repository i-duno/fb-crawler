from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

import pyperclip

import utils

import json, time, hashlib
import logging, sys, os
import threading

from typing import cast

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s %(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("Crawlerv1.0")


class MessengerCrawler:
    def __init__(self, flags=[]):
        cookie_env = os.environ.get("MESSENGERCOOKIE")
        cookiePath = os.path.join(os.path.dirname(__file__), cookie_env)  # type: ignore
        logger.info(f"Loading cookie at path {cookiePath}...")
        self.cookies = json.load(open(cookiePath))

        self.browserTheme = None
        self.main = None
        self.messages = None
        self.interfacedWithUrl = ""

        self.seenMessages = []

        logger.info("Starting up crawler...")
        options = webdriver.ChromeOptions()

        for flag in flags:
            logger.info(f"Adding argument {flag}")
            options.add_argument(flag)

        self.driver = webdriver.Chrome(options=options)
        self.loginsuccess = False

    def initializeDistinctors(self, theme):
        self.browserTheme = theme
        logger.info("Messenger distinctors recieved")

    def loginMessenger(self):
        logger.info("Entry on website")
        self.driver.get("https://www.messenger.com")

        # Wait for login page to load
        utils.targetByXPATH(self.driver, "//input[@name='email' and @id='email']", 10)
        utils.targetByXPATH(self.driver, "//input[@name='pass' and @id='pass']", 10)
        utils.targetByXPATH(
            self.driver, "//button[@name='login' and @id='loginbutton']", 10
        )
        logger.info("Login finished loading")

        logger.info(f"Adding {len(self.cookies)} to browser.")
        for cookie in self.cookies:
            # Check for sameSite dict
            if "sameSite" in cookie:
                cookie["sameSite"] = "None"
            self.driver.add_cookie(cookie)
            logger.info(f"Inserting cookie...\n{cookie}")
        logger.info("Waiting for browser refresh...")
        self.driver.refresh()
        utils.sleepRand()
        if not utils.checkIfAllFalse(
            utils.targetByXPATH(
                self.driver, "//input[@name='email' and @id='email']", 3
            ),
            utils.targetByXPATH(self.driver, "//input[@name='pass' and @id='pass']", 3),
        ):
            logger.critical("Login failed, stopping program.")
            sys.exit(1)
        logger.info("Finalizing login...")
        logger.info("Waiting ~5s for pin element to possibly appear.")
        self.driver.save_screenshot("entry")
        utils.sleepRand(5, 6)
        chatelem = utils.targetByXPATH(
            self.driver, "//div[@aria-label='Close' and @role='button']", 10
        )
        utils.executeOnTrue(chatelem, lambda: chatelem.click())  # type: ignore
        utils.sleepRand()
        dontrestore = utils.targetByXPATH(
            self.driver,
            """//div[@aria-label="Don't restore messages" and @role='button']""",
            10,
        )
        utils.executeOnTrue(dontrestore, lambda: dontrestore.click())  # type: ignore
        utils.sleepRand(3, 5)
        logger.info("Login successful")

        self.loginsuccess = True

        return True

    def navigateToChannel(self, id):
        logger.info(f"Redirecting to https://www.messenger.com/t/{id}")
        self.driver.get(f"https://www.messenger.com/t/{id}")

        ready_state = self.driver.execute_script("return document.readyState")
        if ready_state == "complete":
            logger.info(
                "DOM fully loaded, waiting arbitary time for react elements to load..."
            )
        utils.sleepRand(3, 5)

    def interfaceWithCurrentChannel(self):
        logger.info("Interfacing with current channel...")
        logger.info("Looking for MAIN")
        self.main = utils.targetByXPATH(
            self.driver,
            "//div[@role='main']//div[@role='grid']/div/div[@role='none']",
            15,
        )
        logger.info("Looking for MESSAGES")
        self.messages = utils.targetByXPATH(self.main, "./div", 15)
        self.interfacedWithUrl = self.driver.current_url
        logger.info("Looking for INPUT <p> element")
        self.input = utils.targetByXPATH(self.driver, "//div[@role='main']//div[@role='group']//div[@data-lexical-editor='true']/p", 15)  # type: ignore
        logger.info("Looking for INPUT (send) element")
        self.inputSend = utils.targetByXPATH(self.driver, "//div[@role='main']//div[@role='group']/span/div", 15)  # type: ignore
        logger.info("Interface done.")

    def resetSeenMessages(self):
        self.seenMessages = []

    def sendMessage(self, message: str):
        self.interfaceWithCurrentChannel()
        pyperclip.copy(message)
        self.input.click() #type: ignore
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        self.interfaceWithCurrentChannel()
        self.inputSend.click() #type: ignore
        logger.info(f"Sent message: {message}")

    def scrapeMessages(self):
        newMessages = []

        def getContent(elem):
            if utils.hasClass(elem, self.browserTheme):
                # Works when it is a regular msg element
                msgElem = utils.targetByXPATH(elem, ".//div[@dir='auto']")
                if msgElem:
                    return [msgElem.text]

                # Check if it contains photos
                try:
                    photoElems = elem.find_elements(
                        By.XPATH, ".//img[@alt='Open photo']"
                    )
                    if photoElems:
                        table = []
                        for individualPhotoElem in photoElems:
                            table.append(
                                individualPhotoElem.get_attribute("src")
                            )
                        return table
                finally:
                    pass

                # Check if it contains gif images
                gifElems = utils.targetByXPATH(
                    elem, ".//img[@alt='GIF Image']"
                )
                if gifElems:
                    return [gifElems.get_attribute("src")]

                # Check if it has a download link
                dlLink = utils.targetByXPATH(elem, ".//a[@role='link']")
                if dlLink:
                    return [dlLink.get_attribute("href")]

                return []
            else:
                return []
            
        def checkRowType(elem):
            content = getContent(elem)

            profileElem = utils.targetByXPATH(
                elem, ".//div[@role='button']/img"
            )
            profileData = {"displayName": "", "profileSrc": ""}
            if profileElem:
                profileData["displayName"] = (
                    profileElem.get_attribute("alt") or "none"
                )
                profileData["profileSrc"] = (
                    profileElem.get_attribute("src") or "none"
                )

            return (content, profileData)


        def findNewMessagesOnFrame():
            nonlocal newMessages
            if not self.messages or not self.main:
                logger.critical("Interface is empty")
                sys.exit()
            if self.driver.current_url != self.interfacedWithUrl:
                logger.critical("Interface is set to another url")
                sys.exit()
            self.messages = cast(WebElement, self.messages)
            msgs = self.messages.find_elements(By.XPATH, ".//div[@role='row']")

            # Process doms
            for elem in msgs:

                # Check first for uuid
                logger.debug("Processing new chat row...")

                try:
                    content, profileData = checkRowType(elem)
                    if content == []:
                        continue
                    # Note: content is a list and profileData is a dict
                    msg_text = "/".join(str(x) for x in content)  # type: ignore
                    msg_src = "/".join(str(val) for x, val in profileData.items())
                    msg_final = "/".join([msg_text, msg_src])
                    
                    # msg_hash = hashlib.md5(msg_final.encode()).hexdigest()
                    msg_hash_simple = hashlib.md5(msg_final.encode()).hexdigest()

                    if msg_hash_simple in self.seenMessages:
                        continue
                    else:
                        logger.info(
                            f"Found brand new data: {content} {profileData['displayName']}"
                        )
                        # self.seenMessages.append(msg_hash)
                        self.seenMessages.append(
                            msg_hash_simple
                        )  # Just store the text, since profile names may disappear
                        newMessages.append([content, profileData])

                except StaleElementReferenceException:
                    logger.debug("Holding stale reference, skipping.")
            return newMessages

        return findNewMessagesOnFrame()


utils.sendDiscordWebhook([])
if __name__ == "__main__":
    crawler = MessengerCrawler(
        [
            "--headless",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--window-size=1200,900",
            # Stealth
            "--disable-blink-features=AutomationControlled",
            "--disable-popup-blocking",
            "--disable-notifications",
            "--disable-extensions",
        ]
    )

    CHANNEL = 1871848997066510

    crawler.initializeDistinctors("__fb-light-mode")
    crawler.loginMessenger()
    crawler.navigateToChannel(CHANNEL)
    crawler.interfaceWithCurrentChannel()
    crawler.resetSeenMessages()  # remind this

    hot_keyword = "@Grok"

    LLMClient = Groq(
        api_key=os.environ.get(
            "GROKAPIKEY"
        ),  # This is the default and can be omitted
    )

    def worker():
        while True:
            logger.info("Scrapping new wave now")
            messages = crawler.scrapeMessages()

            for msg in messages:
                content: list[str] = msg[0]
                profileData = msg[1]
                displayName, profileSrc = (
                    profileData["displayName"],
                    profileData["profileSrc"],
                )

                for text in content:
                    if hot_keyword in text.split(" "):
                        logger.info(f'Replying to {content}')
                        chat_completion = LLMClient.chat.completions.create(
                            messages=[
                                {
                                    "role": "user",
                                    "content": "When I ask you to reply to one of my messages, answer in a human-like manner.\nShort yet straight to the point.\nDo not necessarily show your thought process unless if I say otherwise. All of your replies should not exceed more than one paragraph. If I ask you to generate something only give me one. Speak in a casual manner.\nWhen a query requires context, do not ask for any, generate missing information as needed. Format your messages according to the markdown style of FB messenger, make sure that the formatting style caters to mobile, not desktop. Feel free to use messenger compatible emojis.",
                                },
                                {"role": "user", "content": ""},
                                {
                                    "role": "assistant",
                                    "content": "Got it—just hit me up with whatever you need and I'll keep it short and to the point!",
                                },
                                {"role": "user", "content": f'From user: {displayName} message: {content}'},
                            ],
                            model="openai/gpt-oss-20b",
                        )
                        logging.info(f"Groq reply: {chat_completion.choices[0].message.content}")
                        crawler.sendMessage(chat_completion.choices[0].message.content or "i got confuzzled check your code dumbahh")

                # embed = utils.DiscordEmbed()
                # embed.setEmbedAuthor(profileData['displayName'], crawler.driver.current_url, profileData['profileSrc'])
                # embed.setFooter(f"ID: {CHANNEL}") looks hella ugly
                # for v in content:
                # embed.addEmbed(28049, time.strftime("%a, %b %d %H:%M:%S"), None, v, None, None)
                # logger.info(f"Would send webhook here")
                # logger.info(f"Sent webhook with res_code: {utils.sendDiscordWebhook(embed.build())}")

            #time.sleep(10) immediately re-read

    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

    while True:
        pass

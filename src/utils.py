import random
import time

#Simulates typing by calling function while passing text given
def simTyping(element, text):
    for char in text:
        time.sleep(random.uniform(0.1, 0.3))
        element.send_keys(char)
        if random.random() < 0.1: # more randomness
            time.sleep(random.uniform(0.3, 0.7))

def sleepRand(min=0.1, max=0.3):
    time.sleep(random.uniform(min, max))
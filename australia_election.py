from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
import telegram_send
from datetime import date, datetime
from time import sleep

DRIVER_PATH = './chromedriver.exe'
URL = 'https://www.abc.net.au/news/elections/federal/2022/results?filter=all&sort=az&state=all'
ALP_VAL_XPATH = '//*[@id="content"]/div[2]/div[1]/div/section[3]/div/div/a/div[2]/dl/div[2]/dd/div[1]/span'
SLEEP_AMOUNT = 360

driver: webdriver.Chrome = webdriver.Chrome(DRIVER_PATH)

while 1:
    driver.get(URL)
    alp_val_element: WebElement = driver.find_element(by=By.XPATH, value=ALP_VAL_XPATH)
    alp_val: str = alp_val_element.text.split('\n')[0]
    msg: str = f'{datetime.now().time()} - ALP: {alp_val}'
    print(msg)
    telegram_send.send(messages=[msg])
    sleep(SLEEP_AMOUNT)
    
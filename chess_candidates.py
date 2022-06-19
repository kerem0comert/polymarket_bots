from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telegram_send
from datetime import datetime
from time import sleep
import re
from dataclasses import dataclass

DRIVER_PATH = "./chromedriver.exe"
URL = "https://chess24.com/en/watch/live-tournaments/fide-candidates-2022/3/1/"
EVALUATOR_CLASS = "evalindicatorTooltip"
EVALUATOR_REGEX = 'data-tooltip="([^"]*)\|'
RUNNING_TIME_CLASS = "runningTime black"
RUNNING_TIME_REGEX = 'runningTime black="([^"]*)\"'
TIME_PRESSURE_THRESHOLD = 10

@dataclass
class Player:
    name: str
    is_time_pressured: bool = False
@dataclass
class Match:
    match_id: int
    white: Player
    black: Player
    evaluation: float = 0

    def get_players(self) -> str: return f"{self.white.name}-{self.black.name}"

def send_telegram_msg(msg: str, match: Match) -> None:
    to_send: str = f"{datetime.now().time()}-{match.get_players()}: {msg}"
    print(to_send)
    telegram_send.send(messages=[to_send])

matches: list[Match] = [
    Match(1, Player("Ding"), Player("Rapport")),
    Match(2, Player("Caruana"), Player("Duda")),
    Match(3, Player("Radjabov"), Player("Nepomniachtchi")),
    Match(4, Player("Firouzja"), Player("Nakamura")),
]

driver: webdriver.Chrome = webdriver.Chrome(DRIVER_PATH)

while 1:
    for match in matches:
        driver.get(f"{URL}{match.match_id}")
        evaluator_html: str = (
            WebDriverWait(driver, 10)
            .until(
                EC.visibility_of_element_located((By.CLASS_NAME, EVALUATOR_CLASS))
            )
            .get_attribute("innerHTML")
        )
        '''
        running_time_html: str = (
            WebDriverWait(driver, 10)
            .until(
                EC.visibility_of_element_located((By.CLASS_NAME, RUNNING_TIME_CLASS))
            )
            .get_attribute("innerHTML")
        )
        '''
        try:
            evaluation: float = float(
                re.findall(EVALUATOR_REGEX, evaluator_html)[0]
            )
            
            print(
                f"For {match.get_players()}, current evaluation: "
                f"{evaluation} previous evaluation: {match.evaluation}"
            )
            if evaluation != match.evaluation:
                send_telegram_msg(
                    f"Evaluation moved from {match.evaluation} to {evaluation}", match
                )
                match.evaluation = evaluation
            sleep(1)
        except IndexError:
            send_telegram_msg(
                "Evaluation value could not be found with the regex.", match
            )
        except ValueError:
            send_telegram_msg("Evaluation score could not be cast to int", match)

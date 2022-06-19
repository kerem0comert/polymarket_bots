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
EVALUATOR_SELECTOR = "evalindicatorTooltip"
REGEX_FOR_EVALUATOR_SCORE = 'data-tooltip="([^"]*)\|'


@dataclass
class Match:
    match_id: 1
    players: str
    evaluation: float


def send_telegram_msg(msg: str, match: Match) -> None:
    to_send: str = f"{datetime.now().time()}-{match.players}: {msg}"
    print(to_send)
    telegram_send.send(messages=[to_send])


matches: list[Match] = [
    Match(1, "Ding-Rapport", 0),
    Match(2, "Caruana-Duda", 0),
    Match(3, "Radjabov-Nepomniachtchi", 0),
    Match(4, "Firouzja-Nakamura", 0),
]

driver: webdriver.Chrome = webdriver.Chrome(DRIVER_PATH)

while 1:
    for match in matches:
        driver.get(f"{URL}{match.match_id}")
        evaluator_html: str = (
            WebDriverWait(driver, 10)
            .until(EC.visibility_of_element_located((By.CLASS_NAME, EVALUATOR_SELECTOR)))
            .get_attribute("innerHTML")
        )
        try:
            evaluation: float = float(
                re.findall(REGEX_FOR_EVALUATOR_SCORE, evaluator_html)[0]
            )
            if evaluation != match.evaluation:
                send_telegram_msg(
                    f"Evaluation moved from {match.evaluation} to {evaluation}", match
                )
                match.evaluation = evaluation
        except IndexError:
            send_telegram_msg(
                "Evaluation value could not be found with the regex.", match
            )
        except ValueError:
            send_telegram_msg("Evaluation score could not be cast to int", match)

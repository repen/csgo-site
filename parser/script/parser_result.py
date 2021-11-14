"""
парсер результатов
"""
import requests, time
from model import Result, IntegrityError
from bs4 import BeautifulSoup
from interface import IResult
from tool import log as l
from config import REMOTE_API
from threading import Thread
from functools import partial

log = l("[ ParserSnapshot ]")

def create_task(m_id):
    url = REMOTE_API + "/task/{}".format(m_id)
    requests.get(url)
    log.info( "Create Task %s", url )

def get_result(m_id):
    url = REMOTE_API + "/result/{}".format(m_id)
    response = requests.get(url)
    data = response.json()
    if not data["result"]:
        raise ValueError(f"No data. Url {url}")
    log.info(f"Get page {url} : len [{len(data['result'])}]")
    return data["result"]

def extract_result(html):
    collect = []
    soup = BeautifulSoup(html, "html.parser")
    markets = soup.select('div[data-id]')
    for market in markets:

        score = market.select_one(".bma-score, .bm-result").text.strip() if market.select_one(".bma-score, .bm-result") else ""
        winner = 'left' if "betting-won-team1" in market["class"] else "right"
        c_id = int(market["data-id"])
        collect.append( IResult(score=score, winner=winner, c_id=c_id).__dict__ )
    # breakpoint()

    return collect
    # breakpoint()

def write_database(items):
    log.info(f"start write result [{len(items)}]")
    try:
        Result.insert_many(items).execute()
    except IntegrityError:
        pass
    log.info(f"end write result [{len(items)}]")


def work(m_id: int):
    html = get_result( m_id )
    markets = extract_result(html)
    write_database(markets)

def deffered(first, wait ,second):
    first()
    log.info("Run First item")
    time.sleep(wait)
    second()
    log.info("Run Second item")


def starter(m_id: int):
    try:
        work(m_id)
    except ValueError:

        p_deffered = partial(
            deffered,
            lambda : create_task(m_id),
            120,
            lambda : work(m_id)
        )

        Thread( target=p_deffered).start()
        log.error("[!Error]", exc_info=True)

def main():
    work(280262)
    # starter(280262)




if __name__ == '__main__':
    main()
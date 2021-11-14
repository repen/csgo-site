import requests, re, time
from config import REMOTE_API
from bs4 import BeautifulSoup
from interface import IMarket, IFixture, IKoef
from datetime import datetime
from model import Fixture, IntegrityError, Market, Koef
from tool import log as l
from itertools import count
from parser_result import starter as write_result
from threading import Thread

log = l("Parser")

def timeit(f):

    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        log.info( "Time run {} {}".format(te-ts, str(f)) )
        return result

    return timed

def get_page():
    response = requests.get(REMOTE_API + "/html")
    data = response.json()
    html = data['data']
    return html

def dsearch_fixture():
    I = 0
    def search_fixture(fixtures):
        nonlocal I
        if I % 60 == 0:
            log.info(f"== Check fixtures [{len(fixtures)}] for write db. I={I} ==")
            for fixture in fixtures:
                [x.extract() for x in fixture.select("div.bet-team__rank")]
                m_id = int(fixture["data-id"])
                m_timestamp = int( fixture.select_one(".sys-time-left")["data-timestamp"] )
                m_team1 = fixture.select_one("div.bet-team__name.sys-t1name").text.strip()
                m_team2 = fixture.select_one("div.bet-team__name.sys-t2name").text.strip()
                league = fixture.select_one(".bet-match__picture-text")
                league = league.text.strip() if league else ""
                OFixture = IFixture(m_id=m_id, m_timestamp=m_timestamp, m_team1=m_team1,
                         m_team2=m_team2, m_league=league
                )
                try:
                    Fixture.insert( OFixture.__dict__ ).execute()
                except IntegrityError:
                    log.info( "Fixture already exists: %s", str(OFixture) )
        I += 1
    return search_fixture

search_fixture = dsearch_fixture()


def get_fixtures(html):
    # CSS_SELECTOR = ".sys-games-next .bet-item.sys-betting.bet_coming[data-id]" no live
    # live and wait
    CSS_SELECTOR = ".sys-games-next .bet-item.sys-betting.bet_coming[data-id], .bet-item.sys-betting.bet-stream"
    soup = BeautifulSoup(html, "html.parser")
    fixtures = soup.select(CSS_SELECTOR)
    return fixtures


def extract_markets(soup, timestamp):
    collect = []
    events = soup.select("div.bet-events__item")
    for event in events:
        # eid = int(event.select_one("div.bet-event.sys-betting.bet_coming")["data-id"])
        market_name = event.select_one(".bet-event__text-inside-part").text.strip()
        left_val  = int(event.select_one("div.bet-currency.sys-stat-abs-1").text.strip().replace(" ", ""))
        right_val = int(event.select_one("div.bet-currency.sys-stat-abs-2").text.strip().replace(" ", ""))

        try:
            c_id = event.select_one("div.bet-event[data-id]")["data-id"].strip()
        except TypeError:
            log.error(f"TypeError: {str(event)}", exc_info=True)
            continue
            # breakpoint()

        collect.append( IMarket(
            m_id=int(soup["data-id"]),
            c_id=int(c_id), 
            name=market_name, 
            left_value=left_val,
            right_value=right_val, 
            m_snapshot_time=timestamp).__dict__
        )
   
    market_name = "Main"
    left=int( soup.select_one("div.bet-button__content-main.bet-currency.sys-stat-abs-1").text.strip().replace(" ", "") )
    right=int( soup.select_one("div.bet-button__content-main.bet-currency.sys-stat-abs-2").text.strip().replace(" ", "") )

    collect.append(
        IMarket( m_id=int(soup["data-id"]), c_id=int(soup["data-id"]),
            name=market_name, left_value=left, right_value=right, m_snapshot_time=timestamp).__dict__
    )

    return collect

def extract_koef(soup, timestamp):
    left_koef  = soup.select_one(".sys-stat-koef-1").text.replace("x", "").strip()
    right_koef = soup.select_one(".sys-stat-koef-2").text.replace("x", "").strip()
    left_proc  = soup.select_one(".sys-stat-proc-1").text.replace("%", "").strip()
    right_proc = soup.select_one(".sys-stat-proc-2").text.replace("%", "").strip()

    koef = IKoef(
        left_value=left_koef,
        right_value=right_koef, 
        market_name="Main",
        left_percent=left_proc, 
        right_percent=right_proc,
        m_id=int(soup["data-id"]), 
        m_snapshot_time=timestamp
    )

    return koef.__dict__


def write_database(markets, koefs):
    log.info(f"== Start write [markets] in database Market. Elements len: [{len(markets)}]")
    Market.insert_many( markets ).execute()
    Koef.insert_many(koefs).execute()
    log.info(f"== End write [markets] in database Market. Elements len: [{len(markets)}]")

def init_check_end_game():
    """ Проверять закончился матч если да, то записать данные в базу
    """
    fixture_id = set()
    def check_end_game(koef_list):
        current_id = { x['m_id'] for x in koef_list }
        diff = fixture_id.difference( current_id )

        if diff:
            for m_id in diff:
                Thread(target=write_result, args=(m_id, )).start()
                log.info(f"[ Send { m_id } write in result table. ]")

        fixture_id.clear()
        fixture_id.update( current_id )
    return check_end_game

check_end_game = init_check_end_game()

@timeit
def work():
    html = get_page()
    current_time = datetime.now().timestamp().__int__()

    fixtures = get_fixtures( html )
    search_fixture(fixtures)
    market_data = []
    koef_data = []

    for fixture in fixtures:
        markets = extract_markets(fixture, current_time)
        koef = extract_koef(fixture, current_time)
        market_data.extend( markets )
        koef_data.append( koef )

    write_database( market_data, koef_data )
    check_end_game( koef_data )


def main():
    for c in count(start=1):
        work()
        log.info(f"=== Count {c} ====")
        time.sleep(60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.info("=== End work ===")
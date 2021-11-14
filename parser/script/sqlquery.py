"""
В общем нужны все игры где от 2 до 5 карт играют команды,
от 1000 руб на каждом из исходов, исходы
в общем на матч, и на каждую из карт. Скан последний самый,
с финальными суммами результатами

В игре должно быть 2 игры и более
Сумма на исход Main от 1000
Cумма на исход  [Карта #1] Победа на карте от 1000
Cумма на исход  [Карта #2] Победа на карте от 1000

"""
from model import db
from dataclasses import dataclass
from datetime import datetime
from peewee import IntegrityError, OperationalError

import csv

MARKET_NAME = "[Карта #2] Победа на карте"

def write_csv(rows):

    with open(f'{MARKET_NAME}.csv', mode='w') as csv_file:
        fieldnames = ['ID', 'Время', 'Команда 1', 'Команда 2',
                      'Лига', 'Рынок', 'Объем рынка 1', 'Объем рынка 2']
        writer = csv.writer(csv_file)

        writer.writerow(fieldnames)
        for row in rows:
            writer.writerow(row.values())

@dataclass
class IResult:
    match_id: str
    start_time: int
    home_team: str
    away_team: str
    league: str
    market: str
    home_value: int
    away_value: int



sql01 = """SELECT f.m_id, f.m_timestamp, f.m_team1, f.m_team2, f.m_league, market.name, market.left_value, market.right_value FROM market
    INNER JOIN fixture f on market.m_id = f.m_id
WHERE market.c_id={c_id} and market.m_id={m_id} ORDER BY market.id DESC LIMIT 1;
"""

query = db.execute_sql("SELECT m_id, m_timestamp FROM fixture;")
all_ids = [x for x in query.fetchall()]


good = []
for e, fixture_id in enumerate(all_ids):
    sql = "SELECT * FROM market WHERE m_id={} and name='{}' ".format(fixture_id[0], MARKET_NAME) + \
          "and right_value > 999 and left_value > 999 and m_snapshot_time < {}".format(fixture_id[1])
    try:

        print(e, len(all_ids))
        query01 = db.execute_sql(sql)
    except OperationalError:
        break

    result = [x for x in query01.fetchall()]
    if result:
        good.append(result[-1])
    if e == 400:
        break



market_list = []
for market in good:
    m_id = market[1]
    c_id = market[2]
    query = db.execute_sql(sql01.format(c_id=c_id, m_id=m_id))
    result = IResult(*query.fetchall()[0])
    result.start_time = datetime.fromtimestamp(result.start_time).isoformat()
    market_list.append(result.__dict__)
    # market_list.append( IResult(*result.fetchall()[0]).__dict__ )

write_csv(market_list)
# breakpoint()
from peewee import Model, IntegerField, IntegrityError, CharField, SqliteDatabase, MySQLDatabase
from config import BASE_DIR, HOST, SHARE_DIR
import os

IntegrityError = IntegrityError

# если база sqlite
db = SqliteDatabase(
    os.path.join( SHARE_DIR, "betscsgo.sqlite"), pragmas={'journal_mode': 'wal', })

# если база mysql
# db = MySQLDatabase("cs", user="pog",
#                         password="qwerty123", port=3306, host=HOST )

class Fixture(Model):
    m_id = IntegerField(unique=True)
    m_timestamp = IntegerField()
    m_team1  = CharField()
    m_team2  = CharField()
    m_league = CharField()

    class Meta:
        database = db

class Market(Model):
    m_id = IntegerField(index=True)
    c_id = IntegerField()
    m_snapshot_time= IntegerField(index=True)
    left_value = IntegerField()
    name = CharField()
    right_value = IntegerField()

    class Meta:
        database = db

class Result(Model):
    c_id = IntegerField(unique=True)
    winner = CharField()
    score  = CharField()

    class Meta:
        database = db


class Koef(Model):
    m_id = IntegerField(index=True)
    m_snapshot_time= IntegerField(index=True)

    left_value  = CharField()
    market_name = CharField(default="Main")
    right_value = CharField()

    left_percent = CharField()
    right_percent = CharField()

    class Meta:
        database = db

Fixture.create_table()
Market.create_table()
Result.create_table()
Koef.create_table()

# breakpoint()
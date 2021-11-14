from peewee import *
from config import SHARE_DIR
import os

db = SqliteDatabase( os.path.join( SHARE_DIR, "datahtml.db" ), pragmas={'journal_mode': 'wal', } )
dbs = SqliteDatabase( os.path.join( SHARE_DIR, "result_page.db" ), pragmas={'journal_mode': 'wal', } )


class HtmlData(Model):
    m_time   = IntegerField()
    html     = BlobField()


    @staticmethod
    def get_last_html():
        # .decode('unicode-escape')
        query = HtmlData.select().order_by(HtmlData.id.desc()).get()
        data = query.__data__
        return data

    class Meta:
        database = db


class ResultPage(Model):
    m_time = IntegerField()
    m_id = IntegerField()
    data = BlobField()

    @staticmethod
    def get_match_result(m_id):
        result = False
        query = ResultPage.select().where(ResultPage.m_id == m_id)
        if query:
            # result = [x for x in query.namedtuples()][0]
            result = [x for x in query.namedtuples()][0]._asdict()
        return result

    class Meta:
        database = dbs


if __name__ == '__main__':
    pass
    # query = ResultPage.get_match_result(267188)
    # breakpoint()
    # print(len(query))

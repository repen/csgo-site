from peewee import *
from Globals import SHARE_DIR
import os


with open(os.path.join( SHARE_DIR, "task.txt" ), "w", encoding="utf-8") as f:
    f.write("")

db  = SqliteDatabase( os.path.join( SHARE_DIR, "datahtml.db" ),
                      pragmas={'journal_mode': 'wal', } )
db2 = SqliteDatabase( os.path.join( SHARE_DIR, "result_page.db" ),
                      pragmas={'journal_mode': 'wal', } )


class HtmlData(Model):
    m_time   = IntegerField()
    html     = BlobField()

    @staticmethod
    def auto_clear_db():
        cursor = db.execute_sql( 'SELECT count(*) FROM HtmlData' )
        quantity_rows = cursor.fetchone()[0]
        cursor = db.execute_sql( 'SELECT rowid FROM HtmlData ORDER BY rowid LIMIT 1' )
        first_row_id = cursor.fetchone()[0]
        "38888 - 18000"
        if quantity_rows > 200:
            for x in range(first_row_id, first_row_id + 101):
                HtmlData.delete().where(HtmlData.id == x).execute()

        return None

    @staticmethod
    def insert_remove(data):
        HtmlData.insert(data).execute()
        HtmlData.autoremove()

    @staticmethod
    def count_row():
        cursor = db.execute_sql( "SELECT count() FROM htmldata" )
        data = cursor.fetchone()
        return data[0]

    @staticmethod
    def autoremove():
        if HtmlData.count_row() > 200:
            ids = HtmlData.select( HtmlData.id ).limit(150)
            for id_ in ids:
                HtmlData.delete().where( HtmlData.id == id_).execute()


    class Meta:
        database = db

class ResultPage(Model):
    m_time   = IntegerField()
    m_id = IntegerField()
    data = BlobField()


    class Meta:
        database = db2

HtmlData.create_table()
ResultPage.create_table()

if __name__ == '__main__':
    query = HtmlData.select()
    print(len(query))

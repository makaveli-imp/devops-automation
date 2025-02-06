import datetime
import psycopg2
from config.config import Config
import os
from dotenv import load_dotenv

load_dotenv()

class Authority:
    authorities = []

    def __init__(self, id, authority, app_id):
        self.id = id
        self.authority = authority
        self.app_id = app_id
        self.dir = ""
        self.xpaths = None
        self.errors = None

    @staticmethod
    def getauthorities(app_id):
        conn = psycopg2.connect(dbname=os.environ.get('PG_DBNAME'), host=os.environ.get('PG_HOST'), port=os.environ.get('PG_PORT'),
                                    user=os.environ.get('PG_USER'), password=os.environ.get('PG_PASSWORD'))
        
        cur = conn.cursor()
        cur.execute('''SELECT
                                table_authority.id ,table_authority.authority
                                FROM
                                 table_authority 
                                where
                                table_authority.id in( select authority_id from table_applications_pool_applic_authority where application_pool_id = %s)
                                group by table_authority.authority,table_authority.id
                                ORDER  BY table_authority.id DESC 
                                ''', (app_id,))
        result = [Authority(link[0], link[1], app_id) for link in cur.fetchall()]
        cur.close()
        conn.close()
        return result

    @staticmethod
    def getauthoritiesTest():
        # 81 16417 16 11
        conn = psycopg2.connect(dbname=os.environ.get('PG_DBNAME'), host=os.environ.get('PG_HOST'), port=os.environ.get('PG_PORT'),
                                    user=os.environ.get('PG_USER'), password=os.environ.get('PG_PASSWORD'))
        cur = conn.cursor()
        cur.execute('''SELECT
                                table_authority.id ,table_authority.authority
                                FROM
                                 table_authority 
                                where
                                table_authority.id in (81, 16417 ,16, 11)
                                group by table_authority.authority,table_authority.id
                                ORDER  BY table_authority.id DESC 
                                ''')
        result = [Authority(link[0], link[1]) for link in cur.fetchall()]
        cur.close()
        conn.close()
        return result

    def generatedir(self):
        if self.dir == "":
            import time
            self.dir = time.strftime("%Y%m%d\\%H%M%S_") + self.authority + '\\'
        return self.dir

    def getXpaths(self):
        # if self.xpaths == None:
        conn = psycopg2.connect(dbname=os.environ.get('PG_DBNAME'), host=os.environ.get('PG_HOST'), port=os.environ.get('PG_PORT'),
                                    user=os.environ.get('PG_USER'), password=os.environ.get('PG_PASSWORD'))
        cur = conn.cursor()
        cur.execute('''SELECT t.xpath FROM digital_pub_xpath t WHERE authority_id = %s  and not error  
                                        ''', (self.id,))
        self.xpaths = [link[0] for link in cur.fetchall()]
        cur.close()
        conn.close()
        return self.xpaths

    def getErrors(self):
        # if self.xpaths == None:
        conn = psycopg2.connect(dbname=os.environ.get('PG_DBNAME'), host=os.environ.get('PG_HOST'), port=os.environ.get('PG_PORT'),
                                    user=os.environ.get('PG_USER'), password=os.environ.get('PG_PASSWORD'))
        cur = conn.cursor()
        cur.execute('''SELECT t.xpath FROM digital_pub_xpath t WHERE authority_id = %s  and error
                                        ''', (self.id,))
        self.errors = [link[0] for link in cur.fetchall()]
        cur.close()
        conn.close()
        return self.errors


class Visit:
    i = 1

    def __init__(self, id, addin):
        self.index = 1
        self.id = id
        self.addin = addin
        self.dir = ""
        self.filename = "%d.jpeg" % (self.id,)

    def getfilename(self):
        return self.generatedir() + self.filename

    def generatedir(self):
        if self.dir == "":
            import time
            self.dir = time.strftime("%Y\\%m\\%d\\")
            import pathlib
            pathlib.Path(Config.instance.directories.ssdir + self.dir).mkdir(parents=True, exist_ok=True)
        return self.dir

    @staticmethod
    def generatevisitetest(rubric):
        rubric.visit = Visit(Visit.i, datetime.datetime.now())
        Visit.i += 1
        return rubric.visit

    @staticmethod
    def generatevisite(rubric):
        conn = psycopg2.connect(dbname=os.environ.get('PG_DBNAME'), host=os.environ.get('PG_HOST'), port=os.environ.get('PG_PORT'),
                                    user=os.environ.get('PG_USER'), password=os.environ.get('PG_PASSWORD'))
        cur = conn.cursor()
        cur.execute('''INSERT INTO digital_pub_visite(link_id,app_pool_id,v_index)
                             VALUES(%s,%s, trunc(EXTRACT(HOUR FROM now())/6));
                             select currval('digital_pub_visite_id_seq') as id, now() ;''', (rubric.id, rubric.authority.app_id))
        result = cur.fetchone()
        result = Visit(result[0], result[1])
        rubric.visit = result
        conn.commit()
        cur.close()
        conn.close()
        return result


class Rubric:
    visitc = 0

    def __init__(self, id, link, authority):
        self.visit = Rubric.visitc
        Rubric.visitc += 1
        self.id = id
        self.link = link
        self.authority = authority
        self.dir = ""

    def generatedir(self):
        if self.dir == "":
            import time
            self.dir = self.authority.generatedir() + time.strftime("%H%M%S_") + str(self.id) + '\\'
        return self.dir

    @staticmethod
    def getrebrics():
        result = []
        for app_id in Config.instance.services.tracker.pool:
            for authority in Authority.getauthorities(app_id):
                conn = psycopg2.connect(dbname='imperiumdb', host='192.168.3.23', port=5432, user='pub_offline',
                                        password='B0&s$8Sz0Q%HP4fa')
                cur = conn.cursor()
                cur.execute('''select links.id,table_links.link ,links.authority,links.authority_id from (SELECT
                            table_links.rubrique_id,table_authority.authority,table_links.authority_id,
                            max(table_links.id) as id
                            FROM
                            table_links 
                            inner join table_authority on table_links.authority_id = table_authority.id
                            where
                            table_links.authority_id = %s
                            and table_links.rss is false
                            and table_links.actif is true
                            group by table_links.rubrique_id,table_authority.authority,table_links.authority_id ) links
                            inner join  table_links on links.id = table_links.id
                            group by links.id,table_links.link,links.authority,links.authority_id''', (authority.id,))
                result.extend([Rubric(link[0], link[1], authority) for link in cur.fetchall()])
                cur.close()
                conn.close()
        return result

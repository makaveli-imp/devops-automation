import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


class Query:
    queries=[]
    def __init__(self, name, secteur):
        self.name = name
        self.secteur = secteur


class Secteur:
    secteurs=[]
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.queries = []

    @staticmethod
    def getsecteurs():
        Query.queries = []
        Secteur.secteurs = []
        conn = psycopg2.connect(dbname=os.environ.get('PG_DBNAME'), host=os.environ.get('PG_HOST'), port=os.environ.get('PG_PORT'),
                                    user=os.environ.get('PG_USER'), password=os.environ.get('PG_PASSWORD'))
        cur = conn.cursor()
        cur.execute('''SELECT
                                  table_pub_s_secteur.secteur_id,
                                  table_pub_secteurs.secteur,
                                  table_key_word_crawl.key_word
                                FROM
                                  public.table_ads_nav_server
                                  inner join public.table_ads_nav_server_applic_secteur_pub on table_ads_nav_server.id = table_ads_nav_server_applic_secteur_pub.nav_server_id
                                  inner join public.table_pub_secteurs on table_ads_nav_server_applic_secteur_pub.secteur_pub_id = table_pub_secteurs.id
                                  inner join public.table_pub_s_secteur on table_pub_secteurs.id = table_pub_s_secteur.secteur_id

                                  inner join public.table_key_word_crawl_applic_pub_s_secteur on table_pub_s_secteur.id = table_key_word_crawl_applic_pub_s_secteur.s_secteur_id


                                  inner join public.table_key_word_crawl on table_key_word_crawl_applic_pub_s_secteur.key_word_crawl_id = table_key_word_crawl.id


                                  where table_ads_nav_server.identifier = table_ads_nav_server.identifier 
                                and table_key_word_crawl.actif
                                and table_key_word_crawl_applic_pub_s_secteur.actif;''')
        result=cur.fetchall()
        for row in result :
            s = [secteur for secteur in Secteur.secteurs if row[0] == secteur.id]
            if len(s) > 0:
                q = Query(row[2], s[0])
                s[0].queries.append(q)
            else:
                tmp = Secteur(row[0], row[1])
                q = Query(row[2], tmp)
                tmp.queries.append(q)
                Secteur.secteurs.append(tmp)
            Query.queries.append(q)
        cur.close()
        conn.close()
        return Secteur.secteurs

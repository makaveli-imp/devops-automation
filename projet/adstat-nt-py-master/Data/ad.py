import json
import psycopg2
import redis
import os
from dotenv import load_dotenv
from config.config import Config

load_dotenv()
class AdElement():
    counter = 0

    def __init__(self, rubric, filesources, redirectlink, codx, cody,
                 dimw, dimh, xpath, hashs, is_video = False, video_url = None):
        AdElement.counter += 1
        print("total ads : ", AdElement.counter)
        self.container_id = 0
        self.rubric = rubric
        self.dir = ""
        self.filesources = filesources
        self.redirectlink = redirectlink
        try:
            self.clicktag = redirectlink[0]
        except:
            self.clicktag = " "
        if self.clicktag is None:
            self.clicktag = " "
        self.codx = codx
        self.cody = cody
        self.dimw = dimw
        self.dimh = dimh
        self.xpath = xpath
        self.hashs = hashs
        self.index = rubric.visit.index
        self.app_id = rubric.authority.app_id
        self.is_video = is_video
        self.video_url = video_url
        rubric.visit.index += 1
        self.filename = "animation.gif"

    def getfilename(self):
        return self.generatedir() + self.filename

    def generatejsonfile(self):
        with open(Config.instance.directories.adsdir + self.getfilename() + ".JSON", 'w') as out:
            out.write(json.dumps(self.filesources))
            out.close()

    def generatedir(self):
        if self.dir == "":
            self.dir = self.rubric.generatedir() + 'SSAd%02d\\' % (self.index,)
            import pathlib
            pathlib.Path(Config.instance.directories.adsdir + self.dir).mkdir(parents=True, exist_ok=True)
        return self.dir

    def insert(self):
        try:
            r = redis.StrictRedis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=os.environ.get('REDIS_DB'), password=os.environ.get('REDIS_PASSWORD'))
            pub_id = None
            for hash_str in self.hashs:
                pub_id = r.hget(hash_str, 'p')
                if pub_id is not None:
                    print('already exist')
                    break

            conn = psycopg2.connect(dbname=os.environ.get('PG_DBNAME'), host=os.environ.get('PG_HOST'), port=os.environ.get('PG_PORT'),
                                    user=os.environ.get('PG_USER'), password=os.environ.get('PG_PASSWORD'))
            cur = conn.cursor()

            if pub_id is None:
                print('first time')
                if self.is_video:
                    print('++is video: ', self.video_url)
                    query = """INSERT INTO digital_pub(
                                link_id, container_id, dim_x, dim_y,
                                        dim_w, dim_h, xpath , visite_id, isnewsletter, added_in, microservice_id, is_video, video_url)
                                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *; """
                    cur.execute(query, (
                    self.rubric.id, 0, self.codx, self.cody, self.dimw, self.dimh, self.xpath,
                    self.rubric.visit.id, False, self.rubric.visit.addin, self.app_id, True, self.video_url))
                else:
                    hash_str = self.hashs[0]
                    query = """INSERT INTO digital_pub(
                                link_id, container_id, path_pub, dim_x, dim_y,
                                        dim_w, dim_h, xpath , hash_str,clicktag,visite_id,isnewsletter,added_in, microservice_id)
                                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s, %s) RETURNING *; """
                    cur.execute(query, (
                    self.rubric.id, 0, self.getfilename(), self.codx, self.cody, self.dimw, self.dimh, self.xpath, hash_str ,self.clicktag,
                    self.rubric.visit.id, False, self.rubric.visit.addin, self.app_id))
                result =cur.fetchone()
                conn.commit()
                pub_id = result[0]
                print("pub_id new = ", pub_id)
                for hash_str in self.hashs:
                    print("hash added = ", hash_str)
                    r.hset(hash_str, 'p', pub_id)
            else:
                pub_id = pub_id.decode()
                print("pub_id old = ", pub_id)
            

            query = """INSERT INTO digital_pub_trace(
                        link_id, pub_id, container_id, path_pub, dim_x, dim_y,
                                dim_w, dim_h, xpath ,clicktag,visite_id,isnewsletter,added_in, microservice_id)
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s, %s) RETURNING *; """
            cur.execute(query, (
            self.rubric.id, pub_id, 0, self.getfilename(), self.codx, self.cody, self.dimw, self.dimh, self.xpath ,self.clicktag,
            self.rubric.visit.id, False, self.rubric.visit.addin, self.app_id))
            result = cur.fetchone()
            conn.commit()
            print("ad_id = ",result[0])
            
            cur.close()
        except Exception as e:
            print(e)
        finally:
            conn.close()

import tweepy
import pymysql
from dotenv import load_dotenv
import os
from os.path import join,dirname
from datetime import datetime, timezone, timedelta

dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
MYSQL_HOST=os.environ.get("MYSQL_HOST")
MYSQL_USER=os.environ.get("MYSQL_USER")
MYSQL_PASSWORD=os.environ.get("MYSQL_PASSWORD")
MYSQL_DATABASE=os.environ.get("MYSQL_DATABASE")
API_Key=os.environ.get("API_Key")
API_Key_Secret=os.environ.get("API_Key_Secret")
Access_Token=os.environ.get("Access_Token")
Access_Token_Secret=os.environ.get("Access_Token_Secret")

def make_connection():
    return pymysql.connect(host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DATABASE,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

auth = tweepy.OAuthHandler(API_Key, API_Key_Secret)
auth.set_access_token(Access_Token, Access_Token_Secret)
api = tweepy.API(auth)

conn = make_connection()
with conn.cursor() as cursor:
    sql = "SELECT * FROM contest_info"
    cursor.execute(sql)
    for tmp in cursor:
        day, time, _, _ = tmp["schedule"].split()
        start_time = datetime.strptime(day + " " + time, "%Y-%m-%d %H:%M:%S")
        cur_jp = datetime.now() + timedelta(hours=9)
        if cur_jp < start_time and cur_jp + timedelta(minutes=90) > start_time:
            res = []
            res.append(tmp["title"])
            res.append(tmp["schedule"])
            res.append(tmp["rated"])
            res.append("tester: " + tmp["tester"])
            res.append(tmp["url"])
            api.update_status("\n".join(res))
            sql = "DELETE FROM contest_info WHERE title = %s"
            cursor.execute(sql, (tmp["title"]))
        elif cur_jp > start_time:
            sql = "DELETE FROM contest_info WHERE title = %s"
            cursor.execute(sql, (tmp["title"]))
conn.commit()
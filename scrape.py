import requests
from bs4 import BeautifulSoup
import pymysql
from dotenv import load_dotenv
import os
from os.path import join,dirname

dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
MYSQL_HOST=os.environ.get("MYSQL_HOST")
MYSQL_USER=os.environ.get("MYSQL_USER")
MYSQL_PASSWORD=os.environ.get("MYSQL_PASSWORD")
MYSQL_DATABASE=os.environ.get("MYSQL_DATABASE")
def make_connection():
    return pymysql.connect(host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DATABASE,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

base_sp = BeautifulSoup(requests.get("https://onlinemathcontest.com/contests/all").content)
conn = make_connection()
with conn.cursor() as cursor:
    sql = "SELECT url FROM contest_info"
    cursor.execute(sql)
    contest_urls = [tmp["url"] for tmp in cursor]

    for tmp in base_sp.find_all("paper-card"):
        if tmp.find("h2") and tmp.find("h2").contents[0] == " Past Contests ":
            break
        li = tmp.find_all("li")
        schedule = li[0].contents[0].strip()
        rated = li[1].contents[0].strip()
        url = tmp.find("a")["href"]
        sp = BeautifulSoup(requests.get(url).content)
        title = sp.find("h1").contents[0]
        tester = []
        for tmp in filter(lambda x: x.contents and "tester" in x.contents[0], sp.find_all("p")):
            tester = [a.contents[0].strip() for a in tmp.find_all("a")]
        #元々存在するかどうかで場合分け
        if url in contest_urls:
            print("UPDATE", title)
            sql = "UPDATE contest_info SET title = %s, schedule = %s, rated = %s, tester = %s WHERE url = %s"
        else:
            print("INSERT", title)
            sql = "INSERT INTO contest_info (title, schedule, rated, tester, url) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (title, schedule, rated, ",".join(tester), url))
conn.commit()
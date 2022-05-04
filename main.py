import sqlite3
from urllib.request import urlopen
from urllib.error import HTTPError
import json
from tqdm import tqdm


con = sqlite3.connect('subtitles.db')

cur = con.cursor()

# создаем таблицу
cur.execute("SELECT name FROM sqlite_master WHERE type= 'table'; ")
tables = cur.fetchall()
# print(tables)
if not tables or ('subtitles' not in tables[0]):
    cur.execute(
        """
        CREATE TABLE subtitles
        (videoId integer, duration integer, content text, startOfParagraph integer, startTime integer) 
        """)


videoId = 1


def parse_video_subtitles(videoId):
    lang = 'en'
    try:
        ted_url = urlopen(f'https://www.ted.com/talks/subtitles/id/{videoId}/lang/{lang}')
    except HTTPError as e: return None


    ted_json = ted_url.read().decode('utf8')
    ted_list = json.loads(ted_json)

    rows = []
    for indict in ted_list['captions']:
        rows.append([videoId, indict['duration'], indict['content'], indict['startOfParagraph'], indict['startTime']])
    con = sqlite3.connect('subtitles.db')
    cur = con.cursor()
    cur.executemany("insert into subtitles values (?, ?, ?, ?, ?)", rows)
    con.commit()
    con.close()


for videoId in tqdm(range(1, 1001)):
    parse_video_subtitles(videoId)
c = cur.execute("select * from subtitles")
#print(c.fetchall())

con.close()

xEQyrmBQGhxkmRZllGCYb60Et27VS1Zw
postgres://cvlubhat:xEQyrmBQGhxkmRZllGCYb60Et27VS1Zw@suleiman.db.elephantsql.com/cvlubhat

import os
import urllib.parse as up
import psycopg2

up.uses_netloc.append("postgres")
url = up.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(database=url.path[1:],
user=url.username,
password=url.password,
host=url.hostname,
port=url.port
)
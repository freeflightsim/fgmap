#!/usr/bin/env python

import ConfigParser
import sqlalchemy as sa
from sqlalchemy.ext.sqlsoup import SqlSoup


## Gt db credentials from config.ini
conf = ConfigParser.ConfigParser()
conf.read("../config/config.ini")
db_url = conf.get("database", "url")
print db_url

engine = sa.create_engine(db_url, echo=False)
#session = sa.sessionmaker(bind=some_engine)


f = open('./mysql_create.sql')
sql = f.read()
f.close()
#print sql

status = engine.execute(sql)
print status, "###########"

#engine.execute("select 1").scalar()


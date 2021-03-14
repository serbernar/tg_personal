import databases
import sqlalchemy

import settings

database = databases.Database(settings.DATABASE_URL)
metadata = sqlalchemy.MetaData()

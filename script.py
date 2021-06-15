import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
conect = psycopg2.connect(dbname='postgres', user='postgres', host='localhost', password='123')
conect.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursorr = conect.cursor()
cursorr.execute("CREATE DATABASE MangaList; ")
print("Se ha creado exitosamente la base de datos MangaList")

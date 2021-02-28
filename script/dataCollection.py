# coding: utf-8

import mariadb
import sys


try:
    conn = mariadb.connect(
        user="root",
        password="TBzk0922k3*",
        host="localhost",
        port=3306,
        database="moneybot"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()

print(cur)



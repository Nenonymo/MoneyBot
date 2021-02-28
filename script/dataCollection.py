# coding: utf-8

import mariadb
import sys
import os


#get the connection parameters
this_file = os.path.dirname(os.path.abspath(__file__))
dbConfigFile = os.path.join(this_file, '..'+os.sep+'notes.txt')


def initializeDBConnection(dbConnectionConfigPath, startLine): #Works perfectly
    with open(dbConnectionConfigPath, 'r') as f:
        dbArgsUntreated = f.readlines()[startLine:startLine+5]
        dbArgs = dict()
        for i in dbArgsUntreated:
            a = i.replace(' ', '').strip('\n').split(sep='=')
            dbArgs[a[0]] = a[1]

    try:
        conn = mariadb.connect(
            user=dbArgs['User'],
            password=dbArgs['Password'],
            host=dbArgs['Host'],
            port=int(dbArgs['Port']),
            database=dbArgs['Database']
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    cursor = conn.cursor()

    return((cursor, conn))

def createIfNotExisting (serverID, serverName, cursor, connection): #Works but don't save the name of the server
    try:
        cursor.execute("SELECT COUNT(id) AS nbr FROM server WHERE id=?", (serverID,))
        for (nbr) in cursor:
            if nbr[0] != 0:
                return(1)
        cursor.execute("INSERT INTO server (id,name) VALUES (?, ?)", (serverID,''))
        connection.commit()
        return(0)
    except  mariadb.Error as e:
        print(e)
        return(2)

def moneyTransfer (cursor, conn, servID, id1, id2, amount): #Don't work
    try:
        cursor.execute("SELECT userid, serverid, moneyAmount FROM userserver WHERE userid=? AND serverid=?", (id1, servID))
        for (uID, sID, mA) in cursor:
            print(uID, sID, mA)
            if mA < amount:
                return 1
        
        cursor.execute("UPDATE userserver SET moneyAmount = moneyAmount - ? WHERE userid=? AND serverid=?", (amount, id1, servID))
        cursor.execute("UPDATE userserver SET moneyAmount = moneyAmount + ? WHERE userid=? AND serverid=?", (amount, id2, servID))
        conn.commit()
        return(0)

    except mariadb.Error:
        print("Error with the command: one of the users didn't initialized his account")
        return(2)
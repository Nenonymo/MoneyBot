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
        cursor.execute("SELECT COUNT(id) AS nbr FROM servers WHERE id=?", (serverID,))
        for (nbr) in cursor:
            if nbr[0] != 0:
                return(1)
        cursor.execute("INSERT INTO servers (id,name) VALUES (?, ?)", (serverID,''))
        connection.commit()
        return(0)
    except  mariadb.Error as e:
        print(e)
        return(2)

def createBankAccount (cursor, conn, servID, uID, uName): #Works perfectly
    try:
        cursor.execute("SELECT COUNT(id) AS nbr FROM users WHERE id=?", (uID,))
        for nbr in cursor:
            if nbr[0] != 0: #Compte utilisateur déjà existant
                exist = True
            else:
                exist = False

        if exist == False: #compte utilisateur inexistant
            cursor.execute("INSERT INTO users (id) VALUES (?)", (uID,))
            conn.commit()
        
        cursor.execute("SELECT COUNT(userID) AS nbr FROM userserver WHERE serverID=? AND userID=?", (servID, uID))
        for nbr in cursor:
            if nbr[0] != 0:
                return(1)
        cursor.execute("INSERT INTO userserver (serverID, userID, moneyAmount, name, InterractionsAmount) VALUES (?, ?, ?, ?, ?)", (servID, uID, 200, uName, 0)) #insertion couple servID/uID
        conn.commit()
        return(0)
    except mariadb.Error as e:
        print(e)
        return(2)

def getMoneyAmounts (cursor, connection, servID): #Works perfectly
    try:
        cursor.execute("SELECT userID, name, moneyAmount FROM userserver WHERE serverID=? ORDER BY moneyAmount DESC, name", (servID,))
        moneyTable = [(k,n,v) for (k, n, v) in cursor]
        return(moneyTable)
    except mariadb.Error as e:
        print(e)
        return

def getMoneyAmount1Account (cursor, connection, servID, uID):
    try:
        cursor.execute("SELECT moneyAmount FROM userserver WHERE serverID=? AND userID=? ORDER BY moneyAmount DESC", (servID,uID))
        moneyTable = [a for a in cursor]
        return(moneyTable)
    except mariadb.Error as e:
        print(e)
        return

def moneyTransfer (cursor, conn, servID, id1, id2, amount): #seem's to work
    try:
        cursor.execute("SELECT userid, serverid, moneyAmount FROM userserver WHERE userid=? AND serverid=?", (id1, servID))
        for (uID, sID, mA) in cursor:
            print(uID, sID, mA)
            if int(mA) < int(amount):
                return 1
        
        cursor.execute("UPDATE userserver SET moneyAmount = moneyAmount - ? WHERE userid=? AND serverid=?", (amount, id1, servID))
        cursor.execute("UPDATE userserver SET moneyAmount = moneyAmount + ? WHERE userid=? AND serverid=?", (amount, id2, servID))
        conn.commit()
        return(0)

    except mariadb.Error:
        print("Error with the command: one of the users didn't initialized his account")
        return(2)

def defineWorkChannel(cursor, conn, servID, chanID, amount): #Works perfectly
    try:
        cursor.execute("REPLACE INTO work (serverID, channelID, amount) VALUES (?, ?, ?)",(servID, chanID, amount))
        conn.commit()
        return(0)
    except mariadb.Error as e:
        print(e)
        return(2)

def work(cursor, conn, servID, chanID, uID): #Works perfectly
    '''cursor, connection, servID, chanID, uID'''
    try:
        #retrieve the work parameter's:
        cursor.execute("SELECT channelID, amount FROM work WHERE serverID=?",(servID,))
        for (channelID, amount) in cursor:
            if int(channelID) != int(chanID): return 1 #failure signal
        cursor.execute("UPDATE userserver SET moneyAmount = moneyAmount + ? WHERE userid=? AND serverid=?", (amount, uID, servID))
        conn.commit()
        return 0 #success signal
    except mariadb.Error as e:
        print(e)
        return 2 #critical failure signal

def incrementInterractions(cursor, conn, servID, uID):
    try:
        cursor.execute("UPDATE userserver SET InterractionsAmount = 1 + InterractionsAmount WHERE ServerID=? AND UserID=?", (servID, uID))
        conn.commit()
        return(0)
    except mariadb.Error as e:
        print(e)
        return(2)

def newStock(cursor, conn, stockID, stockAlias):
    try:
        cursor.execute("INSERT INTO stocks (stockid, alias) VALUES (?, ?)", (stockID, stockAlias))
        conn.commit()
        return(0)
    except mariadb.Error as e:
        print(e)
        return(2)

def buyStock(cursor, conn, servID, uID, stockID, amount, stockAmount):
    try:
        '''
        cursor.execute('SELECT moneyAmount FROM userserver WHERE userid=? AND serverid=?', (uID, servID))
        for (i) in cursor:
            moneyAmount = i
            pass
        '''
        moneyAmount = getMoneyAmount1Account(cursor, conn, servID, uID)
        if moneyAmount[0][0] < (int(amount) * stockAmount): return(1) #not enough money
        cursor.execute('INSERT INTO userserverstock (userID, serverID, stockID, value) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE value = value + ?', (uID, servID, stockID, amount, amount))
        nA = moneyAmount[0][0] - (int(amount) * stockAmount)
        cursor.execute('UPDATE userserver SET moneyamount = ? WHERE serverid=? AND userID=?', (nA, servID, uID))
        conn.commit()
        return(0)
    except mariadb.Error as e:
        print(e)
        return(2)

def sellStock(cursor, conn, servID, uID, stockID, amount, stockAmount):
    try:
        cursor.execute('SELECT value FROM userserverstock WHERE userid=? AND serverid=? AND stockid=?', (uID, servID, stockID))
        for (i) in cursor:
            stockPossessed = i
            pass
        if stockPossessed[0] < int(amount): return(1) #not enough money
        moneyAmount = getMoneyAmount1Account(cursor, conn, servID, uID)
        cursor.execute('INSERT INTO userserverstock (userID, serverID, stockID, value) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE value = value - ?', (uID, servID, stockID, amount, amount))
        nA = moneyAmount[0][0] + (int(amount) * stockAmount)
        cursor.execute('UPDATE userserver SET moneyamount = ? WHERE serverid=? AND userID=?', (nA, servID, uID))
        conn.commit()
        return(0)
    except mariadb.Error as e:
        print(e)
        return(2)

def getStockWallet(cursor, conn, servID, uID):
    try:
        cursor.execute('SELECT stockID, value FROM userserverstock WHERE userid=? AND serverid=?', (uID, servID))
        outTable = [(sid, val) for (sid, val) in cursor]
        return(outTable)
    except mariadb.Error as e:
        print(e)
        return(2)

def getInteractionsClassment(cursor, conn, servID):
    try:
        cursor.execute('SELECT name, interractionsAmount FROM userserver WHERE serverID=? ORDER BY interractionsamount DESC', (servID,))
        outTable = [(name, inter) for (name, inter) in cursor]
        return(outTable)
    except mariadb.Error as e:
        print(e)
        return(2)

def getRoleList(cursor, conn, servID):
    try:
        cursor.execute('SELECT * FROM ServerRole WHERE ServerID=? ORDER BY cost', (servID,))
        rep = {}
        for roleID, servID, cost, costSell, alias in cursor:
            rep[alias] = (roleID, cost, costSell)
        return(rep)
    except mariadb.Error as e:
        print(e)
        return()

def insertRole(cursor, conn, roleID, servID, cost, costSell, alias):
    try:
        cursor.execute('INSERT INTO ServerRole (roleid, serverID, cost, costSell, alias) VALUES (?,?,?,?,?)', (roleID, servID, cost, costSell, alias))
        conn.commit()
        return(0)
    except mariadb.Error as e:
        print(e)
        return(2)

def changeMoneyAmount(cursor, conn, servID, uID, amount):
    try:
        cursor.execute('UPDATE userServer SET moneyAmount = moneyAmount+? WHERE serverID=? AND userID=?', (amount, servID, uID))
        conn.commit()
        return(0)
    except mariadb.Error as e:
        print(e)
        return(2)
# coding : utf-8


import discord
import os
from datetime import datetime

import dataCollection
import stockManipulation

######################
# Configuration File #
######################
this_file = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_file+'..'+os.sep+'..'+os.sep+'.')

#################
# DB Connection #
#################
cursor, connection = dataCollection.initializeDBConnection("notes.txt", 6)


#########################
# Parameters retrieving #
#########################
with open("notes.txt", 'r') as f:
    botToken = f.readlines()[3].strip('\n')


##################
# Discord Client #
##################
class MyClient(discord.Client):

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')


    async def on_message(self, message):
        #Security for no auto-reply
        if message.author.id == self.user.id:
            return

        ############
        # Commands #
        ############
        elif message.content.startswith('$'):
            #log the command
            with open('botCommands.log', 'a') as f: #open the file in 'append' mode
                f.write('{} : {} : {} : {}\n'.format( #write the following string
                    datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), #datetime of the message
                    message.guild.id, message.author.id, #serverID and author ID
                    message.content)) #content of the message

            if message.content.startswith('$initialize server'): #Works perfectly
                '''Initializing the server, just type "$initialize server"'''
                sig = dataCollection.createIfNotExisting(message.guild.id, message.guild.name, cursor, connection)
                if sig == 2: await message.channel.send("The server initialization didn't worked.") #command error
                elif sig == 1: await message.channel.send("The server had already been initialized.") #server already in DB
                elif sig == 0: await message.channel.send("Server initialized succesfully") #server added to the db

            elif message.content.startswith('$bankaccount create'): #Works perfectly
                '''create the bank account of a user, just type "$create bankaccount"'''
                sig = dataCollection.createBankAccount(cursor, connection, message.guild.id, message.author.id, message.author.name)
                if sig == 2: await message.channel.send("<@!{}> The bank account initialization didn't worked".format(message.author.id))
                elif sig == 1: await message.channel.send("<@!{}> The bank account already exist !".format(message.author.id))
                elif sig == 0: await message.channel.send("<@!{}> Bank account created successfully !".format(message.author.id))

            elif message.content.startswith('$list top10'): #Works but not done
                '''Show the top 10 richest peoples on the server'''
                accountList = dataCollection.getMoneyAmounts(cursor, connection, message.guild.id)
                msgStr = "Here are the top 10 accounts:"
                emote = [':first_place:',':second_place:',':third_place:',
                    ':white_circle:',':blue_circle:',':green_circle:',
                    ':yellow_circle:',':orange_circle:',':red_circle:',
                    ':brown_circle:']

                #######
                # fonction de tri décroissant
                #######
                
                for i in range(0, min(10, len(accountList))):
                    msgStr = "{}\n{} {} : {:.2f}$".format(msgStr, emote[i], accountList[i][1], accountList[i][2])

                embed=discord.Embed(color=0x7aff9c)
                embed.add_field(name="TOP 10 Richest Users", value=msgStr, inline=False)
                await message.channel.send(embed=embed)

            elif message.content.startswith('$settings work'): #Works perfectly
                '''Setup the work channel, use like this: "$settings work [tag channel] [montant] [cooldown]'''
                args = message.content[15:].split(sep=' ')
                sig = dataCollection.defineWorkChannel(cursor, connection, message.guild.id, args[0][2:20], args[1])
                if sig == 0: await message.channel.send("Work channel setted up perfectly !")
                elif sig == 2: await message.channel.send("The work channel setup didn't worked...")

            elif message.content.startswith('$work'): #Works perfectly
                sig = dataCollection.work(cursor, connection, message.guild.id, message.channel.id, message.author.id)
                if sig == 0: await message.channel.send("<@!{}> Thank you for your work !".format(message.author.id))
                elif sig == 1: await message.channel.send("<@!{}> Wrong channel !".format(message.author.id))
                elif sig == 2: await message.channel.send("<@!{}> There is a critical failure in the bot. Please, report this.".format(message.author.id))

            elif message.content.startswith('$bankaccount transfer'): #seems to work
                args = message.content[16:].split(sep=' ')
                args[0] = args[0][3:21]
                sig = dataCollection.moneyTransfer(cursor, connection, message.guild.id, message.author.id, args[0], args[1])
                if sig == 0: await message.channel.send("<@!{}> Transfer successfull".format(message.author.id))
                elif sig == 1: await message.channel.send("<@!{}> You need to have the money you want to transfer".format(message.author.id))
                elif sig == 2: await message.channel.send("<@!{}> Both of the users need to have an open bank account".format(message.author.id))

            elif message.content.startswith('$bankaccount consult'):
                sold = dataCollection.getMoneyAmount1Account(cursor, connection, message.guild.id, message.author.id)
                await message.channel.send("Your bank account is currently {}$ <@!{}> !".format(sold[0][0], message.author.id))

            elif message.content.startswith('$stock create'):
                args = message.content[14:].split(sep=' ')
                sig = dataCollection.newStock(cursor, connection, args[0], args[1])
                if sig == 0: await message.channel.send("Stock created successfully")
                elif sig == 2: await message.channel.send("Stock creation didn't worked")

            elif message.content.startswith('$stock graph'):
                args = message.content[13:].split(sep=' ')
                stockManipulation.graph1Day(args[0])
                stockManipulation.graph1Month(args[0])
                stockManipulation.graph6Month(args[0])
                await message.channel.send(file=discord.File('images/graph1D.png'))
                await message.channel.send(file=discord.File('images/graph1M.png'))
                await message.channel.send(file=discord.File('images/graph6M.png'))

            elif message.content.startswith('$stock list'):
                msg=''
                cursor.execute('SELECT * FROM stocks')
                for (stockID, alias) in cursor:
                    print(stockID, alias)
                    price = stockManipulation.lastValue(stockID)['close']
                    msg = "{}{} :arrow_forward: {:.5f} :arrow_forward: {}\n".format(msg, stockID, price, alias)
                embed=discord.Embed(color=0x7aff9c)
                embed.add_field(name="List of the stocks advailable", value=msg)
                await message.channel.send(embed=embed)

            elif message.content.startswith('$stock buy'):
                args = message.content[11:].split(sep=' ')
                stockAmount = stockManipulation.lastValue(args[0])['close']
                sig = dataCollection.buyStock(cursor, connection, message.guild.id, message.author.id, args[0], args[1], stockAmount)
                if sig==0: await message.channel.send('Successful purchase: {}*{} for {}$'.format(args[1], args[0], stockAmount))
                elif sig==1: await message.channel.send('You don\'t have enough money')
                elif sig==2: await message.channel.send('The purchase didn\'t worked')
            
            elif message.content.startswith('$stock sell'):
                args = message.content[12:].split(sep=' ')
                stockAmount = stockManipulation.lastValue(args[0])['close']
                sig = dataCollection.sellStock(cursor, connection, message.guild.id, message.author.id, args[0], args[1], stockAmount)
                if sig==0: await message.channel.send('Successful sale: {}*{} for {}$'.format(args[1], args[0], stockAmount))
                elif sig==1: await message.channel.send('You don\'t have enough stock')
                elif sig==2: await message.channel.send('The sale didn\'t worked')

            elif message.content.startswith('$stock value'):
                args = message.content[13:].split(sep=' ')
                stockAmount = stockManipulation.lastValue(args[0])['close']
                await message.channel.send('This stock value is now {:.5f}$.'.format(stockAmount))

            elif message.content.startswith('$stock wallet'):
                stockTable = dataCollection.getStockWallet(cursor, connection, message.guild.id, message.author.id)
                msg = ''
                total = 0
                for (i, v) in stockTable:
                    if v != 0:
                        msg = '{}{} :arrow_forward: {}\n'.format(msg, i, v)
                        total += stockManipulation.lastValue(i)['close'] * int(v)
                msg = "{}Estimation of the assets values: {:.2f}$".format(msg, total)
                embed=discord.Embed(color=0x7aff9c)
                embed.add_field(name='{}\'s stock wallet'.format(message.author.name), value=msg)
                await message.channel.send(embed=embed)

        if message.content.startswith('$'):
            i = dataCollection.incrementInterractions(cursor, connection, message.guild.id, message.author.id)

##############
# Bot Launch #
##############
with open("..\\token.txt", 'r') as f:
    token = f.read().strip('\n')
discordBot = MyClient()
discordBot.run(token)

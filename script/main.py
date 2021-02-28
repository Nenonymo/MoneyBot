# coding : utf-8


import discord
import os
from datetime import datetime

import dataCollection

######################
# Configuration File #
######################
this_file = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_file+'..'+os.sep+'..'+os.sep+'.')

#################
# DB Connection #
#################
cursor, connection = dataCollection.initializeDBConnection("notes.txt", 6)



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
        
        elif message.content.startswith('$'):
            #log the command
            with open('botCommands.log', 'a') as f: #open the file in 'append' mode
                f.write('{} : {} : {} : {}\n'.format( #write the following string
                    datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), #datetime of the message
                    message.guild.id, message.author.id, #serverID and author ID
                    message.content)) #content of the message

            if message.content.startswith('$initialize server'):
                print(message.guild.name)
                sig = dataCollection.createIfNotExisting(message.guild.id, message.guild.name, cursor, connection)
                if sig == 2: await message.channel.send("The server initialization didn't worked.") #command error
                elif sig == 1: await message.channel.send("The server had already been initialized.") #server already in DB
                elif sig == 0: await message.channel.send("Server initialized succesfully") #server added to the db
            '''
            if message.content.startswith('$money transfer'):
                args = message.content[16:].split(sep=' ')
                args[0] = args[0][3:21]
            '''






discordBot = MyClient()
discordBot.run(botToken)

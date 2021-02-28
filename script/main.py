# coding : utf-8


import discord


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
        print(message.guild.id, message.channel.id, message.author.id)

discordBot = MyClient()
discordBot.run("ODE1Mjg4NzY0MjQ2MzkyODgz.YDqO1A.fDSJdlFMOmdPOlJ9s9ZAtqSHwkM")
    
import asyncio
import json
import os
import os.path
import random
from os import sep
from types import prepare_class

import discord
from discord import user
from discord.ext import commands
from discord.flags import alias_flag_value
from discord.utils import get
import tokenFile as tf

# variables for the client
prefix = "."
activity = discord.Activity(
    type=discord.ActivityType.watching, name="you guys play | .help")
client = commands.Bot(command_prefix=prefix,
                      help_command=None, case_insensitive=True, activity=activity, status=discord.Status.idle)  # defins the client with prefix, comand case insensitive
qList = []
userIdList = []
client.gameActive = False
queueLimiter = 10

# json handler for server validation


def jsonHandler(server, s2, fileName, item):
    with open(
            f"{server}{os.sep}{fileName}.json", "r+") as f:
        data = json.load(f)
        f.close()

    for i in data[f'{s2}']:
        return i[item]


# on ready print this in the console
@client.event
async def on_ready():
    print(f"------{client.user} is ready to go.------")


# anytime someone messages, print on console with their username
@client.event
async def on_message(message):
    print("(%s) %s(%s): %s" % (message.guild,
                               message.author, message.author.id, message.content))

    await client.process_commands(message)


# join the queue by typing [prefix]j or [prefix]join
@client.command(aliases=['j'])
async def join(ctx, name=None):
    botChID = jsonHandler(
        ctx.message.guild, ctx.message.guild, "serverData", "BotChannelID")
    userName = str(ctx.message.author)
    userID = ctx.message.author.id

    userinfo = f"{userName}¬{userID}"
    userIdMention = f"<@!{int(userID)}>"
    if ctx.channel.id == botChID:
        if client.gameActive == True and userIdMention in userIdList:
            embed = discord.Embed(color=0xff0000)
            embed.add_field(name="Error!",
                            value=f"You are already in a game.\nUse `.current` command to see your game.", inline=False)
            await ctx.send(ctx.author.mention, embed=embed)
            return

        if userIdMention in userIdList:
            embed = discord.Embed(color=0xff0000)
            embed.add_field(name="Error joining the queue!",
                            value=f"You are already in the queue.", inline=False)
            await ctx.send(ctx.author.mention, embed=embed)
            return

        if userIdMention not in userIdList and len(userIdList) < 10:
            qList.append(userName)
            userIdList.append(userIdMention)

            embed = discord.Embed(color=0x8c00ff)
            embed.add_field(name=f"Queue update!",
                            value=f"{userIdMention} entered the queue...\nQueue size: {len(userIdList)}/10", inline=False)
            embed.set_author(
                name="QBot", icon_url="https://i.imgur.com/Knl3ZJn.png")
            await ctx.send(embed=embed)

        if userIdMention not in userIdList and len(userIdList) == queueLimiter:
            embed = discord.Embed(color=0xff0000)
            embed.add_field(name="Error joining the queue!",
                            value=f"There is already a game going on. Try again after the game.\nUse `.current` command to see your game.", inline=False)
            await ctx.send(ctx.author.mention, embed=embed)
            return

        if len(qList) == queueLimiter:
            client.gameActive = True
            random.shuffle(userIdList)
            length = len(userIdList)
            half_index = length//2
            teamA = userIdList[:half_index]
            teamB = userIdList[half_index:]

            client.teamA = "\n".join(teamA)
            client.teamB = "\n".join(teamB)

            tagList = " ".join(userIdList)
            client.randomCap = random.choice(userIdList)

            embed = discord.Embed(title="GAME READY", color=0x8c00ff)
            embed.set_author(
                name="QBot", icon_url="https://i.imgur.com/Knl3ZJn.png")
            embed.add_field(
                name="Team A", value=f"{client.teamA}", inline=True)
            embed.add_field(
                name="Team B", value=f"{client.teamB}", inline=True)
            embed.add_field(name="Game Captain",
                            value=f"{client.randomCap}", inline=False)
            embed.set_footer(
                text=f"Good luck!")
            await ctx.send(tagList, embed=embed)


# randomize the teams made by typing [prefix]shuffle then either yes or no to confirm
@client.command()
async def shuffle(ctx):
    botChID = jsonHandler(
        ctx.message.guild, ctx.message.guild, "serverData", "BotChannelID")
    if ctx.channel.id == botChID and "admin" in [y.name.lower() for y in ctx.author.roles] or "mod" in [y.name.lower() for y in ctx.author.roles] or str(ctx.message.author) in qList and len(qList) == queueLimiter or ctx.author.id == 242402191267069963:
        await ctx.send('Are you sure you want to shuffle?')

        def reshuffle(m):
            return m.author == ctx.message.author

        try:
            this = await client.wait_for('message', check=reshuffle, timeout=40.0)
        except asyncio.TimeoutError:
            return await ctx.message.channel.send(f'Took too long to reply! Teams are locked.')

        if this.content.lower() == "yes" or this.content.lower() == "y":
            client.gameActive = True
            random.shuffle(userIdList)
            length = len(userIdList)
            half_index = length//2
            teamA = userIdList[:half_index]
            teamB = userIdList[half_index:]

            client.teamA = "\n".join(teamA)
            client.teamB = "\n".join(teamB)

            tagList = " ".join(userIdList)
            client.randomCap = random.choice(userIdList)

            embed = discord.Embed(title="GAME RESHUFFLED", color=0x8c00ff)
            embed.set_author(
                name="QBot", icon_url="https://i.imgur.com/Knl3ZJn.png")
            embed.add_field(
                name="Team A", value=f"{client.teamA}", inline=True)
            embed.add_field(
                name="Team B", value=f"{client.teamB}", inline=True)
            embed.add_field(name="Game Captain",
                            value=f"{client.randomCap}", inline=False)
            embed.set_footer(
                text=f"Good luck!")
            await ctx.send(tagList, embed=embed)
        else:
            await ctx.send(f'Reply with "yes" to shuffle. Start again.')

    else:
        embed = discord.Embed(color=0xff0000)
        embed.add_field(
            name="Error!", value="Queue not full yet or other error occured.\n`.help` for help.", inline=False)
        await ctx.send(embed=embed)


# confirm teams once ready by typing [prefix]confirmteams or [prefix]lockteams
@client.command(aliases=['confirmteams'])
async def lockTeams(ctx):
    server = ctx.message.guild
    gameNumber = 0
    botChID = jsonHandler(
        ctx.message.guild, ctx.message.guild, "serverData", "BotChannelID")

    if ctx.channel.id == botChID and "admin" in [y.name.lower() for y in ctx.author.roles] or "mod" in [y.name.lower() for y in ctx.author.roles] or str(ctx.message.author) in qList or ctx.author.id == 242402191267069963:
        if len(qList) == queueLimiter:
            if not os.path.isfile(f"{server}{os.sep}{server}.text"):
                with open(
                        f"{server}{os.sep}{server}.text", "w") as f:
                    f.write(str(0))
                    f.close()

            else:
                with open(
                        f"{server}{os.sep}{server}.text", "r") as f:
                    gameNumber = int(f.read(1))
                    print(type(gameNumber))

            gameNumber += 1
            with open(
                    f"{server}{os.sep}{server}.text", "w") as f:
                f.write(str(gameNumber))
                f.close()

            embed = discord.Embed(color=0x8c00ff)
            embed.add_field(name=f"Game confirmed! Game number #{gameNumber}",
                            value=f"Enjoy the game and another game can begin!", inline=False)
            embed.set_author(
                name="QBot", icon_url="https://i.imgur.com/Knl3ZJn.png")
            embed.set_footer(
                text=f"I think {random.choice(('TeamA', 'TeamB'))} will win...")
            await ctx.send(embed=embed)
            qList.clear()
            userIdList.clear()
            client.gameActive = False
        else:
            embed = discord.Embed(color=0xff0000)
            embed.add_field(
                name="Error!", value="Queue is not full yet. \n`.help` for help.", inline=False)
            await ctx.send(embed=embed)


# restart the queue, only admins or authorized people can do this
@client.command()
async def restartQ(ctx):
    botChID = jsonHandler(
        ctx.message.guild, ctx.message.guild, "serverData", "BotChannelID")

    if ctx.channel.id == botChID and "admin" in [y.name.lower() for y in ctx.author.roles] or "mod" in [y.name.lower() for y in ctx.author.roles] or str(ctx.message.author) in qList and len(qList) == queueLimiter or ctx.author.id == 242402191267069963:
        await ctx.send('Are you sure you want to restart the queue?')

        def reshuffle(m):
            return m.author == ctx.message.author

        try:
            this = await client.wait_for('message', check=reshuffle, timeout=40.0)
        except asyncio.TimeoutError:
            return await ctx.message.channel.send(f'Took too long to reply!. Try again.')

        if this.content.lower() == "yes" or this.content.lower() == "y":
            embed = discord.Embed(color=0x8c00ff)
            embed.add_field(name=f"Q restarted!",
                            value=f"You can now requeue!", inline=False)
            embed.set_author(
                name="QBot", icon_url="https://i.imgur.com/Knl3ZJn.png")
            embed.set_footer(
                text=f"You can queue now.")
            await ctx.send(embed=embed)
            qList.clear()
            userIdList.clear()
        if this.content.lower() == "no" or this.content.lower() == "n":
            embed = discord.Embed(color=0x8c00ff)
            embed.add_field(name=f"Q not restarted!",
                            value=f"Same queue active still.", inline=False)
            embed.set_author(
                name="QBot", icon_url="https://i.imgur.com/Knl3ZJn.png")
            await ctx.send(embed=embed)
            qList.clear()
            userIdList.clear()
    else:
        embed = discord.Embed(color=0xff0000)
        embed.add_field(
            name="Error!", value="Queue is not full yet or other error occured. `.help` for help.", inline=False)
        await ctx.send(embed=embed)


# check the current queue
@ client.command(aliases=['queue'])
async def q(ctx):
    botChID = jsonHandler(
        ctx.message.guild, ctx.message.guild, "serverData", "BotChannelID")
    if ctx.channel.id == botChID and client.gameActive == False:
        listForEmbed = "\n".join(userIdList)
        embed = discord.Embed(title="Waiting for game...", color=0x8c00ff)
        embed.set_author(
            name="QBot", icon_url="https://i.imgur.com/Knl3ZJn.png")
        embed.add_field(name="Current queue",
                        value=f"{listForEmbed}\n{len(userIdList)}/10", inline=False)
        embed.set_footer(
            text=f"{random.choice(('Rahman is better than Mike.', 'Mike is better than Rahman', 'Both Mike and Rahman are bots', 'Can Clyde finally win a cup or no?', 'Is dubbeh actually not baiting?', 'So what bring you back to Warface?', 'Whosteria or noobsteria?', 'Can mike only play rifle in post?', 'Which somali is in that smoke?', 'Who is the 1-trick?'))}")
        await ctx.send(embed=embed)
    if client.gameActive == True:
        embed = discord.Embed(color=0xff0000)
        embed.add_field(name="There is already is game!",
                        value=f"There is already a game going on.\nUse `.current` command to see the game.", inline=False)
        await ctx.send(ctx.author.mention, embed=embed)


# leave the queue
@client.command(aliases=['l'])
async def leave(ctx):
    botChID = jsonHandler(
        ctx.message.guild, ctx.message.guild, "serverData", "BotChannelID")
    userName = str(ctx.message.author)
    userID = ctx.message.author.id

    userinfo = f"{userName}¬{userID}"
    userIdMention = f"<@!{int(userID)}>"
    if ctx.channel.id == botChID and client.gameActive == False:
        if userIdMention in userIdList and userName in qList:
            userIdList.remove(userIdMention)
            qList.remove(userName)

            embed = discord.Embed(color=0x00ff2a)
            embed.add_field(name="Success!",
                            value=f"You have left the queue!", inline=False)
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(color=0xff0000)
            embed.add_field(name="Error!",
                            value=f"You are not in the queue yet! `.join` - to join the queue", inline=False)
            embed.add_field(name="Help",
                            value=f"`.help` to access help", inline=False)
            await ctx.send(ctx.author.mention, embed=embed)
    else:
        embed = discord.Embed(color=0xff0000)
        embed.add_field(name="Error!",
                        value=f"You are in a game and cannot leave right now!", inline=False)
        embed.add_field(name="Help",
                        value=f"`.help` to access help", inline=False)
        await ctx.send(ctx.author.mention, embed=embed)


# check the current game
@ client.command(aliases=['current'])
async def currentmatch(ctx):
    botChID = jsonHandler(
        ctx.message.guild, ctx.message.guild, "serverData", "BotChannelID")

    if ctx.channel.id == botChID and len(qList) == queueLimiter:
        embed = discord.Embed(title="Current match", color=0x8c00ff)
        embed.set_author(
            name="QBot", icon_url="https://i.imgur.com/Knl3ZJn.png")
        embed.add_field(name="Team A", value=f"{client.teamA}", inline=True)
        embed.add_field(name="Team B", value=f"{client.teamB}", inline=True)
        embed.add_field(name="Game Captain",
                        value=f"{client.randomCap}", inline=False)
        embed.set_footer(
            text=f"I think {random.choice(('TeamA', 'TeamB'))} will win...")
        await ctx.send(ctx.author.mention, embed=embed)

    else:
        embed = discord.Embed(color=0xff0000)
        embed.add_field(name="Error!",
                        value=f"No game active. `.join` to join the queue!", inline=False)
        embed.add_field(name="Help",
                        value=f"`.help` to access help", inline=False)
        await ctx.send(ctx.author.mention, embed=embed)


# set a bot channel where the bot will type
@ client.command()
async def botChannel(ctx, botCh: discord.TextChannel = None):
    if not botCh:
        embed = discord.Embed(color=0xff0000)
        embed.add_field(
            name="Error!", value="Channel name doesn't exist. `.botChannel [BotChannel]` `.help` for help.", inline=False)
        await ctx.send(embed=embed)

    else:
        data = {}
        data[f'{ctx.message.guild}'] = []
        data[f'{ctx.message.guild}'].append({
            'BotChannelID': botCh.id,
        })

        server = ctx.message.guild

        path = "O:{os.sep}Coding{os.sep}Python\Projects{os.sep}Discord{os.sep}QBot"
        jPath = os.path.join(path, f"{server}")

        if not os.path.exists(jPath):
            os.makedirs(jPath)

        with open(f"{path}{os.sep}{server}{os.sep}serverData.json", "w+") as f:
            json.dump(data, f)
            f.close()

        embed = discord.Embed(color=0x008000)
        embed.add_field(
            name="Successful!", value=f"Bot channel set! <#{botCh.id}>", inline=False)
        await ctx.send(embed=embed)


# help command
@client.command()
async def help(ctx):
    botChID = jsonHandler(
        ctx.message.guild, ctx.message.guild, "serverData", "BotChannelID")

    if ctx.channel.id == botChID:
        embed = discord.Embed(title="QBot Help Command",
                              description="You can find all the commands here which are available to a normal player.", color=0xeeff00)
        embed.set_author(
            name="QBot", icon_url="https://i.imgur.com/Knl3ZJn.png")
        embed.add_field(name="To join the queue",
                        value="`.join` or `.j`", inline=True)
        embed.add_field(name="To leave the queue",
                        value="`.leave` or `.l`", inline=True)
        embed.add_field(name="Shows the players in the queue",
                        value="`.q`", inline=False)
        embed.add_field(name="Locks the team and frees the queue for another game to begin",
                        value="`.lockTeams` or `.confirmteams`", inline=False)
        embed.add_field(name="Shuffles the queue, it is restricted to mods/admins or players in the current queue. You will need to follow up with a confirmation yes or no the complete the commmand",
                        value="`.shuffle` -> `yes` or `no`", inline=False)
        embed.add_field(name="Check the the match in progress",
                        value="`.current` or `.currentmatch`", inline=False)
        embed.add_field(name="Restart the queue if someone leaves or isn't able to play",
                        value="`.restartq` -> `yes` or `no`", inline=False)
        embed.set_footer(
            text=f"Made by exel :)")
        await ctx.send(embed=embed)

# run the client using the token from tf file
client.run(tf.TOKEN)

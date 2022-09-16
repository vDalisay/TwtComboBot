# This example requires the 'message_content' intent.

from datetime import timedelta
from types import NoneType
from unicodedata import name
import discord
import re
from discord.utils import get
from dotenv import load_dotenv
import os
from discord import app_commands
from discord.ext import commands
load_dotenv(".env")
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

highScore = {}
parrotId = '<a:posting_parrot:1018558586495971439>'
kwakId = '<:kwak:977331125213081600>'
twtBaseURL = 'https://timewilltell.forumotion.com/'
topicURL = ''


twtTagBoxChannelId = 974039783095537714
LTgeneralchannelId = 899629505067511831
LTddchannelId = 1018550654639292576
botChannelId = 982355182367174736
generalId = 969308979270402158
plotTalkId = 969306319309930617
gmHubId = 973980526744571904

channelId = twtTagBoxChannelId
userChannels = [ LTgeneralchannelId, botChannelId, twtTagBoxChannelId]
adminChannels = [LTddchannelId, LTgeneralchannelId, gmHubId ]

filteredMsgs = []
lastMessage = None
historyMsgList = []
topicMsgs = []

emojiList = {
             1: "<:1_:1018865741862281316>", 
             2: "<:2_:1018865743074435213>", 
             3: "<:3_:1018865744815075339>", 
             4: "<:4_:1018865746211786782>", 
             5: "<:5_:1018865747432316998>", 
             6: "<:6_:1018865748573179906>", 
             7: "<:7_:1018865750615793754>", 
             8: "<:8_:1018865754336145468>", 
             9: "<:9_:1018865755883843624>", 
             10: "<:10:1018865757515419688>",
             11: "<:11:1018865759939735573>", 
             12: "<:12:1018865761290289213>",
             13: "<:13:1018865762556985384>", 
             14: "<:14:1018865764045955112>", 
             15: "<:15:1018865765010657353>", 
             16: "<:16:1018865767107805224>", 
             17: "<:17:1018865768630337547>", 
             18: "<:18:1018865770429693952>", 
             19: "<:19:1018865771516018768>", 
             20: "<:20:1018865772715581490>",
             21: "<:21:1018894853788139620>", 
             22: "<:22:1018894855038042112>",
             23: "<:23:1018894856396996730>", 
             24: "<:24:1018894857709822093>", 
             25: "<:25:1018894859307859968>", 
             26: "<:26:1018894860633256028>", 
             27: "<:27:1018894861816053873>", 
             28: "<:28:1018894864122904607>", 
             29: "<:29:1018894865582522388>", 
             30: "<:30:1018894866937286716>",
             }
#HIGHSCORE
async def addToHighScore(topic, streakScore):
    if streakScore < 2:
        return

    if topic in highScore:
        highScore.update({topic : streakScore})
    else:
        highScore[topic] = streakScore
    #Cleanup, remove lowest of the 6 and make a top 5
    if(len(highScore) > 5):
        sortedHS = sorted(highScore.items(), key=lambda item: item[1], reverse=True)
        key = sortedHS[-1]
        highScore.pop(key[0])

async def wipe():
    highScore.clear()

async def remove(msg):
    topic = msg.content.split('=')[1]
    del highScore[topic]

async def switchChannel(msg, _channelId):
    if(msg.channel.id == twtTagBoxChannelId):
        _channelId = LTgeneralchannelId
    else:
        _channelId = twtTagBoxChannelId

    await msg.reply(f"Channel switched to {channelId}!")
    return

async def info(ctx):
    embed=discord.Embed(title="Info Log", description="This info is meant for the developer aka @Draak", color=0xFF5733)
    embed.add_field(name=f'**Channel**', value=f'> channelID: {channelId}',inline=False)
    await ctx.send(embed=embed)

    
async def embed(ctx):
    embed=discord.Embed(title="Top 5 TimeWillTell Combo Scores", description="Who has retained the favor of the dragon the longest?", color=0xFF5733)
    sortedHS = sorted(highScore.items(), key=lambda item: item[1], reverse=True)
    for key, value in sortedHS:
        topicName = await trimTopicForHS(key)
        embed.add_field(name=f'**Score: {value}** - {topicName}', value=f'> Read here: {key}',inline=False)
    await ctx.send(embed=embed)

async def trimTopicForHS(topic):
    withoutNum = topic.split('#')[0]
    topicName = withoutNum.split('/')[-1]
    return topicName
    
#REACTIONS
async def getTopicUrl(sentence):
    for word in sentence.split():
        if twtBaseURL in word:
            print("topicURL:" + word)
            trimmedUrl = word.split('#')[0]

            print("trimmedURL:" + trimmedUrl)
            return trimmedUrl 

async def filterMessages(pastMessages, topic):
    for pastMsg in pastMessages:
        for word in pastMsg.content.split(' '):
            if twtBaseURL in word:
                urlWithoutPost = word.split('#')[0]
                fullTopic = urlWithoutPost.split('/')[-1]
                topicNameAndPage = fullTopic.split('-')[0]
                topicNum = topicNameAndPage.split('p')[0]
                if topicNum in topic:
                    filteredMsgs.append(pastMsg)

    print('<2H FilteredMsgs:' + str(len(filteredMsgs)))
    return filteredMsgs

async def addReactions(topicMsgs):
    streakCount = len(topicMsgs)
    if(streakCount < 2): 
        return
    
    await filteredMsgs[0].add_reaction(kwakId)

    await filteredMsgs[0].add_reaction(emojiList[streakCount])

    await filteredMsgs[0].add_reaction(parrotId)
    
def reset():
    topicURL = ''
    filteredMsgs.clear()
    historyMsgList.clear()
    lastMessage = None

async def getMsgHistory(msgTime):
    history = [ms async for ms in client.get_channel(channelId).history(after=(msgTime - timedelta(hours=2)), limit = 400)]
    for msg in history:
        historyMsgList.append(msg) 
    historyMsgList.reverse()
    return historyMsgList

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user: return    
    if message.channel.id in userChannels:
        if(message.content.startswith('!score')):
            await embed(message.channel)
    elif(message.channel.id in adminChannels):
        if(message.content.startswith('!reset')):
            await wipe()
            await message.reply(f"Highscores reset!")
        if(message.content.startswith('!remove')):
            await remove(message)
            await message.reply(f"Score removed!")
        if(message.content.startswith("!info")):
            await info(message.channel)

    if message.channel.id != channelId: 
        return
    
    reset()

    print('<--------------------START-------------------->')
    topicURL = await getTopicUrl(message.content)

    if type(topicURL) is not str: 
        print('topicUrl not found: ' + str(topicURL))
        return

    filteredMsgs = await getMsgHistory(message.created_at)

    topicMsgs = await filterMessages(filteredMsgs, topicURL)

    await addReactions(topicMsgs)
    await addToHighScore(topicURL, len(topicMsgs))

    print('(Mine) LatestMsg: ' + filteredMsgs[0].content)
    if(len(filteredMsgs) > 1):
        print('PreviousMsg: ' + filteredMsgs[1].content)

    #topic combo high score list command
    print('<---------------------END--------------------->')
    reset()

    return

client.run(TOKEN)

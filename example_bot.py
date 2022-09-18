# This example requires the 'message_content' intent.

from datetime import timedelta
from unicodedata import name
import discord
import re
from discord.utils import get
from dotenv import load_dotenv
import os
from discord.ext import commands
import socket 

load_dotenv(".env")
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
#intents.message_content = True

client = discord.Client(intents=intents)

highScore = {}
parrotId = '<a:posting_parrot:1018558586495971439>'
kwakId = '<:kwak:977331125213081600>'
twtBaseURL = 'https://timewilltell.forumotion.com/'
topicURL = ''


LTgeneralchannelId = 899629505067511831
LTddchannelId = 1018550654639292576

twtTagBoxChannelId = 974039783095537714
botChannelId = 982355182367174736
generalId = 969308979270402158
plotTalkId = 969306319309930617
gmHubId = 973980526744571904
announcementId = 969308725531783218

async def getChannel():
    if("VincentY740" in socket.gethostname()):
        print("Listening on LTGeneral")
        return LTgeneralchannelId
    else:
        print("Listening on TwTTagBoxChannel")
        return twtTagBoxChannelId
        
channelId = 0
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

reverseEmojiList = {
             1018865741862281316: 1, 
             1018865743074435213: 2, 
             1018865744815075339: 3, 
             1018865746211786782: 4, 
             1018865747432316998: 5, 
             1018865748573179906: 6, 
             1018865750615793754: 7, 
             1018865754336145468: 8, 
             1018865755883843624: 9, 
             1018865757515419688: 10,
             1018865759939735573: 11, 
             1018865761290289213: 12,
             1018865762556985384: 13, 
             1018865764045955112: 14, 
             1018865765010657353: 15, 
             1018865767107805224: 16, 
             1018865768630337547: 17, 
             1018865770429693952: 18, 
             1018865771516018768: 19, 
             1018865772715581490: 20,
             1018894853788139620: 21, 
             1018894855038042112: 22,
             1018894856396996730: 23, 
             1018894857709822093: 24, 
             1018894859307859968: 25, 
             1018894860633256028: 26, 
             1018894861816053873: 27, 
             1018894864122904607: 28, 
             1018894865582522388: 29, 
             1018894866937286716: 30,
             }

announcementTriggers = {}
            
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

async def info(ctx):
    embed=discord.Embed(title="Info Log", description="This info is meant for the developer aka @Draak", color=0xFF5733)
    embed.add_field(name=f'**Channel**', value=f'> channelID: {channelId}',inline=False)
    embed.add_field(name=f'**Host**', value=f'> name: {socket.gethostname}',inline=False)
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

async def setAnnouncement(_title, _description, _color=0x00FF00, _thumbnail='', trigger='', winner=''):
    embed=discord.Embed(title=_title, description=_description, color=_color, thumbnail=_thumbnail)
    embed.set_author(name=f"{winner}")
    announcementTriggers[int(trigger)] = embed

async def checkAnnouncementTriggers(newScore, author):
    if(len(announcementTriggers) == 0):
        return
    if(announcementTriggers.get(newScore) is not None):
        embed = announcementTriggers.get(newScore)
        
        if(embed.author.name is ''):
            embed.remove_author()
        else:
            embed.set_author(name=f"{author.name} triggered an event!", icon_url=author.avatar_url)  

        channel = client.get_channel(LTddchannelId)
        await channel.send(embed=embed)
        announcementTriggers.pop(newScore)
    
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

    #Seting new combo
    if(len(topicMsgs) == 2):
        newScore = 2
    else:
        newScore = await getCurrentComboCount(topicMsgs[1]) + 1

    await filteredMsgs[0].add_reaction(kwakId)

    await filteredMsgs[0].add_reaction(emojiList[newScore])

    await filteredMsgs[0].add_reaction(parrotId)

    return newScore
    
async def getCurrentComboCount(lastStreakMsg):
    for reaction in lastStreakMsg.reactions:
        if(hasattr(reaction.emoji,'id')):
            if reverseEmojiList.get(reaction.emoji.id) is not None:
                return reverseEmojiList.get(reaction.emoji.id)

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
    global channelId 
    channelId = await getChannel()

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
        if(message.content.startswith("!setAnnouncement")):
            if(len(message.content.split('=')) < 2):
                await message.reply("Format is: !setAnnouncement =<title> =<description> =<color(optional)> =<thumbnail(optional)> =<trigger(optional)> =<winner(optional)>")
            else:
                content = message.content.split('=')
                params = []
                for x in range(1,7):
                    try:
                        params.append(content[x])
                    except IndexError:
                        params.append(None)

                await setAnnouncement(params[0], params[1], 0xFF5733, params[3], params[4], params[5])
                await message.reply("Announcement set with following info:" + str(params))
                print(params)

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

    if(len(topicMsgs) < 2): #means its not a streak
        reset()
        print('New first topic posted!')
        return

    score = await addReactions(topicMsgs)
    
    await checkAnnouncementTriggers(score, topicMsgs[0].author)
    
    await addToHighScore(topicURL, score)

    print('(Mine) LatestMsg: ' + filteredMsgs[0].content)
    if(len(filteredMsgs) > 1):
        print('PreviousMsg: ' + filteredMsgs[1].content)

    #topic combo high score list command
    print('<---------------------END--------------------->')
    reset()

    return

client.run(TOKEN)

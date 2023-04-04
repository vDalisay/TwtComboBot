# This example requires the 'message_content' intent.

from datetime import timedelta
from unicodedata import name
import discord
import re
from discord.utils import get
import os
from dotenv import load_dotenv
from discord.ext import commands
import socket 

load_dotenv(".env")
TOKEN = "MTAxNzc1MDUyMjMwMTc5NjQ1NA.GaU9Ng.XhmgLPMli-QQR_rm4o5s0FwAF35596JGU50DhM"
intents = discord.Intents.all()

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
twtAnnouncementId = 969308725531783218

async def getChannel():
    if("Vincent-Desktop" in socket.gethostname()):
        print("Listening on LTGeneral")
        return LTgeneralchannelId
    else:
        print("Listening on TwTTagBoxChannel")
        return twtTagBoxChannelId

async def getBotAnnouncementChannel():
    if("Vincent-Desktop" in socket.gethostname()):
        print("Announcement channel: LTddchannelId")
        return LTddchannelId
    else:
        print("Announcement channel: plotTalkId")
        return plotTalkId

channelId = 0
botAnnouncementsId = 0
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

async def setAnnouncement(message):
    rgb = eval(announcementContent["twtColor"])
    twtColor = discord.Colour.from_rgb(rgb[0], rgb[1], rgb[2])
    embed=discord.Embed(title=announcementContent["twtTitle"], description=announcementContent["twtDescription"], colour=twtColor )
    embed.set_thumbnail(url=announcementContent["twtThumbnail"])
    embed.set_author(name=announcementContent["twtWinner"])

    announcementTriggers[int(announcementContent["twtTrigger"])] = embed
    
    await message.reply("Sending a preview of the announcement:")
    await message.channel.send(embed=embed)

async def checkAnnouncementTriggers(newScore, author):
    if(len(announcementTriggers) == 0):
        return
    if(announcementTriggers.get(newScore) != None):
        embed = announcementTriggers.get(newScore)
        
        if(embed.author.name != ""):
            embed.set_author(name=f"{author.name} triggered an event!", icon_url=author.avatar_url)  

        channel = client.get_channel(botAnnouncementsId)
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

#COMMAND HANDLING
async def handleUserCommands(message):
    if(message.content.startswith('!score')):
        await embed(message.channel)

async def handleAdminCommands(message):
    if(message.content.startswith('!reset')):
        await wipe()
        await message.reply(f"Highscores reset!")
    if(message.content.startswith('!remove')):
        await remove(message)
        await message.reply(f"Score removed!")
    if(message.content.startswith("!info")):
        await info(message.channel)
    if(message.content.startswith("!setAnnouncement")):
        await handleSetAnnouncement(message)

#Help Command (REVAMP LATER)
async def handleHelpCommand(message):
    embed=discord.Embed(title="Set Announcement Help", description="Start a command with !setAnnouncement and follow up with any of the below content options that you want to fill.\n The required content options are: \n - _twtTitle_ \n - _twtDescription_ \n - _twtTrigger_ \n To use these, look at the example below. Other content options that you want to fill can be added as you wish or be left out. \n", color=0xFF5733)
    embed.add_field(name=f'**Example command:**', value=f'!setAnnouncement \n ^twtTitle \n _This is a test title_ \n ^twtDescription \n _Here you can describe what your announcement or trigger is all about!_ \n ^twtTrigger \n _15_ \n ',inline=False)
    embed.add_field(name='**---------------**', value='\nㅤ', inline=False)
    embed.add_field(name=f'**^twtTitle**', value=f'Displays the given input as the title for the announcement. \n --- \n **Example:** \n _^twtTitle_ \n This example title roars loudly!',inline=True)
    embed.add_field(name=f'**^twtDescription**', value=f'Displays the given input as the description for the announcement. \n Formatting supports anything discord can do so **bold** text can be achieved by surrounding words with double "*" etc.\n --- \n **Example:** \n _^twtDescription_ \n The roar from the _example title_ is heard all throughout the realm. \n \n The people of Odiria are even fleeing below the top section of this example description!',inline=True)
    embed.add_field(name=f'**^twtTrigger**', value=f'Given a number as input, the trigger will correspond to the streak count needed in order for the announcement to be placed. \n The first time a streak has been achieved that matches your trigger count will prompt the bot to post the announcement. \n Multiple triggers at the same time can be set in advance! \n (e.g. one at 15, one at 20 and one at 30 but do not set two of them at the same streak count or set a count above the current max count of 30, no idea what happens then tbh)\n --- \n **Example:** \n _^twtTrigger_ \n 21 ',inline=False)
    embed.add_field(name='**---------------**', value='\nㅤ', inline=False)
    embed.add_field(name=f'**^twtColor** (optional)', value=f'Given an RGB input, this will change the sidecolor of the announcement. \n Use it by providing the individual RGB values of a color, just like you would in CSS. \n --- \n **Example:** \n _^twtColor_ \n 255,199,72',inline=True)
    embed.add_field(name=f'**^twtThumbnail** (optional)', value=f'Given an URL that starts with http(s), it will display an extra image inside of the announcement. Only web links are allowed, local images are not supported. \n --- \n **Example:** \n _^twtThumbnail_ \n https://awoiaf.westeros.org/images/thumb/d/d4/Aegon_on_Balerion.jpg/1200px-Aegon_on_Balerion.jpg',inline=True)
    embed.add_field(name=f'**^twtWinner** (optional)', value=f'If you want to show the person that has triggered the announcement/event inside of the announcement, you can use this option. \n Using this option will add the name and avatar of the person inside of the announcement with the following format text: _(Insert person name) triggered an event!_ \n --- \n **Example:** \n _^twtWinner_ \n Yes \n _(You can put any text here to opt in, even putting in "No" will opt you in, its more about text being present here)_',inline=True)
    embed.add_field(name='**---------------**', value='\nㅤ', inline=False)
    embed.add_field(name=f'**Quick Copy Paste**', value=f'!setAnnouncement \n ^twtTitle \n ^twtDescription \n ^twtTrigger \n ^twtColor \n ^twtThumbnail \n ^twtWinner',inline=True)
    
    await message.channel.send(embed=embed)

#Announcement Command
async def handleSetAnnouncement(message):
    if(len(message.content.split('^')) < 2):
        await handleHelpCommand(message)
        return
    await getAnnouncementContents(message)
    await setAnnouncement(message)
    global announcementContent
    announcementContent = {
    "twtTitle": "",
    "twtDescription": "",
    "twtColor": 0,
    "twtTrigger": 0,
    "twtThumbnail": "",
    "twtWinner": ""
    }

announcementContent = {
    "twtTitle": "",
    "twtDescription": "",
    "twtColor": 0,
    "twtTrigger": 0,
    "twtThumbnail": "",
    "twtWinner": ""
}

async def getAnnouncementContents(commandMsg):
    snippets =  commandMsg.content.split("^")
    annoucementKeys = announcementContent.copy()

    print("--Announcement Content Start--")
    for twtParam in annoucementKeys.keys():
        for piece in snippets:
            if piece.startswith(twtParam):
                if(twtParam != "twtDescription"):
                    key = piece.replace("\n", " ").split(' ')[0]
                else:
                    key = piece.split(' ')[0]
                
                value = piece.split(twtParam)[1:]
                value = [s for s in value if not value == '']
                announcementContent[key] = value[0]
                
                break
    print("--Announcement Content End--")

#EVENTS
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    global channelId, botAnnouncementsId 
    channelId = await getChannel()
    botAnnouncementsId = await getBotAnnouncementChannel()

@client.event
async def on_message(message):
    if message.author == client.user: return    
    if message.channel.id in userChannels:
        await handleUserCommands(message)
    elif(message.channel.id in adminChannels):
        await handleAdminCommands(message)

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

#Author: Siam Shafiq, siam.shafiq@gmail.com
#This is a discord bot experimental project written in python.
#The functionality is limited to checking Win/Lose rates and posting them to the discord channel.
#This bot also tracked the most frequent times that you would find someone online on discord.

import os
import random
import requests
import json
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import tasks
from discord.ext.commands import Bot
from discord import Member


import datetime

load_dotenv()
#An env file contained the discord token required.
token = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    channel = client.get_channel(609449706573135903)

#Greeting message if a new user joined the server
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the server!'
    )

#These are the events that will trigger certain things to occur
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #This was to test if the bot was listening
    elif message.content == '/word' or message.content == "/Word":
        response = "Loud and clear :)"
        await message.channel.send(response)

    #This block checks the saved data, calculate the most frequented times for each person and post the times.
    elif message.content == '/playerdata' or message.content == '/Playerdata':
        all_player_data = await calculate_frequent_times()
        final_response = ""
        for x in all_player_data:
            final_response = final_response + x + "\n"
        await message.channel.send(final_response)
    
    #This block would fetch Dota 2 Win/Loss rates using the OpenDota Api and display their information/
    elif message.content[0:7] =='/stats/':
        profile_id = message.content[7:len(message.content)]
        print(profile_id)
        
        final_string = ""

        #All of the following is just formatted text for the user to see.
        r = requests.get('https://api.opendota.com/api/players/' + profile_id)
        response = json.loads(r.text)
        print("Account: " + response['profile']['personaname'])
        final_string = final_string + "Account: " + response['profile']['personaname'] + "\n"
        print("MMR Estimate: " + str(response['mmr_estimate']['estimate']))
        final_string = final_string + "MMR Estimate: " + str(response['mmr_estimate']['estimate']) + "\n"

        r = requests.get('https://api.opendota.com/api/players/' + profile_id + '/wl')
        todos = json.loads(r.text)
        print("Wins: " + str(todos['win']))
        final_string = final_string + "Wins: " + str(todos['win']) + "\n"
        print("Loses: " + str(todos['lose']))
        final_string = final_string + "Loses: " + str(todos['lose']) + "\n"

        win_rate = (todos['win']/(todos['win'] + todos['lose'])) * 100
        win_rate = round(win_rate,2)
        print("Win Rate: " + str(win_rate) + "%")
        final_string = final_string + "Win Rate: " + str(win_rate) + "%" + "\n"

        await message.channel.send(final_string)

#Fetches the members that are online on discord but not on the voice channel and logs the time.
async def get_members():
    await client.wait_until_ready()
    now = datetime.datetime.now()
    hournotation = "00"
    print ("%d:%s" % (now.hour,hournotation)) 

    while True:
        for guild in client.guilds:
            for member in guild.members:
                path = "G:\\Programming\\python\\discord_bot\\%s.txt" % member.id
                f = open(path, "a")
                
                x = member 
                y = str(member.status)

                status = "online"
                print(member.status)

                if y == status:
                    f.write("%d\n" % now.hour)
                    print("Printed!")
                f.close()

        channel = client.get_channel(609449706573135903)
        await asyncio.sleep(1800)

#Fetches the members currently on the voice channel and logs the times that they are online
async def get_members_voice():

    await client.wait_until_ready()
    hournotation = "00"

    voicechannels = [611021813551726593,632042204948463617,609449706573135905]
    
    while True:
        now = datetime.datetime.now()
        for channels in voicechannels:
            VoiceChannel = client.get_channel(channels)
            member_voice = VoiceChannel.members
            for member in member_voice:
                path = "G:\\Programming\\python\\discord_bot\\user_data_voice\\%s.txt" % member.id
                f = open(path, "a")
                f.write("%d\n" % now.hour)
                f.close()
                print(str(member) + " is on the voice channel at " + str(now.hour))

        await asyncio.sleep(1800)


#Calculates the most frequent time
async def calculate_frequent_times():
    player_data = []
    for guild in client.guilds:
        for member in guild.members:
            path = "G:\\Programming\\python\\discord_bot\\user_data_voice\\"

            y = str(member.id)
            file = "%s.txt" % (str(member.id))
            times = []
            for filename in os.listdir(path):
                # print(filename)
                if(filename == file):
                    path = "G:\\Programming\\python\\discord_bot\\user_data_voice\\%s.txt" % member.id
                    
                    f = open(path,"r")

                    for x in f:
                        times.append(x)

            unique_num = unique_numbers(times)

            counter = 0
            max = 0

            while(counter < len(unique_num)):
                occur = times.count(unique_num[counter])
                if(int(occur) > int(max)):
                    max = unique_num[counter]
                counter = counter + 1
            player_data.append("%s is most likely to be online at %s" % (client.get_user(member.id), time_convert(int(max))))

    return player_data

#Helper method for calculating the most frequent time.
def unique_numbers(array):
    list_uniq = []
    counter = 0

    while(counter < len(array)):
        if(array[counter] not in list_uniq):
            list_uniq.append(array[counter])
        counter = counter + 1
    
    return list_uniq


def time_convert(time):
    if(time > 12):
        time_hour = "%d%s" % (time-12," PM")
        return time_hour

    elif(time == 12):
        time_hour = "%d%s" % (time," PM")
        return time_hour

    elif(time < 12 and time != 0):
        time_hour = "%d%s" %(time," AM")
        return time_hour
    elif(time == 0):
        time_hour = "%d%s" % (12," AM")
        return time_hour
    else:
        return "not enough data"

#This was for testing purposes
def print_test():
    all_player_data = calculate_frequent_times()
    final_response = ""
    for x in all_player_data:
        final_response = final_response + x + "\n"
    print(final_response)

client.loop.create_task(get_members_voice())
client.run(token)
import asyncio
import datetime

import discord
import requests
import os  # default module
from dotenv import load_dotenv

load_dotenv()  # load all the variables from the env file
bot = discord.Bot()


def check_server_status():
    url = "https://api.mcstatus.io/v2/status/java/play.kangapi.fr"
    response = requests.request("GET", url)
    JSON_response = response.json()
    return JSON_response['online']


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.slash_command(description="Start the minecraft server")
async def start(ctx):
    # Check if the server is already running
    if check_server_status():
        await ctx.respond(":red_circle: Server is already running!")
        return

    # Get the actual time
    start_time = datetime.datetime.now()

    await ctx.respond(f"Starting the server... (approx. 1 minute)")

    # Start the server with docker and the container name
    os.system(f"docker start {os.getenv('MINECRAFT_SERVER_CONTAINER_NAME')}")

    # Check if the server is running
    counter = 0
    while not check_server_status():
        # wait 5 seconds
        range_to_check = 5
        await asyncio.sleep(range_to_check)
        counter += 1
        if counter == 36:
            # Keep only the minutes

            await ctx.respond(f"{ctx.author.mention}:red_circle: Server failed to start! (stop checking after {counter * range_to_check / 60} minutes)")
            return

    # Get the actual time
    end_time = datetime.datetime.now()
    spent_time = end_time - start_time
    await ctx.respond(f"{ctx.author.mention}:green_circle: Server is now online! (took {str(spent_time.seconds)} seconds)")


@bot.slash_command(description="Stop the minecraft server")
async def stop(ctx):
    # Check if the server is already running
    if not check_server_status():
        await ctx.respond(":red_circle: Server is already stopped!")
        return

    await ctx.respond("Stopping the server...")

    # Stop the server with docker and the container name
    os.system(f"docker stop {os.getenv('MINECRAFT_SERVER_CONTAINER_NAME')}")

@bot.slash_command(description="Check if the server is running")
async def status(ctx):
    if check_server_status():

        embed = discord.Embed(
            title=":green_circle: Server is running!",
            color=discord.Colour.green()
        )

        url = "https://api.mcstatus.io/v2/status/java/play.kangapi.fr"
        response = requests.request("GET", url)
        JSON_response = response.json()

        docker_container_status = os.popen(f"docker inspect {os.getenv('MINECRAFT_SERVER_CONTAINER_NAME')}").read()
        print(docker_container_status)

        embed.add_field(name="IP", value=JSON_response['host'], inline=False)
        embed.add_field(name="Players", value=f"{JSON_response['players']['online']}/{JSON_response['players']['max']}", inline=False)
        # Show the players
        if JSON_response['players']['online'] > 0:
            players = ""
            for player in JSON_response['players']['list']:
                players += f"{player['name_clean']} "
            embed.add_field(name="Online", value=players, inline=False)

        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(
            title=":red_circle: Server is stopped!",
            color=discord.Colour.red()
        )
        await ctx.respond(embed=embed)

bot.run(os.getenv('TOKEN'))  # run the bot with the token

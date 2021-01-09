# import asyncio
import os

import discord
import random
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
D_TOKEN = os.getenv("DISCORD_TOKEN")
SERVER = os.getenv("DISCORD_SERVER")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    serv = discord.utils.get(bot.guilds, name=SERVER)
    print(
        f"{bot.user.name} has connected to Discord.\n"
        f"{serv.name}(server id: {serv.id})"
        )


@bot.event
async def on_member_join(member):
    serv = discord.utils.get(bot.guilds, name=SERVER)
    strings = (f"Hi, {member.name}, welcome to {serv.name}! "
               "Thank you for joining! This bot was created by jayyy#5860"
               " with the intention of developing, testing and building a "
               "Discord bot for fun. Want to contribute? Shoot them a DM!"
               " Enjoy your stay!")

    print(f"User connected: {member.name}, sending a DM..")
    await member.create_dm()
    await member.dm_channel.send(strings)


@bot.event
async def on_message(msg):
    serv = discord.utils.get(bot.guilds, name=SERVER)
    await bot.process_commands(msg)

    if msg.author == bot.user:
        return

    if msg.content == "Hi, PyBot!":
        await msg.channel.send(f"Hi, {msg.author}!")
    if msg.content == "PyBot, are you working?":
        await msg.channel.send("Yes!")
    if msg.content == "PyBot, what is this server's name?":
        await msg.channel.send(f"This server's name is {serv.name}.")


class MessageModeration(commands.Cog):
    # message deletion commands -- clear, purge
    @commands.command(name="clear", help=("Deletes the specified number of "
                                          "channel messages. Defaults to 5."))
    async def clear(self, ctx, n=5):
        channel = ctx.message.channel

        try:
            n = int(n) if n != "all" else n
        except ValueError:
            await ctx.send("Invalid/no number specified. Please use integers.")
            return

        d = await channel.purge(limit=n)
        await ctx.send(f"Deleted {len(d)} message(s).")

    @commands.command(name="purge", help="Purges all channel messages.")
    async def purge(self, ctx):
        channel = ctx.message.channel
        d = await channel.purge()
        await ctx.send(f"Deleted {len(d)} message(s).")


class FunCommands(commands.Cog):
    # rolls a random nmumber between two specified integers
    @commands.command(name="roll", help=("Rolls a random number between "
                                         "two given numbers. Must be "
                                         "integers."))
    async def roll(self, ctx, start, end):
        author = ctx.author
        print(f"Running roll command, triggered by {author}")
        try:
            n = random.randint(int(start), int(end))
        except ValueError:
            await ctx.send("Please enter two numbers (non-float), e.g. 1-6!")
        else:
            await ctx.send(f"Between {start}-{end}, {author} rolled: {n}!")


class GeneralCommands(commands.Cog):
    # tells the user which server they're on
    @commands.command(name="whereami", help=("Lets the user know which server "
                                             "they're on for whatever reason."
                                             ))
    async def whereami(self, ctx):
        author = ctx.message.author
        print(f"Running whereami command, triggered by {author}")
        serv = discord.utils.get(bot.guilds, name=SERVER)
        await ctx.send(f"You are on {serv.name}, {author}!")


bot.add_cog(FunCommands())
bot.add_cog(GeneralCommands())
bot.add_cog(MessageModeration())
bot.run(D_TOKEN, bot=True)

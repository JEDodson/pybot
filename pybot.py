# import asyncio
import os
import sys
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
import logging
import requests
from better_profanity import profanity

logging.basicConfig(format="%(asctime)s"+" "*20+"%(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
    # serv = discord.utils.get(bot.guilds, name=SERVER)
    await bot.process_commands(msg)
    if msg.author == bot.user:
        return

    if msg.content == "Hi, PyBot!":
        await msg.channel.send(f"Hi, {msg.author}!")
    if msg.content == "PyBot, are you working?":
        await msg.channel.send("Yes!")
    if msg.content == "Go to sleep, PyBot.":
        await msg.channel.send("Okay, going to sleep.")
        sys.exit(1)

    if profanity.contains_profanity(msg.content):
        await msg.channel.send("Ooo, you said a bad word! Naughty naughty.")


class MessageModeration(commands.Cog):
    # message deletion commands -- clear, purge
    @commands.command(name="clear", help=("Deletes the specified number of "
                                          "channel messages. Defaults to 5."))
    async def clear(self, ctx, n=5):
        author = ctx.author
        logger.info(f"Running clear command, triggered by {author}")
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
        author = ctx.author
        logger.info(f"Running purge command, triggered by {author}")
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
        logger.info(f"Running roll command, triggered by {author}")
        try:
            n = random.randint(int(start), int(end))
        except ValueError:
            await ctx.send("Please enter two numbers (non-float), e.g. 1-6!")
        else:
            await ctx.send(f"Between {start}-{end}, {author} rolled: {n}!")

    @commands.command(name="8ball", help="Ask a question, any question!")
    async def magic_8ball(self, ctx):
        author = ctx.author
        logger.info(f"Running magic_8ball command, triggered by {author}")
        options = ["It is certain.", "It is decidedly so,",
                   "Without a doubt.", "Yes – definitely.",
                   "You may rely on it.", "As I see it, yes.",
                   "Most likely.", "Outlook good.", "Yes.",
                   "Signs point to yes.", "Reply hazy, try again.",
                   "Ask again later.", "Better not tell you now.",
                   "Cannot predict now.", "Concentrate and ask again.",
                   "Don't count on it.", "My reply is no.",
                   "My sources say no.", "Outlook not so good.",
                   "Very doubtful."]
        await ctx.send(f"{random.choice(options)}")

    @commands.command(name="qod", help=("Gives the quote of the day."
                                        " optional argument: categories"))
    async def qod(self, ctx, query=""):
        quote_url = "https://quotes.rest"
        author = ctx.author
        logger.info(f"Running quote command, triggered by {author}")
        if "categories" in query:
            try:
                r = requests.get(f"{quote_url}/qod/categories")
            except r.status_code == 400:
                await ctx.send((
                    "Uh-oh! I can't get a category for you right now."
                    " How about a cookie?"))
            else:
                cat = r.json()["contents"]["categories"]
                cat_str = ""
                for k in cat.keys():
                    cat_str += k + ", "
                await ctx.send(
                    f"Categories available for quote of the day: {cat_str}")
        elif len(query) > 1:
            try:
                r = requests.get(f"{quote_url}/qod?category={query}")
            except r.status_code == 400:
                await ctx.send((
                    "Uh-oh! I can't get a category for you right now."
                    " How about a cookie?"))
            else:
                quote = r.json()["contents"]["quotes"][0]
                await ctx.send(f"\"{quote['quote']}\", by {quote['author']}")
        else:
            try:
                r = requests.get(f"{quote_url}/qod")
            except r.status_code == 400:
                await ctx.send((
                    "Uh-oh! I can't get a category for you right now."
                    " How about a cookie?"))
            else:
                quote = r.json()["contents"]["quotes"][0]
                await ctx.send(f"\"{quote['quote']}\", by {quote['author']}")


class GeneralCommands(commands.Cog):
    # tells the user which server they're on
    @commands.command(name="whereami", help=("Lets the user know which server "
                                             "they're on for whatever reason."
                                             ))
    async def whereami(self, ctx):
        author = ctx.message.author
        logger.info(f"Running whereami command, triggered by {author}")
        serv = discord.utils.get(bot.guilds, name=SERVER)
        await ctx.send(f"You are on {serv.name}, {author}!")


bot.add_cog(FunCommands())
bot.add_cog(GeneralCommands())
bot.add_cog(MessageModeration())
bot.run(D_TOKEN, bot=True)

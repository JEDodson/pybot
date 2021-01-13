# import asyncio
import os
import sys
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from trivia_dict import TRIVIA_DICT
import logging
import requests

logging.basicConfig(format="%(asctime)s"+" "*20+"%(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()
D_TOKEN = os.getenv("DISCORD_TOKEN")
SERVER = os.getenv("DISCORD_SERVER")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="#", intents=intents)

current_question = {}


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

    @commands.command(name="urban", help="Grab instant Urban Dict results")
    async def urban(self, ctx, *query):
        ur = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
        host = "mashape-community-urban-dictionary.p.rapidapi.com"
        string = " ".join(query)
        query_string = {"term": string}
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': host
        }
        try:
            r = requests.get(ur, headers=headers, params=query_string)
        except r.status_code != 200:
            await ctx.send("Unable to get an Urban response. Try again?")
        else:
            author = ctx.message.author
            logger.info(f"Running urban command, triggered by {author}")
            results = r.json()
            definition = ""
            for x in results["list"][0]["definition"]:
                if x == "[" or x == "]":
                    pass
                else:
                    definition += x
            await ctx.send(definition)


class GeneralCommands(commands.Cog):
    # tells the user which server they're on
    @commands.command(name="whereami", help=("Lets the user know which server "
                                             "they're on for whatever reason."
                                             ))
    async def whereami(self, ctx):
        author = ctx.message.author
        logger.info(f"Running whereami command, triggered by {author}")
        serv = ctx.message.guild
        await ctx.send(f"You are on {serv}, {author}!")

    @commands.command("say", help="PyBot repeats whatever you tell it to.")
    async def say(self, ctx, *echo):
        say = " ".join(echo)
        await ctx.send(say)


class StarWarsCommands(commands.Cog):
    @commands.command(name="trivia", help="Random Star Wars trivia question")
    async def trivia(self, ctx):
        author = ctx.message.author
        global current_question
        random_qa = random.choice(list(TRIVIA_DICT.items()))
        current_question[random_qa[0]] = random_qa[1]
        string = (
                  f"{author} asked for a Star Wars trivia question!"
                  f" Your Question: {random_qa[0]}"
                  " Use !answer (answer) to answer the question!")
        logger.info(f"Running trivia command, triggered by {author}")
        print(current_question)
        await ctx.send(string)

    @commands.command(name="answer", help="Answer a trivia question")
    async def answer(self, ctx, *args):
        author = ctx.message.author
        user_answer = " ".join(args)
        string = f"{author} answered correctly with {user_answer}! More?"
        qa = list(current_question.items())[0] if current_question else None
        if not current_question:
            await ctx.send("There is no active trivia question right now!")
        else:
            if user_answer.lower() in qa[1].lower():
                await ctx.send(string)
                del current_question[qa[0]]


bot.add_cog(FunCommands())
bot.add_cog(StarWarsCommands())
bot.add_cog(GeneralCommands())
bot.add_cog(MessageModeration())
bot.run(D_TOKEN, bot=True)

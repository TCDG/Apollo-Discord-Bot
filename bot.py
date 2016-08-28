#! python3
# coding: utf-8

import discord
from discord.ext import commands
import random
import logging
import sys
from datetime import datetime
from cogs.utils import checks
import json

# logging
logging.basicConfig(level=logging.WARNING)


# JSON load
def load_db():
    with open('db.json') as f:
        return json.load(f)


# Database load
db = load_db()

# bot declaration
prefix = db['prefix']

description = '''Hello! I'm Apollo, margobra8's multipurpose Discord bot.
I run with Python 3.5 <3.\n
One of my main utilities is an AdBlock for users links in nicknames.
But there are a lot of other commands I can run and things I can do.'''
bot = commands.Bot(command_prefix=prefix, description=description, no_pm=True, pm_help=True)

# ads declaration/banning from db
ads = db['ads']
# ads = [".biz"] # tests only
whitelist = db['whitelist']
role_whitelist = db['role_whitelist']
current_datetime = datetime.now().strftime("%d %b %Y %H:%M")


# Error handling
@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author,
                               '[ERROR:NoPrivateMessage] Sorry. This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.channel,
                               '[ERROR:DisabledCommand] Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        pass  # do nothing

    elif isinstance(error, commands.CheckFailure):
        await bot.send_message(ctx.message.channel,
                               "[ERROR:CheckFailure] Sorry. You don't have enough permissions to run this command.")
    elif isinstance(error, commands.CommandNotFound):
        await bot.send_message(ctx.message.channel,
                               "[ERROR:CmdNotFound] Sorry. The command you requested doesn't exist.")


@bot.event
async def on_ready():
    print('\nLogged in as')
    print("User: " + bot.user.name)
    print("ID: " + bot.user.id)
    print("Instance run at: " + current_datetime)
    print('------')
    await bot.change_status(game=discord.Game(name="%help | v.1.5"), idle=False)


@bot.event
async def on_resumed():
    print('resumed...')


@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        print("{0} has updated its nickname".format(after))
        for word in ads:
            if word.lower() in str(after.nick).lower():
                try:
                    alert = '{0.mention} nickname violates the guidelines, removing...'
                    await bot.send_message(after.server, alert.format(after))
                    await bot.change_nickname(after, '[Nick violates rules]')
                except discord.HTTPException:
                    error = "There was an error changing {0.mention} nickname."
                    await bot.send_message(after.server, error.format(after))
            else:
                continue


@bot.event
async def on_server_join(server):
    await bot.send_message(server, "Hello @everyone! I've just joined here!, please enable nickname permissions \
                                   so that I can run my commands and functions properly!")


@bot.command()
@checks.is_owner()
async def change_nick(member: discord.Member, nick_chosen: str):
    """Changes the nick of an user"""
    try:
        await bot.change_nickname(member, nick_chosen)
        await bot.say("{0} nickname successfully changed to '{1}'".format(member, nick_chosen))
    except discord.HTTPException:
        await bot.say("[ERROR:HTTPException] {0.name} has not enough permissions.".format(bot.user))


@bot.command()
@checks.is_owner()
async def change_game(*game_chosen: str):
    """Changes the game the bot is playing"""
    game_conc = ' '.join(map(str, game_chosen))
    game_str = discord.Game(name=game_conc)
    try:
        await bot.change_status(game=game_str, idle=False)
        await bot.say("```Game correctly changed to {0}```".format(game_conc))
    except discord.HTTPException:
        await bot.say("```Could not change game, please try again```")


@bot.command()
async def choose(*choices: str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))


@bot.command(enabled=False)
@checks.is_owner()
async def do_eval(*evaluation: str):
    """Sends an eval of a string"""
    arg_conc = ' '.join(map(str, evaluation))
    decision = eval(str(arg_conc))
    await bot.say(decision)


@bot.command(enabled=False)
@checks.is_owner()
async def do_exec(*execution: str):
    """Executes something"""
    arg_conc = ' '.join(map(str, execution))
    decision = exec(str(arg_conc))
    await bot.say(decision)


@bot.command()
async def purge():
    """Purges the member's nicks for censorship"""
    print("Scanning Servers and nicknames")
    for server in bot.servers:
        for member in server.members:
            print("server: {0} | user: {1.name} | role: {1.top_role} | role_id: {1.top_role.id}".format(server, member,
                                                                                                        member))
            if member.name not in whitelist:
                for word in ads:
                    if word.lower() in str(member.nick).lower():
                        try:
                            await bot.change_nickname(member, '[Nick violates rules]')
                            alert = '{0.mention} nickname violates the guidelines, removing...'
                            await bot.send_message(member.server, alert.format(member))
                        except discord.HTTPException:
                            error = "There was an error changing {0.mention} nickname."
                            await bot.send_message(member.server, error.format(member))
                            print(error)
                    else:
                        continue
            else:
                print("!!!!!! {0.name} ignored, continuing...".format(member))


"""
@bot.command(st)
async def wipe():
    # TODO: add desc Clears all messages from the server
    for discord.Message in bot.server:
        await bot.delete_message(discord.Message)
"""

sleep = "zZzZ..."


@bot.command()
@checks.is_owner()
async def shutdown():
    """Terminates the bot's main process"""
    print(sleep)
    await bot.say(sleep)
    await bot.close()


@bot.command()
@checks.is_owner()
async def user_list():
    """Displays a log of all users in every server the bot is connected to"""
    print("!!!!usrlist!!!! Scanning Servers and nicknames as requested")
    await bot.say("A list of the users in the servers has been logged into the bot console.")
    print("\nLog datetime: " + current_datetime)
    print("----------------------")
    for server in bot.servers:
        for member in server.members:
            print(
                "server: {0} | user: {1.name} | user_id: {1.id} | role: {1.top_role} | role_id: {1.top_role.id}".format(
                    server, member,
                    member))


@bot.command()
async def date_joined(member: discord.Member):
    """Says when a member joined from the bot server's database"""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))


# run dat shit tho
if __name__ == '__main__':
    if any('debug' in arg.lower() for arg in sys.argv):
        bot.command_prefix = '$'

    bot.client_id = db['client_id']
    bot.carbon_key = db['carbon_key']  # Future carbon integration???? well never know
    bot.bots_key = db['bots_key']

    bot.run(db['token'])

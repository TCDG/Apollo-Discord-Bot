#! python3
# coding: utf-8

import argparse
import json

import discord
from discord.ext import commands

from .utils import config, checks


# JSON load
def load_db():
    with open('db.json') as f:
        return json.load(f)


# Database load
db = load_db()
# ads declaration/banning from db
ads = db['ads']
# ads = [".biz"] # tests only
whitelist = db['whitelist']
role_whitelist = db['role_whitelist']


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


class AdBlock:
    """AdBlock related commands."""

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('mod.json', loop=bot.loop)

    def bot_user(self, message):
        return message.server.me if message.channel.is_private else self.bot.user

    def __check(self, ctx):
        msg = ctx.message
        if checks.is_owner_check(msg):
            return True

        # user is bot banned
        if msg.author.id in self.config.get('plonks', []):
            return False

        # check if the channel is ignored
        # but first, resolve their permissions

        perms = msg.channel.permissions_for(msg.author)
        bypass_ignore = perms.administrator

        # now we can finally realise if we can actually bypass the ignore.

        if not bypass_ignore and msg.channel.id in self.config.get('ignored', []):
            return False

        return True

    @commands.command(name='change_nick', no_pm=True, aliases=['nick_change'])
    @checks.is_owner()
    async def change_nick(self, member: discord.Member, nick_chosen: str):
        """Changes the nick of an user"""
        try:
            await self.bot.change_nickname(member, nick_chosen)
            await self.bot.say("{0} nickname successfully changed to '{1}'".format(member, nick_chosen))
        except discord.HTTPException:
            await self.bot.say("[ERROR:HTTPException] {0.name} has not enough permissions.".format(self.bot.user))

    @commands.command(name='censor', no_pm=True, aliases=['clean'])
    async def censor(self):
        """Purges the member's nicks for censorship"""
        print("Scanning Servers and nicknames")
        for server in self.bot.servers:
            for member in server.members:
                print("server: {0} | user: {1.name} | role: {1.top_role} | role_id: {1.top_role.id}".format(server,
                                                                                                            member,
                                                                                                            member))
                if member.name not in whitelist:
                    for word in ads:
                        if word.lower() in str(member.nick).lower():
                            try:
                                await self.bot.change_nickname(member, '[Nick violates rules]')
                                alert = '{0.mention} nickname violates the guidelines, removing...'
                                await self.bot.send_message(member.server, alert.format(member))
                            except discord.HTTPException:
                                error = "There was an error changing {0.mention} nickname."
                                await self.bot.send_message(member.server, error.format(member))
                                print(error)
                        else:
                            continue
                else:
                    print("!!!!!! {0.name} ignored, continuing...".format(member))


def setup(bot):
    bot.add_cog(AdBlock(bot))

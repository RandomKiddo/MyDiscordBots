import discord
from discord.ext import commands, tasks
from discord.utils import get
import datetime
from random import randint, choice
import os
import time
import json
import webcolors
import requests
from bs4 import BeautifulSoup as bs
import asyncio
import traceback
#from discord_ui import UI, SlashOption, Button

TOKEN = 'OBSCURED'

client = commands.Bot(command_prefix = '-', intents = discord.Intents.all())
client.remove_command('help')
#ui = UI(client)

VERSION = '3.0.0'
CLOUD_VERSION = 2
VERSION_MSG = 'Changes from 2.1.16 to 3.0.0 -> Hello Google Cloud VM!\nChanges from 2.1.15 to 2.1.16 -> Added More Responses'
UP_TO_DATE = True
LINES = 958

# Events

@client.event
async def on_ready():
    await client.change_presence(activity = discord.Game(name = 'The Duck Song'))
    global start_time
    start_time = time.time()

@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
    	await process_mention(message)
    await client.process_commands(message)

async def process_mention(message):
    await message.channel.send(await smart_response(message.content.lower()))

async def smart_response(r):
    f = open('responses.json', 'r')
    content = json.load(f)
    for _ in content:
        if _ in r:
            return str(choice(content[_]))
    return str(choice(content['null']))

@client.event
async def on_connect():
    pass

@client.event
async def on_disconnect():
    pass

@client.event
async def on_raw_reaction_add(payload):
    m_id = payload.message_id
    f = open('payload.json', 'r')
    j = json.load(f)
    try:
        data = json[m_id]
    except Exception:
        return
    if data is None:
        return
    role = payload.member.guild.get_role(data[0])
    emoji = get(client.emojis, name=data[1])
    await payload.member.add_roles(role)
    message = await payload.member.guild.get_channel(payload.channel_id).fetch_message(m_id)
    await message.remove_reaction(emoji, payload.member)

@client.event
async def on_command_error(ctx, error):
    if type(error) is commands.CommandOnCooldown:
        await errmsg(ctx, f'Woah there! Retry this in `{error.retry_after}`s')
    else:
        await errmsg(ctx, str(error))

async def errmsg(ctx, descr):
    if ctx.author.id == 'OBSCURED':
        embed = discord.Embed(
            title = 'An Error Occurred',
            description = traceback.format_exc(),
            colour = discord.Colour.red()
        )
        await ctx.send(embed=embed)
    else:
    	embed = discord.Embed(
	    title = 'An Error Occurred',
	    description = descr,
	    colour = discord.Colour.red()
        )
    	await ctx.send(embed=embed)

@client.event
async def on_member_join(member):
    door = member.guild.get_channel('OBSCURED')
    await door.send(f'Hello <@{member.id}>! Don\'t forget to read the rules or check out the new members channel!')

@client.event
async def on_member_remove(member):
    door = member.guild.get_channel('OBSCURED')
    await door.send(f'Goodbye {member.name}!')

# Commands

@client.command()
async def ping(ctx):
    '''Pong'''
    api = int((round(client.latency, 3)) * 1000)
    now = datetime.datetime.now()
    now = now.replace(tzinfo=None)
    at = ctx.message.created_at
    at = at.replace(tzinfo=None)
    bot = str(now - at)
    bot = bot[9:11]
    bot = str(bot).rstrip(':')
    await ctx.send('Pong! API: `{}ms`, Bot: `{}ms`'.format(api, bot))

@client.command(aliases = ['colour'])
async def color(ctx, hexcode):
    uid = ctx.author.id
    user = ctx.guild.get_member(int(uid))
    if user == None:
        await errmsg(ctx, 'An User Fetch Error Occurred')
        return
    roles = user.roles
    if roles[len(roles) - 1].name == 'Admin':
        role = roles[len(roles) - 2]
    else:
        role = roles[len(roles) - 1]
    possible_random = hexcode
    if 'random' in possible_random.lower():
        code = lambda: randint(0, 255)
        r = code()
        g = code()
        b = code()
        await role.edit(colour = discord.Colour.from_rgb(r, g, b))
        hexcode = '#{:02x}{:02x}{:02x}'.format(r, g, b)
        await ctx.send('Name Role Color Updated To {}'.format(hexcode))
        return
    if '#' not in hexcode:
        await errmsg(ctx, 'No Hex Code Found (# Is Mandatory)')
        return
    hexcode = str(hexcode).lstrip('#').strip()
    hlen = len(hexcode)
    rgb = tuple(int(hexcode[i:i + hlen//3], 16) for i in range(0, hlen, hlen//3))
    await role.edit(colour = discord.Colour.from_rgb(rgb[0], rgb[1], rgb[2]))
    await ctx.send('Name Role Color Updated To #{}'.format(hexcode))

@client.command()
async def swore(ctx):
    guild = ctx.guild
    voice_channels = guild.voice_channels
    for _ in voice_channels:
        if _.id == 'OBSCURED':
            channel = _
    name = channel.name
    index = name.index(':')
    num = int(name[index + 2:].strip())
    rest = name[:index + 2]
    num += 1
    await channel.edit(name = '{}{}'.format(rest, str(num)))
    await ctx.send('OBSCURED\'s Swear Jar Incremented')

@client.command(aliases = ['nr'])
async def namerole(ctx, role_name):
    if not ctx.author.guild_permissions.administrator:
        await errmsg(ctx, 'You don\'t have permission to do this')
        return
    guild = ctx.guild
    new_role = await guild.create_role(
        name = role_name,
        permissions = discord.Permissions(
            create_instant_invite = True,
            kick_members = False,
            ban_members = False,
            administrator = False,
            manage_channels = False,
            manage_guild = False,
            add_reactions = True,
            view_audit_log = False,
            priority_speaker = False,
            stream = True,
            read_messages = True,
            send_messages = True,
            send_tts_messages = False,
            manage_messages = False,
            embed_links = True,
            attach_files = True,
            read_message_history = True,
            mention_everyone = True,
            external_emojis = True,
            view_guild_insights = False,
            connect = True,
            speak = True,
            mute_members = False,
            deafen_members = False,
            move_members = False,
            use_voice_activation = True,
            change_nickname = True,
            manage_nicknames = False,
            manage_roles = False,
            manage_webhooks = False,
            manage_emojis = False
        ),
        colour = discord.Colour.default(),
        hoist = False,
        mentionable = True,
        reason = 'New Name Role For New Member'
    )
    await ctx.send('Role {} Created Successfully'.format(new_role))
    i = 1
    for role in guild.roles:
        if role.name == 'Member':
            member_position = i
            break
        i += 1
    await ctx.send('Member Role Position Found At {}'.format(member_position))
    await new_role.edit(position = member_position)
    await ctx.send('{} Role Positioned Successfully'.format(new_role))

@client.command()
async def wr(ctx, value):
    guild = ctx.guild
    voice_channels = guild.voice_channels
    for _ in voice_channels:
        if _.id == 'OBSCURED':
            channel = _
    name = channel.name
    index = name.index(':')
    current_value = int(name[index + 2:])
    if int(value) < current_value:
        return
    rest = name[:index + 2]
    await channel.edit(name = '{}{}'.format(rest, str(value)))
    await ctx.send('Ping WR Updated To: {}'.format(str(value)))

@client.command(aliases = ['nick'])
async def nickname(ctx, nickname):
    author = ctx.author
    if 'remove' in nickname.lower().strip():
        await author.edit(nick = None)
        await ctx.send('Nickname Removed')
    else:
        await author.edit(nick = nickname)
        await ctx.send('Nickname Updated To {}'.format(nickname))

@client.command()
async def help(ctx, cmd = None):
    if cmd is None:
        embed = discord.Embed(
            title = 'Help',
            description = 'Psyduck Help Page',
            colour = discord.Colour.default()
        )
        embed.add_field(
            name = 'System',
            value = '`ping`, `help`, `lock`, `unlock`, `poll`, `clear`, `version`, `slowmode`, `stats`, `status`, `statusinfo`, `privatize`, `unprivatize`, `uptime`, `lines`, `report`, `suggestion`, `resolve`',
            inline = False
        )
        embed.add_field(
            name = 'Custom',
            value = '`color`, `swore`, `namerole`, `wr`, `nickname`, `ohio`, `bruh`, `spam`, `stop`, `forgive`, `seecolor`, `repeat`',
            inline = False
        )
        await ctx.send(embed=embed)
    else:
        SYSTEM = ['ping', 'help', 'lock', 'unlock', 'poll', 'clear', 'version', 'slowmode', 'stats', 'status', 'statusinfo',
        'privatize', 'unprivatize', 'uptime', 'lines', 'report', 'suggestion', 'resolve']
        CUSTOM = ['color', 'swore', 'namerole', 'wr', 'nickname', 'ohio', 'bruh', 'spam', 'stop', 'forgive', 'seecolor',
        'repeat']
        f = open('help.json', 'r')
        j = json.load(f)
        cmd = str(cmd)
        specified_json = None
        if cmd not in SYSTEM and cmd not in CUSTOM:
            await help(ctx, None)
            return
        elif cmd in SYSTEM:
            specified_json = j["system"][cmd]
        else:
            specified_json = j["custom"][cmd]
        embed = discord.Embed(
            title = 'Help - {}'.format(specified_json["title"]), 
            description = '`The help page for the {} command`'.format(specified_json["title"].lower()), 
            colour = discord.Colour.default()
        )
        embed.add_field(
            name = 'Usage:',
            value = specified_json["usage"],
            inline = False
        )
        embed.add_field(
            name = 'Description:', 
            value = specified_json["description"],
            inline = False
        )
        embed.add_field(
            name = 'Requires:', 
            value = 'N/A' if specified_json["requires"] == None else specified_json["requires"],
            inline = False
        )
        embed.add_field(
            name = 'Aliases:',
            value = 'N/A' if specified_json["aliases"] == None else ', '.join([str(elem) for elem in specified_json["aliases"]]),
            inline = False
        )
        embed.set_footer(text = 'Requested By: {}#{}'.format(ctx.author.name, ctx.author.discriminator))
        await ctx.send(embed=embed)

@client.command()
async def ohio(ctx):
    guild = ctx.guild
    voice_channels = guild.voice_channels
    for _ in voice_channels:
        if _.id == 'OBSCURED':
            channel = _
    name = channel.name
    index = name.index(':')
    num = int(name[index + 2:].strip())
    rest = name[:index + 2]
    num += 1
    await channel.edit(name = '{}{}'.format(rest, str(num)))
    await ctx.send('OBSCURED Ohio\'s Incremented')

@client.command()
async def bruh(ctx):
    guild = ctx.guild
    voice_channels = guild.voice_channels
    for _ in voice_channels:
        if _.id == 'OBSCURED':
            channel = _
    name = channel.name
    index = name.index(':')
    num = int(name[index + 2:].strip())
    rest = name[:index + 2]
    num += 1
    await channel.edit(name = '{}{}'.format(rest, str(num)))
    await ctx.send('Bruh Moments Incremented')

@client.command()
async def lock(ctx, amount=1, eta='UNKNOWN'):
    if not ctx.author.guild_permissions.administrator or ctx.author.voice.channel is None:
        await errmsg(ctx, 'You don\'t have permission to do this')
        return
    await ctx.author.voice.channel.edit(
        name = ctx.author.voice.channel.name + ' (LOCKED ETA_{})'.format(eta),
        user_limit = amount
    )

@client.command()
async def unlock(ctx):
    if not ctx.author.guild_permissions.administrator or ctx.author.voice.channel is None:
        await errmsg(ctx, 'You don\'t have permission to do this')
        return
    channel = ctx.author.voice.channel
    await channel.edit(
        name = channel.name[:channel.name.index('LOCKED')-2],
        user_limit = None
    )

stop = False
@client.command()
async def spam(ctx, id):
    if not ctx.author.guild_permissions.administrator:
        await errmsg(ctx, 'You don\'t have permission to do this')
        return
    guild = ctx.guild
    user = guild.get_member(int(id))
    amount_pinged = 0
    if user is not None:
        global stop
        stop = False
        global spam_user
        spam_user = user
        while not stop:
            await ctx.send(user.mention)
            amount_pinged += 1
            time.sleep(0.5)
    await ctx.send('Ping Amount: {}'.format(amount_pinged))

@client.command()
async def stop(ctx):
    global spam_user
    if ctx.author.guild_permissions.administrator or spam_user.id == ctx.author.id:
        global stop
        stop = True

@client.command()
async def poll(ctx, question, *args):
    if (len(args) > 10):
        await ctx.send("Max Options = 10")
        return
    embed = discord.Embed(
        title = str(question),
        description = 'React With The Appropriate Emoji(s) To Vote!', 
        colour = discord.Colour.default()
    )
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    index = 0
    for _ in args:
        embed.add_field(
            name = emojis[index],
            value = _,
            inline = False
        )
        index += 1
    embed.set_footer(text = 'Asked by: {}#{}'.format(ctx.author.name, ctx.author.discriminator))
    await ctx.message.delete()
    message = await ctx.channel.send(embed=embed)
    for _ in range(len(args)):
        await message.add_reaction(emojis[_])

@client.command()
async def clear(ctx, amount=10):
    if not ctx.author.guild_permissions.administrator:
        await errmsg(ctx, 'You don\'t have permission to do this')
        return
    await ctx.channel.purge(limit=amount)

@client.command()
async def test(ctx):
    if not ctx.author.guild_permissions.administrator:
        return
    channel = ctx.guild.get_channel('OBSCURED')  
    embed = discord.Embed(
        title = '@#school-dis Suppression',
        description = 'For those who despise school to the point where it makes you depressed',
        colour = discord.Colour.teal()
    )
    msg = await channel.send(embed = embed)
    await msg.add_reaction('🖊️')

@client.command()
async def stats(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title = 'Server Stats',
        description = 'Stats on The Duck Song',
        colour = discord.Colour.greyple()
    )
    embed.add_field(
        name = 'Server',
        value = f'**Name:** {guild.name}\n**ID:** {guild.id}\n**Owner:** {guild.owner}',
        inline = True
    )
    bot = 0
    real = 0
    for m in guild.members:
        if m.bot:
            bot += 1
        else:
            real += 1
    embed.add_field(
        name = 'Member',
        value = f'**Real Members:** {real}\n**Bot Members:** {bot}\n**Amount Banned:** {len(await guild.bans())}',
        inline = True
    )
    guild_roles = guild.roles
    highest_roles = []
    tracker = len(guild_roles) - 1
    while tracker >= len(guild_roles) - 3:
        if tracker >= 0:
            highest_roles.append(guild_roles[tracker].name)
        tracker -= 1
    while len(highest_roles) < 3:
        highest_roles.append(None)
    embed.add_field(
        name = 'Roles', 
        value = f'**Roles:** {len(guild_roles)}\n**Top 3 Roles:** {highest_roles[0]} | {highest_roles[1]} | {highest_roles[2]}',
        inline = True
    )
    embed.add_field(
        name = 'Filters',
        value = f'**Verification Level:** {str(guild.verification_level).title()}\n**MFA Level:** {guild.mfa_level}\n**Explicit Content:** {str(guild.explicit_content_filter).title()}',
        inline = True
    )
    cac = f'**Categories:** {len(guild.categories)}\n**Text Channels:** {len(guild.text_channels)}\n**Voice Channels:** {len(guild.voice_channels)}'
    embed.add_field(name='Channels & Categories', value=cac, inline=True)
    created = str(guild.created_at)
    created = created[:created.index('.')]
    joined = str(ctx.author.joined_at)
    joined = joined[:joined.index('.')]
    dates = f'**Created On:** {created}\n**Joined On:** {joined}'
    embed.add_field(name='Dates', value=dates, inline=True)
    nlevel = guild.default_notifications
    if nlevel == discord.NotificationLevel.all_messages:
        nlevel = 'All Messages'
    else:
        nlevel = 'Mentions Only'
    overview = f'**Region:** {str(guild.region).title()}\n**Preferred Locale:** {str(guild.preferred_locale).title()}\n**AFK Timeout:** {int(guild.afk_timeout / 60)}\n**AFK Channel:** {guild.afk_channel}\n**Notifications:** {nlevel}'
    embed.add_field(name='Overview', value=overview, inline=True)
    system = f'**System Channel:** {guild.system_channel}\n**Join Notifications:** {guild.system_channel_flags.join_notifications}'
    embed.add_field(name='System', value=system, inline=True)
    limits = f'**Emoji Limits:** {guild.emoji_limit}\n**Bitrate Limit:** {guild.bitrate_limit}\n**Filesize Limit:** {guild.filesize_limit}'
    embed.add_field(name='Limits', value=limits, inline=True)
    await ctx.send(embed=embed)

@client.command()
async def version(ctx):
    descr = None
    if UP_TO_DATE:
        descr = 'Psyduck is currently up-to-date with version {}! Hooray! :tada:\n\n{}'.format(VERSION, VERSION_MSG)
    else:
        descr = 'Psyduck is currently out-of-date compared to version 1.17.3! :frowning:\n\n{}'.format(VERSION_MSG)
    embed = discord.Embed(
        title = 'Psyduck Version `{}`'.format(VERSION),
        description = descr,
        colour = discord.Colour.gold()
    )
    embed.set_footer(text='Google Cloud Push v{}'.format(CLOUD_VERSION))
    msg = await ctx.send(embed=embed)
    emoji = [i for i in ctx.guild.emojis if i.name == 'psyduck']
    await msg.add_reaction(emoji[0])

@client.command()
async def slowmode(ctx, amt = 0):
    if not ctx.author.guild_permissions.administrator:
        await errmsg(ctx, 'You don\'t have permission to do this')
        return
    channel = ctx.channel
    amt = 0
    try:
        amt = int(amt)
    except Exception:
        amt = 5
    await channel.edit(slowmode_delay = amt)

@client.command()
async def status(ctx):
    embed = discord.Embed(
        title = 'Psyduck Status',
        description = 'Current Status of Psyduck',
        colour = discord.Colour.dark_orange()
    )
    embed.add_field(
        name = 'Status',
        value = 'API: :green_circle:\nShard: :green_circle:\nJSON: :green_circle:\nGoogle Cloud: :green_circle:\n',
        inline = True
    )
    embed.add_field(
        name = 'Key',
        value = ':green_circle: Online\n:yellow_circle: Maintenance\n:red_circle: Offline\n:purple_circle: Removed',
        inline = True
    )
    await ctx.send(embed=embed)

@client.command()
async def statusinfo(ctx):
    embed = discord.Embed(
        title = 'Psyduck Status Info', 
        description = 'Describes what the info in the `status` command means', 
        colour = discord.Colour.teal()
    )
    embed.add_field(name = 'Application Programming Interface (API)', value = 'discord.py; what the bot is coded in', inline = True)
    embed.add_field(name = 'Shard', value = 'Runs the bot, defaults to 1', inline = True)
    embed.add_field(name = 'Javascript Object Notation (JSON)', value = 'Stores payload and help data to retrieve, cutting runtime', inline = True)
    #embed.add_field(name = 'SQLite', value = 'Stores info in a database to retrieve later with SQL', inline = True)
    embed.add_field(name = 'Google Cloud', value = 'The Google Cloud VM that runs Psyduck (should always be online)', inline = True)
    #embed.add_field(name = 'Git', value = 'Github link that pushes to Heroku (should always be online)', inline=True)
    await ctx.send(embed=embed)

@client.command()
async def join(ctx):
    if ctx.author.voice is None:
        await errmsg(ctx, 'You\'re not in a vc ' + ''.join([_ for _ in ctx.guild.emojis if _.name == 'thonk']))
        return
    vc = ctx.author.voice.channel
    await vc.connect()

@client.command()
async def leave(ctx):
    for vc in client.voice_clients:
        if vc.guild == ctx.message.guild:
            await vc.disconnect()
            return
    await errmsg(ctx, 'No VC to leave!' + ''.join([_ for _ in ctx.guild.emojis if _.name == 'thonk']))

@client.command()
async def privatize(ctx, size=5):
    if ctx.author.voice is None:
        await errmsg(ctx, 'You\'re not in a vc ' + ''.join([_ for _ in ctx.guild.emojis if _.name == 'thonk']))
        return
    await ctx.send('Privatizing VC...')
    await ctx.author.voice.channel(user_limit=size)

@client.command()
async def unprivatize(ctx):
    if ctx.author.voice is None:
        await errmsg(ctx, 'You\'re not in a vc ' + ''.join([_ for _ in ctx.guild.emojis if _.name == 'thonk']))
        return
    await ctx.send('Unprivatizing VC...')
    await ctx.author.voice.channel(user_limit=None)
        
@client.command()
async def forgive(ctx):
    responses = (
        'I forgive no one...',
        'I forgive you \:)',
        'Maybe this time...',
        'No way',
        '...'
    )
    await ctx.send(choice(responses))

@client.command(aliases = ['seecolour'])
async def seecolor(ctx, *args):
    def closest_color(r):
        c = {}
        for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - r[0]) ** 2
            gd = (g_c - r[1]) ** 2
            bd = (b_c - r[2]) ** 2
            c[(rd+gd+bd)] = name
        return c[min(c.keys())]
    def get(r):
        try:
            c = a = webcolors.rgb_to_name(r)
        except ValueError:
            c = closest_color(r)
            a = None
        return a, c
    if len(args) == 3:
        rgb = (args[0], args[1], args[2])
        hexcode = '%02x%02x%02x' % rgb
        actual, closest = get(rgb)
        name = ''
        if actual is None:
            name = closest
        else:
            name = actual
    elif len(args) == 1:
        hexcode = str(args[0]).lstrip('#').strip()
        hlen = len(hexcode)
        rgb = tuple(int(hexcode[i:i + hlen//3], 16) for i in range(0, hlen, hlen//3))
        actual, closest = get(rgb)
        name = ''
        if actual is None:
            name = closest
        else:
            name = actual
    else:
        await errmsg(ctx, 'Too many arguments!')
        return
    embed = discord.Embed(
        title = name.title(),
        colour = discord.Colour.from_rgb(rgb[0], rgb[1], rgb[2])
    )
    embed.add_field(name = 'Hex', value=f'#{hexcode}', inline=True)
    embed.add_field(name = 'RGB', value=f'{rgb[0]}, {rgb[1]}, {rgb[2]}', inline=True)
    response = requests.get('https://www.google.com/search?q={}+color+image'.format(hexcode))
    soup = bs(response.content, 'html.parser')
    img = soup.find('img')
    alt = img['alt']
    embed.set_thumbnail(url='https://' + alt)
    await ctx.send(embed=embed)

@client.command()
async def uptime(ctx):
    global start_time
    delta = time.time() - start_time
    embed = discord.Embed(
        title = 'Psyduck v{} Uptime'.format(VERSION),
        colour = discord.Colour.gold()
    )
    embed.add_field(name = 'Uptime:', value=f'Psyduck v{VERSION} has been running for `{delta}`s', inline=False)
    def approx(t):
        if t < 60: return ''
        elif t >= 60 and t < 3600: return f'That\'s about {int(t // 60)}min(s)!'
        elif t >= 3600 and t < 86400: return f'That\'s about {int(t // 60)}min(s) or {int(t // 60 // 60)}hr(s)!'
        else: return f'That\'s about {int(t // 60)}min(s) or {int(t // 60 // 60)}hr(s) or {int(t // 60 // 60 // 24)}day(s)!'
    embed.set_footer(text=approx(delta))
    await ctx.send(embed=embed)

@client.command()
async def lines(ctx):
    embed = discord.Embed(title = 'Lines', description = 'There are currently `{}` lines in Psyduck\'s Source Code!'.format(LINES), colour = discord.Colour.blurple())
    embed.set_footer(text = 'Shhhhh... there\'s an @ on line 352...')
    await ctx.send(embed=embed)

@client.command(aliases = ['bug'])
async def report(ctx):
    channel = ctx.guild.get_channel('OBSCURED')
    def check(author):
        def inner_check(message):
            return message.author == author and (message.author.name != 'Psyduck' or author.name != 'Psyduck')
        return inner_check
    await ctx.send('Enter A Bug Report!')
    embed = discord.Embed(
        title = 'What Bug Did You Run Into?',
        colour = discord.Colour.red(),
        description = '`Thank You For Reporting This Bug! We\'ll Be Sure To Get It Fixed ASAP!`'
        )
    await ctx.send(embed=embed)
    try:
        response = await client.wait_for('message', check=check(ctx.author), timeout=120)
    except asyncio.TimeoutError:
        await ctx.send('We Didn\'t Get Your Bug Message')
        return
    embed = discord.Embed(
        title = 'Psyduck - Bug Report Check',
        colour = discord.Colour.red(),
        description = '`Your Bug Report Check`'
        )
    embed.add_field(name='Suggestion:', value=response.content, inline=False)
    await ctx.send('Is This Correct? Yes / No')
    await ctx.send(embed=embed)
    try:
        iscorrect = await client.wait_for('message', check=check(ctx.author), timeout=30)
    except asyncio.TimeoutError:
        await ctx.send('You Didn\'t Confirm Your Report')
        return
    if 'yes' in iscorrect.content.lower():
        embed = discord.Embed(
            title = 'Psyduck - Bug Upload',
            colour = discord.Colour.red(),
            description = '`Uploading Your Bug Report!`'
            )
        process = '**Started Upload**\n'
        embed.add_field(name='Uploading:', value=process, inline=False)
        await ctx.send(embed=embed)
        async for i in ctx.channel.history(limit=1):
            message = i
        process += '**Fetching Current Time**\n'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        process += '**Fetching Guild Name**\n'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        process += '**Fetching Your Username And Discrim**\n'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        process += '**Gathering Your Suggestion**\n'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        process += '**Compiling**\n'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        process += '**Sent**'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        t = datetime.datetime.now()
        u = ctx.author.name
        i = ctx.author.id
        d = ctx.author.discriminator
        s = response.content
        embed = discord.Embed(title = 'Bug Report @ `{}`'.format(t), description = '{} ({}#{})'.format(i, u, d), colour = discord.Colour.red())
        embed.add_field(name = '`Report`:', value = s, inline=True)
        await channel.send(embed=embed)
        u_embed = discord.Embed(title = 'Thanks For Your Bug Report!', description = 'We\'ll get back to you once we have evaluated the issue!', colour = discord.Colour.blue())
        u_embed.set_footer('Resolved by: {}'.format(ctx.author.name))
        await ctx.author.send(embed=u_embed)
    else:
        await report(ctx)

@client.command(aliases = ['suggest'])
async def suggestion(ctx):
    channel = ctx.guild.get_channel('OBSCURED')
    def check(author):
        def inner_check(message):
            return message.author == author and (message.author.name != 'Psyduck' or author.name != 'Psyduck')
        return inner_check
    await ctx.send('Enter A Suggestion!')
    embed = discord.Embed(
        title = 'What Do You Think Psyduck Could Add?',
        colour = discord.Colour.green(),
        description = '`Thank You For Your Suggestion! We\'ll Try To Implement It!`'
        )
    await ctx.send(embed=embed)
    try:
        response = await client.wait_for('message', check=check(ctx.author), timeout=120)
    except asyncio.TimeoutError:
        await ctx.send('We Didn\'t Get Your Suggestion')
        return
    embed = discord.Embed(
        title = 'Psyduck - Suggestion Check',
        colour = discord.Colour.green(),
        description = '`Your Suggestion Report Check`'
        )
    embed.add_field(name='Suggestion:', value=response.content, inline=False)
    await ctx.send('Is This Correct? Yes / No')
    await ctx.send(embed=embed)
    try:
        iscorrect = await client.wait_for('message', check=check(ctx.author), timeout=30)
    except asyncio.TimeoutError:
        await ctx.send('You Didn\'t Confirm Your Suggestion')
        return
    if 'yes' in iscorrect.content.lower():
        embed = discord.Embed(
            title = 'Psyduck - Suggestion Upload',
            colour = discord.Colour.green(),
            description = '`Uploading Your Suggestion!`'
            )
        process = '**Started Upload**\n'
        embed.add_field(name='Uploading:', value=process, inline=False)
        await ctx.send(embed=embed)
        async for i in ctx.channel.history(limit=1):
            message = i
        process += '**Fetching Current Time**\n'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        process += '**Fetching Your UUID**\n'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        process += '**Fetching Your Username and Discrim**\n'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        process += '**Gathering Your Suggestion**\n'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        process += '**Compiling**\n'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        process += '**Sent**'
        embed.set_field_at(0, name='Uploading:', value=process, inline=False)
        await message.edit(embed=embed)
        t = datetime.datetime.now()
        u = ctx.author.name
        i = ctx.author.id
        d = ctx.author.discriminator
        s = response.content
        embed = discord.Embed(title = 'Suggestion @ `{}`'.format(t), description = '{} ({}#{})'.format(i, u, d), colour = discord.Colour.green())
        embed.add_field(name = '`Report`:', value = s, inline=True)
        await channel.send(embed=embed)
        u_embed = discord.Embed(title = 'Thanks For Your Suggestion!', description = 'We\'ll get back to you once we have evaluated the suggestion!', colour = discord.Colour.blue())
        u_embed.set_footer('Resolved by: {}'.format(ctx.author.name))
        await ctx.author.send(embed=u_embed)
    else:
        await suggestion(ctx)

@client.command()
async def resolve(ctx, id, message):
    if not ctx.author.guild_permissions.administrator:
        await errmsg(ctx, 'You don\'t have permission to do this')
        return
    channel = ctx.guild.get_channel('OBSCURED')
    partial_msg = channel.get_partial_message(int(id))
    msg = await partial_msg.fetch()
    description = msg.embeds[0].description
    uid = int(description[:description.index('(')])
    user = client.get_guild('OBSCURED').get_member(uid)
    embed = discord.Embed(
        title = 'Thank you for your suggestion / bug report',
        description=message,
        colour = discord.Colour.blue()
    )
    await user.send(embed=embed)
    await msg.delete()

@client.command()
async def repeat(ctx, s):
    BLACKLIST = ('dumb', 'stupid', 'fat', 'ugly', 'idiot', 'Sathvik', 'Sathi')
    content = ctx.message.content.lower()
    for _ in BLACKLIST:
        if _ in content:
            opts = ('Ok', 'Sure', 'Yes, we know', 'L', 'Nice try')
            await ctx.send(str(choice(opts)))
            return
    await ctx.send(str(s))

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @tasks.loop(seconds=86400)
    async def bcheck(self):
        await self.bot.wait_until_ready()
        now = datetime.datetime.now()
        m = now.month
        d = now.day
        def day_ending(year):
            age = str(now.year - year)
            if age[-1] == "1": 
                return age + "st"
            elif age[-1] == "2":
                return age + "nd"
            elif age[-1] == "3":
                return age + "rd"
            else:
                return age + "th"
        with open('bdays.json', 'r') as f:
            contents = json.load(f)
            for _ in contents:
                inner = contents[_]
                if inner['month'] == m and inner['day'] == d:
                    user = client.get_guild('OBSCURED').get_member(int(_))
                    await user.send('Happy Birthday!')
                    f_age = day_ending(inner['year'])
                    await user.guild.get_channel('OBSCURED').send(f'Happy {f_age} Birthday <@{user.id}>!')
        await asyncio.sleep(86400)

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(aliases = ['rockpaperscissors'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rps(self, ctx):
        buttons = [
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="Rock",
                custom_id='r'
            ),
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="Paper",
                custom_id='p'
            ),
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="Scissors",
                custom_id='s'
            )
        ]
        action_row = interactions.ActionRow(components=buttons)
        embed = discord.Embed(
            title = 'Rock Paper Scissors',
            description = 'Are you ready?',
            colour = discord.Colour.greyple()
        )
        def check(i: discord.Interaction, button):
            return i.author == ctx.author and i.message == msg
        msg = await ctx.message.channel.send(embed=embed, components=action_row)
        try:
            interaction, button = await client.wait_for('button_click', check=check, timeout=30)
        except asyncio.TimeoutError:
            edit_embed = discord.Embed(title = 'Game Time Out :/', description='-', colour=discord.Colour.red())
            await msg.edit(embed=edit_embed)
            return
        opts = ['r', 'p', 's']
        bot_choice = choice(opts)
        if button.custom_id == bot_choice:
            draw_embed = discord.Embed(
                title = 'Draw!', 
                description = 'You both picked the same thing!', 
                colour = discord.Colour.gold()
            )
            await msg.edit(embed=draw_embed)
        elif (button.custom_id == 'r' and bot_choice == 's') or (button.custom_id == 'p' and bot_choice == 'r') or (button.custom_id == 's' and bot_choice == 'p'):
            win_embed = discord.Embed(
                title = 'You Won!',
                description = 'Congrats on beating Psyduck!',
                colour = discord.Colour.green()
            )
            await msg.edit(embed=win_embed)
        else:
            loss_embed = discord.Embed(
                title = 'Oops, You Lost!',
                description = 'Try again?',
                colour = discord.Colour.red()
            )
            await msg.edit(embed=loss_embed)

'''
@ui.slash.user_command("test", guild_ids=['OBSCURED'])
async def test(ctx, user = None):
    await ctx.send('test')
'''

client.add_cog(Birthday(client))
client.add_cog(Games(client))
client.run(TOKEN)


# TODO: Process @Psyduck Messages, errmsg on other errors, version command more info on changes

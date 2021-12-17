import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import logging
from asyncio import sleep
from time import time
import random

urls = [
    'https://www.bestbuy.com/site/nvidia-geforce-rtx-3080-10gb-gddr6x-pci-express-4-0-graphics-card-titanium-and-black/6429440.p?skuId=6429440'
#    ,
#    'https://www.bestbuy.com/site/dell-s2721dgf-27-gaming-ips-qhd-freesync-and-g-sync-compatible-monitor-with-hdr-displayport-hdmi-accent-grey/6421624.p?skuId=6421624'
]

cooldown_urls = []

oos_btn = 'c-button c-button-disabled c-button-lg c-button-block add-to-cart-button'
is_btn = 'c-button c-button-primary c-button-lg c-button-block c-button-icon c-button-icon-leading add-to-cart-button'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
}

logging.basicConfig(filename='app.log', level=logging.INFO, filemode='w')

class CooldownUrl:
    def __init__(self, url):
        self.url = url
        self.cd = 3600 // 20
    def tick(self):
        self.cd -= 1
    def done(self):
        return self.cd <= 0

def log(s):
    print(s)
    logging.info(s)

def cooldown(url):
    cd_url = CooldownUrl(url)
    cooldown_urls.append(cd_url)
    urls.remove(url)
    log(f'Placed {url} in cooldown')

def check_cooldowns():
    for cd_url in cooldown_urls[::-1]:
        cd_url.tick()
        if cd_url.done():
            urls.append(cd_url.url)
            cooldown_urls.remove(cd_url)
            log(f'Removed {cd_url.url} from cooldown')

class Lookupbot:
    def __init__(self):
        load_dotenv()
        self.TOKEN = os.getenv('DISCORD_TOKEN')
        self.names = {'GUILD' : os.getenv('GUILD_NAME'),
                      'CHANNEL' : os.getenv('CHANNEL_NAME'),
                      'ROLE' : os.getenv('ROLE_NAME')}
        print(self.names)
        self.ids = {}
        self.cnt = 0
        self.last_get_status = -1
        self.any_bad_status = False

    def set_id(self, id_name, id):
        self.ids[id_name] = id
        log(f'set {id_name} as {id}')
    
    def get_status(self, url):
            log(f'checking {url}')
            page = requests.get(url=url, headers=headers, timeout=2)
            soup = BeautifulSoup(page.text, 'html.parser')
            self.last_get_status = page.status_code
            if page.status_code != 200:
                self.any_bad_status = True
            if len(soup.find_all('button', class_=is_btn)) > 0:
                return 'InStock'
            elif soup.text.find('High Demand Product') > -1:
                return 'Pending'
            else:
                return 'NotInStock'

print(f'Hello world')

lookup = Lookupbot()
bot = commands.Bot(command_prefix='~')

@tasks.loop(seconds=20)
async def dolookup():
    i = lookup.cnt
    lookup.cnt += 1
    log(f'=== ITERATION {i} ===')
    check_cooldowns()
    #go backwards
    for url in urls[::-1]:
        status = lookup.get_status(url)
        if status == 'NotInStock':
            log('>> Not in stock')
        elif status == 'InStock':
            log('>> IN STOCK! >>')
            guild = bot.get_guild(lookup.ids['GUILD'])
            role = guild.get_role(lookup.ids['ROLE'])
            ch = bot.get_channel(lookup.ids['CHANNEL'])
            await ch.send(f'>> In stock! <@&{role.id}> <<')
            await ch.send(url)
            cooldown(url)
        elif status == 'Pending':
            log('>> IN STOCK SOON!!')
            guild = bot.get_guild(lookup.ids['GUILD'])
            role = guild.get_role(lookup.ids['ROLE'])
            ch = bot.get_channel(lookup.ids['CHANNEL'])
            await ch.send(f'SOOOOON! <@&{role.id}>')
            await ch.send(url)
        else:
            log('I should not be here')

@bot.command(name='start')
async def start_the_loop(ctx):
    if not dolookup.is_running():
        await ctx.send('Starting...')
        dolookup.start()
        log('>> Starting Bot')
    else:
        await ctx.send('Already running...')

@bot.command(name='stop')
async def stop_the_loop(ctx):
    if dolookup.is_running():
        await ctx.send('Stopping...')
        log('>> Stopping bot')
        dolookup.stop()
    else:
        await ctx.send('Already stopped...')

@bot.command(name='status')
async def x_status(ctx):
    send_status = {}
    send_status['Running'] = dolookup.is_running()
    send_status['Iteration'] = lookup.cnt
    send_status['LastHTTPStatus'] = lookup.last_get_status
    send_status['AnyBadHTTPStatus'] = lookup.any_bad_status
    s = str(send_status)
    print(s)
    await ctx.send(s)

@bot.command(name='add-item')
async def add_item(ctx):
    passed_items = ctx.message.content.split()
    passed_items.pop(0)
    for passed_item in passed_items:
        print(passed_item)
        if passed_item.startswith('https://'):
            urls.append(passed_item)
            log(f'Added {passed_item[0:50]}... to check list')
            await ctx.send(f'Added {passed_item[0:50]}... to check list')
        else:
            log(f'Bad add-item, start with \'https://\': {passed_item}')
            await ctx.send(f'Bad add-item, start with \'https://\': {passed_item[0:10]}')

@bot.command(name='urls')
async def dump_urls(ctx):
    log('Dumped URLS')
    await ctx.send(str(urls))

good_bot_replies = ['Wow thanks!', 'Sub to my OnlyFans: @NutsNBolts', 'Domo Origato Mr Roboto', 'https://www.youtube.com/watch?v=0gnrlQu0_k4']

@bot.event
async def on_message(message):
    if message.author != bot.user:
        if message.content.lower().strip() == 'good bot':
            await message.reply(good_bot_replies[random.randrange(len(good_bot_replies))])
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Bot error')

@bot.event
async def on_ready():
    log(f'{bot.user} has connected to Discord')
    found_guild, found_channel, found_role = False, False, False
    for guild in bot.guilds:
        if guild.name == lookup.names['GUILD']:
            found_guild = True
            lookup.set_id('GUILD', guild.id)
            for channel in guild.channels:
                if channel.name == lookup.names['CHANNEL']:
                    found_channel = True
                    lookup.set_id('CHANNEL', channel.id)
            for role in guild.roles:
                if role.name == lookup.names['ROLE']:
                    found_role = True
                    lookup.set_id('ROLE', role.id)
        break
    if not found_guild or not found_channel or not found_role:
        log('did not find guild, channel, or role')

bot.run(lookup.TOKEN)


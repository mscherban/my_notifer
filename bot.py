import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import logging

urls = [
    'https://www.bestbuy.com/site/nvidia-geforce-rtx-3080-10gb-gddr6x-pci-express-4-0-graphics-card-titanium-and-black/6429440.p?skuId=6429440'
#    ,
#    'https://www.bestbuy.com/site/dell-s2721dgf-27-gaming-ips-qhd-freesync-and-g-sync-compatible-monitor-with-hdr-displayport-hdmi-accent-grey/6421624.p?skuId=6421624'
]

oos_btn = 'c-button c-button-disabled c-button-lg c-button-block add-to-cart-button'
is_btn = 'c-button c-button-primary c-button-lg c-button-block c-button-icon c-button-icon-leading add-to-cart-button'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
}

logging.basicConfig(filename='app.log', level=logging.INFO, filemode='w')

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

    def set_id(self, id_name, id):
        self.ids[id_name] = id
        s = f'set {id_name} as {id}'
        print(s)
        logging.info(s)
    
    def get_status(self):
            i = self.cnt
            url = urls[i % len(urls)]
            self.cnt += 1
            print(f'{i}: checking {url}')
            logging.info(f'{i}: checking {url}')
            page = requests.get(url=url, headers=headers, timeout=2)
            soup = BeautifulSoup(page.text, 'html.parser')
            if len(soup.find_all('button', class_=is_btn)) > 0:
                return 'InStock', url
            elif soup.text.find('High Demand Product') > -1:
                return 'Pending', url
            else:
                return 'OutOfStock', url
            
print(f'Hello world')

lookup = Lookupbot()
bot = commands.Bot(command_prefix='`')

@tasks.loop(seconds=15)
async def dolookup():
    status, url = lookup.get_status()
    if status == 'NotInStock':
        print('>> Not in stock')
        logging.info('>> Not in stock')
    elif status == 'InStock':
        print('>> IN STOCK!')
        logging.info('>> IN STOCK!')
        guild = bot.get_guild(lookup.ids['GUILD'])
        role = guild.get_role(lookup.ids['ROLE'])
        ch = bot.get_channel(lookup.ids['CHANNEL'])
        await ch.send(f'In stock! <@&{role.id}>')
        await ch.send(url)
        await ch.send('Stopping bot, `start to restart')
        dolookup.stop()
    elif status == 'Pending':
        print('>> IN STOCK SOON!!')
        logging.info('>> IN STOCK SOON!!')
        guild = bot.get_guild(lookup.ids['GUILD'])
        role = guild.get_role(lookup.ids['ROLE'])
        ch = bot.get_channel(lookup.ids['CHANNEL'])
        await ch.send(f'SOOOOON! <@&{role.id}>')
        await ch.send(url)
        await ch.send('Stopping bot, `start to restart')
        dolookup.stop()

@bot.command(name='start')
async def start_the_loop(ctx):
    if not dolookup.is_running():
        await ctx.send('Starting...')
        dolookup.start()
        logging.info('>> Starting Bot')
    else:
        await ctx.send('Already running...')

@bot.command(name='stop')
async def stop_the_loop(ctx):
    if dolookup.is_running():
        await ctx.send('Stopping...')
        logging.info('>> Stopping bot')
        dolookup.stop()
    else:
        await ctx.send('Already stopped...')

@bot.command(name='status')
async def x_status(ctx):
    running = dolookup.is_running()
    s = f'running={running},iteration={lookup.cnt}'
    print(s)
    await ctx.send(s)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Bot error')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord')
    logging.info(f'{bot.user} has connected to Discord')
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
        print('did not find guild, channel, or role')
        logging.error('did not find guild, channel, or role')


# @dolookup.before_loop
# async def before_dolookup():
#     print ('waiting...')
#     await bot.wait_until_ready()

#dolookup.start()
bot.run(lookup.TOKEN)
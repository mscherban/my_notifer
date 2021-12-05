import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import time

urls = [
    'https://www.bestbuy.com/site/nvidia-geforce-rtx-3080-10gb-gddr6x-pci-express-4-0-graphics-card-titanium-and-black/6429440.p?skuId=6429440'
    ,
    'https://www.bestbuy.com/site/dell-s2721dgf-27-gaming-ips-qhd-freesync-and-g-sync-compatible-monitor-with-hdr-displayport-hdmi-accent-grey/6421624.p?skuId=6421624'
]

oos_btn = 'c-button c-button-disabled c-button-lg c-button-block add-to-cart-button'

headers = {
    'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'
}

class Lookupbot:
    def __init__(self):
        load_dotenv()
        self.TOKEN = os.getenv('DISCORD_TOKEN')
        self.guild_id = os.getenv('GUILD_ID')
        self.ch_id = os.getenv('CHANNEL_ID')
        self.role_id = os.getenv('ROLE_ID')
        self.cnt = 0
    
    def get_status(self):
            i = self.cnt
            url = urls[i % len(urls)]
            print(f'{i}: checking {url}')
            page = requests.get(url=url, headers=headers)
            soup = BeautifulSoup(page.text, 'html.parser')
            OutOfStock = soup.find_all('button', class_=oos_btn)
            self.cnt += 1
            return len(OutOfStock) == 0, url

print(f'Hello world')

lookup = Lookupbot()
bot = commands.Bot(command_prefix='`')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord')

@tasks.loop(seconds=10)
async def dolookup():
    status, url = lookup.get_status()
    if status == 0:
        print('>> Not in stock')
    else:
        print('>> IN STOCK!')
        guild = bot.get_guild(int(lookup.guild_id))
        role = guild.get_role(int(lookup.role_id))
        ch = bot.get_channel(int(lookup.ch_id))
        await ch.send(f'In stock! ' + '<@&' + str(role.id) + '>' )
        await ch.send(url)


@dolookup.before_loop
async def before_dolookup():
    print ('waiting...')
    await bot.wait_until_ready()

dolookup.start()
bot.run(lookup.TOKEN)
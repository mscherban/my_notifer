# my_notifer

## Requirements to get running:
```
sudo apt install python3 python3-venv python3-pip

git clone https://github.com/mscherban/my_notifer.git

cd my_notifer

python3 -m venv .venv

source .venv/bin/activate

pip3 install -r requirements.txt
```
## Variables
Create .env file with your: the ID of the guild(server), channel, and role:
```
# .env
DISCORD_TOKEN=XYXYXYXYXYXYX.SAKDKASKDKASKDAKSD.098788
GUILD_NAME=MyGuildName
CHANNEL_ID=MyNotificationChannel
ROLE_ID=MyRoleToPing
```

## Start the bot:
```
python3 bot.py
```

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
GUILD_ID=1112223333444445555666
CHANNEL_ID=9998887776567543222
ROLE_ID=000009987755343221211
```

## Start the bot:
```
python3 bot.py
```

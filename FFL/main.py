import json
import os
import redis
import requests
import schedule
import time
import tweepy

# Twitter Developer Account Credentials
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
key = os.getenv("KEY")
secret = os.getenv("SECRET")

# Twitter Developer Account Settings
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
auth.secure = True
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

client = redis.Redis(host=os.getenv("HOST"), port=6379, db=10,
                     password=os.getenv("REDIS_PASS"))

url = "https://api.sleeper.app/v1/players/nfl"


def get_players():
    r = requests.get(url)
    return json.loads(r.content)


def set_players():
    players = get_players()
    i = 0
    for key, value in players.items():
        i += 1
        if i % 500 == 0:
            print(f"{i} players added to database!")
        if value['position'] != "DEF":
            i = set_position_player(key, value, i)
            continue
        else:
            i = set_defense(key, value, i)
            continue
    print(f"Total of {i} players added to database")


def set_position_player(id, info, i):
    try:
        client.hset(str(id), info['full_name'], info['position'])
        return i
    except Exception:
        return i-1


def set_defense(id, info, i):
    try:
        client.hset(str(id), info["team"], info['position'])
        return i
    except Exception:
        return i-1


def get_trending(type, hours, limit):
    url = f"https://sleeper.app/v1/players/nfl/trending/{type}?lookback_hours={hours}&limit={limit}"
    r = requests.get(url)
    return json.loads(r.content)


def send_add_tweet(content):
    content = "Sleeper's top 3 added players today\n\n" + content
    content = content + "#cloudbot"
    api.update_status(content)


def send_drop_tweet(content):
    content = "Sleeper's top 3 dropped players today\n\n" + content
    content = content + "#cloudbot"
    api.update_status(content)


def trending():
    add = get_trending("add", 24, 3)
    to_string = ""
    i = 0
    for item in add:
        i += 1
        hash = client.hgetall(item["player_id"])
        for key, value in hash.items():
            key = key.decode("utf-8")
            value = value.decode("utf-8")
            if i == 1:
                position = "1st:"
            elif i == 2:
                position = "2nd:"
            else:
                position = "3rd:"
            to_string += f"{position} {key}, Position: {value}\n"
    send_add_tweet(to_string)
    drop = get_trending("drop", 24, 3)
    i = 0
    to_string = ""
    for item in drop:
        i += 1
        hash = client.hgetall(item["player_id"])
        for key, value in hash.items():
            key = key.decode("utf-8")
            value = value.decode("utf-8")
            if i == 1:
                position = "1st:"
            elif i == 2:
                position = "2nd:"
            else:
                position = "3rd:"
            to_string += f"{position} {key}, Position: {value}\n"
    send_drop_tweet(to_string)


print(time.ctime())
schedule.every().days.at("12:00").do(set_players)
schedule.every().day.at("16:30").do(trending)



while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as identifier:
        print(identifier)
        time.sleep(1)

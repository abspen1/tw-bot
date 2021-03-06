import os
import redis
import schedule
import time
import tweepy


consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
key = os.getenv("KEY")
secret = os.getenv("SECRET")


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
auth.secure = True
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
client = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379,
                     password=os.getenv("REDIS_PASS"))

if client.get('last_seen') is None:
    client.set('last_seen', '1194877411671724066')
    client.set('read', '53309254')


def auto_follow():
    client.incr('read', 50)
    # terms = ["python", "programming", "basketball", "sports", "stock", "followback", "follow back"]
    query = "ifb"
    print(f"Following users who have tweeted about the {query}")
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(50)
    num_followed = 0
    for tweet in search:
        if tweet.user.followers_count > 5000:
            continue
        try:
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            if e.reason[:13] == "[{'code': 283":
                return
            time.sleep(2)
        try:
            api.create_friendship(tweet.user.id)
            time.sleep(2)
            # print(f"You are now following {tweet.user.screen_name}")
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429":
                print("Followed too many people... ending this")
                return
            if e.reason[:13] == "[{'code': 283":
                return
            time.sleep(2)
    query = "follow back"
    print(f"Following users who have tweeted about the {query}")
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(50)
    for tweet in search:
        if tweet.user.followers_count > 5000:
            continue
        try:
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            if e.reason[:13] == "[{'code': 283":
                return
            time.sleep(2)
        try:
            api.create_friendship(tweet.user.id)
            time.sleep(2)
            # print(f"You are now following {tweet.user.screen_name}")
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429":
                print("Followed too many people... ending auto_follow")
                return
            time.sleep(2)
    print(f"Now following {num_followed} more users.")


def unfollow():
    print("Running unfollow function.")
    friendNames, followNames = [], []
    try:
        for friend in tweepy.Cursor(api.friends).items(250):
            friendNames.append(friend.screen_name)
        for follower in tweepy.Cursor(api.followers).items(250):
            followNames.append(follower.screen_name)
    except tweepy.TweepError as e:
        print(e.reason)
        time.sleep(2)

    friendset = set(friendNames)
    followset = set(followNames)
    not_fback = friendset.difference(followset)
    unfollowed = 0
    for not_following in not_fback:
        unfollowed += 1
        try:
            api.destroy_friendship(not_following)
        except tweepy.TweepError as e:
            print(e.reason)
        time.sleep(5)
    print(f"Unfollowed {unfollowed} losers.")


def read_last_seen():
    # file_read = open(FILE_NAME, 'r')
    # last_seen = int(file_read.read().strip())
    # file_read.close()
    last_seen = int(client.get('last_seen'))
    return last_seen


def store_last_seen(last_seen):
    # file_write = open(FILE_NAME, 'w')
    # file_write.write(str(last_seen))
    # file_write.close()
    client.set('last_seen', str(last_seen))
    return

def reply():
    # print("Checking for any mentions")
    # print(time.ctime())
    tally = 0
    tweets = api.mentions_timeline(read_last_seen(), tweet_mode='extended')
    for tweet in reversed(tweets):
        print("Replied to ID - " + str(tweet.id) + " - " + tweet.full_text)

        # api.update_status("@" + tweet.user.screen_name + " Hello, this is an auto-reply", tweet.id)
        # api.retweet(tweet.id)
        api.create_favorite(tweet.id)
        store_last_seen(tweet.id)
    client.incr('read', tally)


def searchBot():
    client.incr('read', 40)
    tweets = tweepy.Cursor(api.search, "cloud deployment").items(40)
    print("Running cloud deployment search.")
    count = 0
    for tweet in tweets:
        try:
            count += 1
            if count % 12 == 0:
                tweet.retweet()
                print("Retweet done!")
            api.create_favorite(tweet.id)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            else:
                print(e.reason)
                return
        time.sleep(2)


def searchBot2():
    client.incr('read', 20)
    tweets = tweepy.Cursor(api.search, "google cloud").items(20)
    print("Running google cloud search.")
    count = 0
    for tweet in tweets:
        count += 1
        try:
            # tweet.retweet()
            if count % 20 == 0:
                print(f"Favorited {count} google cloud tweets!")
            api.create_favorite(tweet.id)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            else:
                print(e.reason)
                return
        time.sleep(2)


def searchBot3():
    client.incr('read', 50)
    tweets = tweepy.Cursor(api.search, "python").items(50)
    print("Running python search.")
    i = 0
    for tweet in tweets:
        i += 1
        try:
            if i % 40 == 0:
                print(f"Favorited {i} python tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
        except tweepy.TweepError as e:
            print(f"Favorited {i} python tweets")
            if e.reason[:13] == "[{'code': 139":
                continue
            else:
                print(e.reason)
                return
        time.sleep(2)


def ifb_bot():
    client.incr('read', 150)
    tweets = tweepy.Cursor(api.search, "ifb").items(150)
    print("Running ifb search.")
    i = 0
    for tweet in tweets:
        i += 1
        try:
            if i % 50 == 0:
                print(f"Favorited {i} ifb tweets")
            api.create_favorite(tweet.id)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            else:
                print(e.reason)
                return
        time.sleep(2)


def searchBot4():
    client.incr('read', 36)
    tweets = tweepy.Cursor(api.search, "docker").items(36)
    print("Running docker search.")
    i = 0
    for tweet in tweets:
        i += 1
        try:
            if i % 16 == 0:
                print(f"Favorited {i} docker tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            else:
                print(e.reason)
                return
        time.sleep(2)


def tigerSearch():
    client.incr('read', 80)
    tiger = tweepy.Cursor(api.search, "#data").items(80)
    print("Running #data search.")
    i = 0
    for tweet in tiger:
        i += 1
        try:
            if i % 40 == 0:
                print(f"Favorited {i} #data tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            else:
                print(e.reason)
                return
        time.sleep(2)


def speithSearch():
    client.incr('read', 50)
    speith = tweepy.Cursor(api.search, "#bigdata").items(50)
    print("Running #bigdata search.")
    i = 0
    for tweet in speith:
        i += 1
        try:
            if i % 30 == 0:
                print(f"Favorited {i} #bigdata tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            else:
                print(e.reason)
                return
        time.sleep(2)


def fowlerSearch():
    client.incr('read', 20)
    fowler = tweepy.Cursor(api.search, "golang").items(20)
    print("Running golang search.")
    i = 0
    for tweet in fowler:
        i += 1
        try:
            if i % 20 == 0:
                print(f"Favorited {i} golang tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            else:
                print(e.reason)
                return
            time.sleep(2)


def brysonSearch():
    client.incr('read', 30)
    bryson = tweepy.Cursor(api.search, "redis").items(30)
    print("Running redis search.")
    i = 0
    for tweet in bryson:
        i += 1
        try:
            if i % 20 == 0:
                print(f"Favorited {i} redis tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            else:
                print(e.reason)
                return
        time.sleep(2)


def thank_new_followers():
    total_followers = client.scard('thanked_followers')
    thanked_followers = []
    followers = []
    if client.smembers('thanked_followers'):
        for follower in list(client.smembers('thanked_followers')):
            thanked_followers.append(follower.decode("utf-8"))
    thanked_followers = set(thanked_followers)
    new = 0
    for follower in tweepy.Cursor(api.followers).items(100):
        followers.append(str(follower.id))
        # follower has a long list of possible things to see.. kinda neat
        if not follower.following:
            try:
                follower.follow()
                time.sleep(3)
                new += 1
                # Moved this print statement so that if there is an error we don't print
            except tweepy.TweepError as e:
                """ Ignores error that we've already tried to follow this person
                    The reason we're ignoring this error is because if someone is private
                    we will keep trying to follow them until they accept our follow.
                """
                if e.reason[:13] != "[{'code': 160":
                    return
                time.sleep(2)
    if new > 0:
        print(f"Followed {new} people.")
    followers_set = set(followers)
    new_followers = followers_set.difference(thanked_followers)
    if new_followers:
        trouble = False
        # print("Thanking new followers.")
        for follower in new_followers:
            client.sadd('thanked_followers', str(follower))
            if not trouble:
                try:
                    to_string = "\nAppreciate you following me! Click the link in my bio if you're interested in creating your own automated twitter account!"
                    api.send_direct_message(follower, to_string)
                except tweepy.TweepError as e:
                    if e.reason[:13] == "[{'code': 226":
                        print("They think this is spam...")
                        trouble = True
                    else:
                        print(e.reason)
                client.sadd('thanked_followers', str(follower))
                time.sleep(3)
            else:
                client.sadd('thanked_followers', str(follower))
        new_total_followers = client.scard('thanked_followers')
        new_total_followers -= total_followers
        acct = api.get_user("Bottimus2")
        actual_followers = str(acct.followers_count)
        print(
            f"Bottimus has {new_total_followers} new followers. Total of {actual_followers} followers.")
        webapp_update()


def webapp_update():
    client = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379,
                         password=os.getenv("REDIS_PASS"))
    read = int(client.get("read"))
    acct = api.get_user("Bottimus2")
    try:
        recent = acct.status.text
    except Exception as e:
        print(e)
    client.set("followers", str(acct.followers_count))
    client.set("favorites", str(acct.favourites_count))
    client.set("statuses", str(acct.statuses_count))
    client.set("read", str(read))
    # client.set("recent", recent)


def send_error_message(follower, message):
    try:
        api.send_direct_message(follower, message)
        print("Sent dm to owner since we errored out.")
    except tweepy.TweepError as e:
        if e.reason[:13] != "[{'code': 139" or e.reason[:13] != "[{'code': 226" or e.reason[:13] != "[{'code': 429":
            print(e.reason)
        time.sleep(10*60)
        send_error_message(441228378, message)


webapp_update()
print(time.ctime())

schedule.every(5).minutes.do(thank_new_followers)
# schedule.every(4).days.do(ifb_bot)
schedule.every(2).days.at("12:23").do(searchBot)
schedule.every(3).days.at("15:23").do(searchBot2)
schedule.every(2).days.at("10:38").do(searchBot3)
schedule.every(3).days.at("08:23").do(searchBot4)
schedule.every(2).days.at("09:34").do(tigerSearch)
schedule.every(3).days.at("12:48").do(speithSearch)
schedule.every(2).days.at("14:48").do(fowlerSearch)
schedule.every(3).days.at("16:48").do(brysonSearch)
# schedule.every(2).days.at("18:01").do(auto_follow)
schedule.every().thursday.at("02:01").do(unfollow)
schedule.every().monday.at("02:01").do(unfollow)


while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except tweepy.TweepError as e:
        send_error_message(441228378, e.reason)
        time.sleep(1)

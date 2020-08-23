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
client = redis.Redis(host="10.10.10.1", port=6379,
                     password=os.getenv("REDIS_PASS"))
#api.update_status('Hello from Bottimus2. This is my second tweet!')

def auto_follow():
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


def retweet_tendie():  
    # tally = 0
    client = redis.Redis(host="10.10.10.1", port=6379,
                         password=os.getenv("REDIS_PASS"))
    tweet_id = int(client.get('since_id'))
    tweets = api.home_timeline(since_id=tweet_id, include_rts=1, count=200)
    for tweet in reversed(tweets):
        # tally += 1
        try:
            if tweet.user.screen_name == 'InternTendie' or tweet.user.screen_name == 'CalendarKy':
                # print(f"We got here at {tally}")
                if str(tweet.text)[:1] != "@" and str(tweet.text)[:2] != "RT":
                    print(tweet.text)
                    api.create_favorite(tweet.id)
                    # tweet.retweet()
                    # print(client.get('since_id'))
                    time.sleep(2)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)
        client.set('since_id', tweet.id)


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

#store_last_seen(FILE_NAME, '1194877411671724066')
def reply():
    # print("Checking for any mentions")
    # print(time.ctime())
    tweets = api.mentions_timeline(read_last_seen(), tweet_mode='extended')
    for tweet in reversed(tweets):
        print("Replied to ID - " + str(tweet.id) + " - " + tweet.full_text)

        # api.update_status("@" + tweet.user.screen_name + " Hello, this is an auto-reply", tweet.id)
        #api.retweet(tweet.id)
        api.create_favorite(tweet.id)
        store_last_seen(tweet.id)


def dm_reply():
    last_seen = int(client.get('dm_seen_2'))
    messages = api.list_direct_messages(last_seen)
    for message in reversed(messages):
        sender_id = message.message_create['sender_id']
        ## moving this if statement for quicker runtime ;]
        if not client.sismember('sent_dm_2', str(sender_id)):
            text = message.message_create['message_data']['text']
            print(text)
            if check_dm(text.lower()):
                github_dm(sender_id)
        last_seen = message.id
    client.set('dm_seen_2', str(last_seen))


def check_dm(text):
    if 'yes' in text.lower() or 'yea' in text.lower() or 'send it' in text.lower() or 'yep' in text.lower() or 'sure' in text.lower() or 'ya' in text.lower():
        return True
    return False


def github_dm(sender_id):
    client.sadd('sent_dm_2', str(sender_id))
    to_string = "\nAwesome, here is the link! If you have any questions about anything you can either create an issue within github or message me here! :)\n" + \
        "https://github.com/abspen1"
    api.send_direct_message(sender_id, to_string)

    # Subtract one here since I added my ID to ignore also
    num = client.scard('sent_dm_2') - 1
    print(f"Sent github dm : {num}")

def searchBot():
    tweets = tweepy.Cursor(api.search, "#lebronjames").items(50)
    print("Running #lebronjames search.")
    print(time.ctime())
    count = 0
    for tweet in tweets:
        try:
            count+=1
            if count % 15 == 0:
                tweet.retweet()
                print("Retweet done!")
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)


def searchBot2():
    tweets = tweepy.Cursor(api.search, "nba").items(200)
    print("Running nba search.")
    print(time.ctime())
    count = 0
    for tweet in tweets:
        count += 1
        try:
            # tweet.retweet()
            if count % 20 == 0:
                print(f"Favorited {count} nba tweets!")
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)


def searchBot3():
    tweets = tweepy.Cursor(api.search, "lakers").items(250)
    print("Running laker search.")
    print(time.ctime())
    i = 0
    for tweet in tweets:
        i += 1
        try:
            if i % 50 == 0:
                print(f"Favorited {i} laker tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)


def ifb_bot():
    tweets = tweepy.Cursor(api.search, "ifb").items(250)
    print("Running ifb search.")
    i = 0
    for tweet in tweets:
        i += 1
        try:
            if i % 50 == 0:
                print(f"Favorited {i} ifb tweets")
            api.create_favorite(tweet.id)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
        time.sleep(2)


def handles_reply():
    tweets = tweepy.Cursor(api.search, "drop your handle").items(200)
    print("Running handle search.")
    i = 0
    for tweet in tweets:
        if str(tweet.text)[:1] != "@" and str(tweet.text)[:2] != "RT":
            i += 1
            try:
                if i < 3:
                    print(f"Replied to {i} handle tweets")
                    api.update_status("@" + tweet.user.screen_name +
                                      " Follow @Bottimus2 & I'll Follow Back", tweet.id)
                    api.create_favorite(tweet.id)
                if i == 2:
                    return
            except tweepy.TweepError as e:
                if e.reason[:13] != "[{'code': 139":
                    print(e.reason)
            time.sleep(2)
        

def follow_followers():
    # print(time.ctime())
    # print("Retrieving and following followers")
    for follower in tweepy.Cursor(api.followers).items():
        if not follower.following:
            print(f"Following {follower.name}")
            follower.follow()


def searchBot4():
    tweets = tweepy.Cursor(api.search, "Kyrie Irving").items(20)
    print("Running Kyrie search.")
    print(time.ctime())
    i = 0
    for tweet in tweets:
        i += 1
        try:
            if i % 20 == 0:
                print(f"Favorited {i} Kyrie tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)


def tigerSearch():
    tiger = tweepy.Cursor(api.search, "tiger woods").items(100)
    print("Running Tiger search.")
    print(time.ctime())
    i = 0
    for tweet in tiger:
        i += 1
        try:
            if i % 40 == 0:
                print(f"Favorited {i} Tiger tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)


def speithSearch():
    speith = tweepy.Cursor(api.search, "Jordan Speith").items(50)
    print("Running Speith search.")
    print(time.ctime())
    i = 0
    for tweet in speith:
        i += 1
        try:
            if i % 30 == 0:
                print(f"Favorited {i} Speith tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)


def fowlerSearch():
    fowler = tweepy.Cursor(api.search, "Rickie Fowler").items(20)
    print("Running Fowler search.")
    print(time.ctime())
    i = 0
    for tweet in fowler:
        i += 1
        try:
            if i % 20 == 0:
                print(f"Favorited {i} Fowler tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)


def brysonSearch():
    bryson = tweepy.Cursor(api.search, "Bryson Dechambeau").items(50)
    print("Running DeChambeau search.")
    print(time.ctime())
    i = 0
    for tweet in bryson:
        i += 1
        try:
            if i % 20 == 0:
                print(f"Favorited {i} Bryson tweets")
                tweet.retweet()
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
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
        #follower has a long list of possible things to see.. kinda neat
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
                    print(e.reason)
                time.sleep(2)
    if new > 0:
        print(f"Followed {new} people.")
    followers_set = set(followers)
    new_followers = followers_set.difference(thanked_followers)
    if new_followers:
        trouble = False
        # print("Thanking new followers.")
        for follower in new_followers:
            if not trouble:
                try:
                    to_string = "\nAppreciate you following me! If you're interested in programming or if you'd like to create a twitter bot of your own, I can send you a link to my github!\n" + \
                        "If your next message has 'yes' anywhere in it I will send you a link!"
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
        total_followers = new_total_followers - total_followers
        print(f"Bottimus has {total_followers} new followers. Total of {new_total_followers} followers.")
    dm_reply()

def gain_tweet():
    try:
        client = redis.Redis(host="10.10.10.1", port=6379,
                            password=os.getenv("REDIS_PASS"))
        num = int(client.get('gain_tweet'))
        num += 1
        client.set('gain_tweet', str(num))
        tweet = f"#{num} Follow me & everyone who retweets/likes. Add your handles, I follow back! :)"
        api.update_status(tweet)
        print(f"Tweeted gain tweet #{num}")
    except tweepy.TweepError as e:
        print(e)


print(time.ctime())
#schedule.every(20).minutes.do(reply)
schedule.every(8).minutes.do(thank_new_followers)
schedule.every(10).minutes.do(dm_reply)
# schedule.every(180).seconds.do(retweet_tendie)
schedule.every(200).minutes.do(handles_reply)
schedule.every().hour.do(ifb_bot)
# schedule.every(2).hours.do(gain_tweet)
schedule.every().day.at("02:23").do(searchBot)
schedule.every().day.at("04:23").do(searchBot2)
schedule.every().day.at("06:23").do(searchBot3)
schedule.every().day.at("08:23").do(searchBot4)
schedule.every().day.at("10:48").do(tigerSearch)
schedule.every().day.at("12:48").do(speithSearch)
schedule.every().day.at("14:48").do(fowlerSearch)
schedule.every().day.at("16:48").do(brysonSearch)
schedule.every().day.at("18:01").do(auto_follow)
schedule.every().thursday.at("02:01").do(unfollow)
schedule.every().monday.at("02:01").do(unfollow)


while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except tweepy.TweepError as e:
        print(e.reason)
        time.sleep(1)

# if __name__ == "__main__":
#     searchBot()
#     searchBot2()
#     searchBot3()
#     searchBot4()
#     auto_follow()
    # unfollow()

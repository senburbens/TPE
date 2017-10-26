from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import json
import os
import sys
import time
import requests
from py2neo import authenticate, Graph, Node, Relationship


# set up authentication parameters
authenticate("localhost:7474", "neo4j", "newbensur3190")
graph = Graph()

graph.run("CREATE CONSTRAINT ON (u:User) ASSERT u.username IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (t:Tweet) ASSERT t.id IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (h:Hashtag) ASSERT h.name IS UNIQUE")


ckey='5VzxGisdpIpIvkKooMhVuXdr2'
csecret='FpGEeXirnuUKeowq8LzM4wDIMM49iAz7ETaQvv9IyuYoqnqGQC'
atoken='846421312545275904-EvXw2ZQFkKVzkXScKE6OXGmjVeDHJBK'
asecret='c35RTMXPRyZCljw0DFyJRD1XUQgtVGtCKPfCILmpK2I3p'


#def upload_tweets(tweets):
    #for t in tweets:
        #u = t["user"]
        #e = t["entities"]

        #tweet = Node("Tweet", id=t["id"])
        #graph.merge(tweet)
        #tweet["text"] = t["text"]
        #tweet.push()

        #user = Node("User", username=u["screen_name"])
        #graph.merge(user)

        #graph.merge(Relationship(user, "POSTS", tweet))

        #for h in e.get("hashtags", []):
            #hashtag = Node("Hashtag", name=h["text"].lower())
            #graph.merge(hashtag)
            #graph.merge(Relationship(hashtag, "TAGS", tweet))

        #for m in e.get('user_mentions', []):
            #mention = Node("User", username=m["screen_name"])
            #graph.merge(mention)
            #graph.merge(Relationship(tweet, "MENTIONS", mention))

        #reply = t.get("in_reply_to_status_id")

        #if reply:
            #reply_tweet = Node("Tweet", id=reply)
            #graph.merge(reply_tweet)
            #graph.merge(Relationship(tweet, "REPLY_TO", reply_tweet))

        #ret = t.get("retweeted_status", {}).get("id")

        #if ret:
            #retweet = Node("Tweet", id=ret)
            #graph.merge(retweet)
            #graph.merge(Relationship(tweet, "RETWEETS", retweet))

class listener(StreamListener) :
    
    def on_data(self, data) :
        try :
            decoded = json.loads(data)
            print '@%s: %s langue : %s' % (decoded['user']['screen_name'],decoded['text'],decoded['lang'].encode('ascii', 'ignore'))
           # print(str(decoded['coordinates']))
            #print(str(decoded['geo']))
            #print(str(decoded['user']['geo_enabled']))
            #print(str(decoded['user']['location']))
            #tweet= data.split(',"text":"')[1]#.split('","source')[0]
            #print(tweet)
            
            #upload tweets to neo4j
            tweet = Node("Tweet", id=decoded["id"])
            graph.merge(tweet)
            tweet["text"] = decoded["text"]
            tweet.push()
            #print tweet
            #print tweet['text']
            #print decoded
            
            user = Node("User", username=decoded['user']["screen_name"])
            graph.merge(user)
            print user
            
            graph.merge(Relationship(user, "POSTS", tweet))
            
            e=decoded['entities']
            print e
            
            for h in e.get("hashtags", []):
                hashtag = Node("Hashtag", name=h["text"].lower())
                graph.merge(hashtag)
                graph.merge(Relationship(hashtag, "TAGS", tweet))
            
            
            for m in e.get('user_mentions', []):
                mention = Node("User", username=m["screen_name"])
                graph.merge(mention)
                graph.merge(Relationship(tweet, "MENTIONS", mention))
            
            reply = decoded.get("in_reply_to_status_id")
            
            if reply:
                reply_tweet = Node("Tweet", id=reply)
                graph.merge(reply_tweet)
                graph.merge(Relationship(tweet, "REPLY_TO", reply_tweet))
                
            ret = decoded.get("retweeted_status", {}).get("id")    
            
            if ret:
                retweet = Node("Tweet", id=ret)
                graph.merge(retweet)
                graph.merge(Relationship(tweet, "RETWEETS", retweet))
            
            print("\n")
            saveFile=open('filtered_tweets.csv','a')
            saveFile.write(data)
            saveFile.write('\n\n\n')
            saveFile.close()
            return True
        except (BaseException, e) :
            print('failed ondata,',str(e))
            time.sleep(5)

    def on_error(self, status) :
        print(status)
        
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream=Stream(auth, listener())
twitterStream.filter(locations = [105.797482,20.995099,105.876446,21.050380]) #Hanoi
#twitterStream.filter(locations = [2.224199,48.815573,2.469921,48.902145]) #Paris
#twitterStream.filter(locations = [-72.361793,18.498006,-72.207127,18.660069]) #Port-au-Prince
#twitterStream.filter(locations = [-74.259090,40.477399,-73.700272,40.917577])# New York City













#TWITTER_BEARER = os.environ["TWITTER_BEARER"]

#headers = dict(accept="application/json", Authorization="Bearer " + TWITTER_BEARER)

#payload = dict(
    #count=100,
    #result_type="recent",
    #lang="en",
    #q=sys.argv[1]
#)

#base_url = "https://api.twitter.com/1.1/search/tweets.json?"


#def find_tweets(since_id):
    #print("debut")
    #payload["since_id"] = since_id
    #url = base_url + "q={q}&count={count}&result_type={result_type}&lang={lang}&since_id={since_id}".format(**payload)
    #print("moitie")
    #r = requests.get(url, headers=headers)
    #print("apres request")
    #print(r.json())
    #tweets = r.json()["statuses"]
    #print(tweets)
    #print("fin")
    
    #return tweets





#since_id = -1

#while True:
    #try:
        #tweets = find_tweets(since_id=since_id)
        #print("Apres appel")

        #if not tweets:
            #print("No tweets found.")
            #time.sleep(60)
            #continue


        #since_id = tweets[0].get("id")
        #upload_tweets(tweets)

        #print("{} tweets uploaded!".format(len(tweets)))
        #time.sleep(60)

    #except Exception as e:
        #print(e)
        #time.sleep(60)
        #print("NO")
        #continue



















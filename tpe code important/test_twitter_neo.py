from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import json
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
from py2neo import authenticate, Graph, Node, Relationship
from datetime import datetime
import json
from textblob import TextBlob
import re

#print  sys.getdefaultencoding()

# set up authentication parameters
authenticate("localhost:7474", "neo4j", "newbensur3190")
graph = Graph()

graph.run("CREATE CONSTRAINT ON (u:User) ASSERT u.username IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (t:Tweet) ASSERT t.id IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (h:Hashtag) ASSERT h.name IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (p:Sentiment) ASSERT p.polarite IS UNIQUE;")
#graph.run('CREATE (:Sentiment {polarite:"positif"}),(:Sentiment {polarite:"negatif"}),(:Sentiment {polarite:"neutre"});')


ckey='5VzxGisdpIpIvkKooMhVuXdr2'
csecret='FpGEeXirnuUKeowq8LzM4wDIMM49iAz7ETaQvv9IyuYoqnqGQC'
atoken='846421312545275904-EvXw2ZQFkKVzkXScKE6OXGmjVeDHJBK'
asecret='c35RTMXPRyZCljw0DFyJRD1XUQgtVGtCKPfCILmpK2I3p'

DATETIME_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'#'%Y-%m-%d_%H:%M'

def traduireTweet(textATraduire) :
	translated_text = textATraduire.translate(to='en')
	return 	translated_text

def tweetSentiment(tweet_text) :
	text_to_translate = TextBlob(clean_tweet(str(tweet_text))) 
	#print dir(translated_text)            
	if text_to_translate.detect_language() == 'en' :
		#print('TRANSLATED TEXT SAME AS ORIGINAL : ',str(text_to_translate))
	        #print('CLEANED TWEET : ', self.clean_tweet(str(text_to_translate)))
		#print('SENTIMENT : ', self.get_tweet_sentiment(self.clean_tweet(str(text_to_translate))))
		return  get_tweet_sentiment(clean_tweet(str(text_to_translate)))
	else :
		translated_text = traduireTweet(text_to_translate)
	        #translated_text = text_to_translate.translate(to='en')
		#print('TRANSLATED TEXT : ',str(translated_text))
		#print('CLEANED TWEET : ', self.clean_tweet(str(translated_text)))
		#print('SENTIMENT : ', self.get_tweet_sentiment(self.clean_tweet(str(translated_text))))
		#print('SENTIMENT : ', self.get_tweet_sentiment(str(translated_text)))
		return get_tweet_sentiment(str(translated_text))
	    

def clean_tweet(text):
	'''
	Utility function to clean tweet text by removing links, special characters
	using simple regex statements.
	'''
	return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])\
		                            |(\w+:\/\/\S+)", " ", text).split())

def get_tweet_sentiment(text):
	'''
	Utility function to classify sentiment of passed tweet
	using textblob's sentiment method
	'''
	# create TextBlob object of passed tweet text
	analysis = TextBlob(clean_tweet(text))
	# set sentiment
	if analysis.sentiment.polarity > 0:
	    return 'positif'
	elif analysis.sentiment.polarity == 0:
	    return 'neutre'
	else:
	    return 'negatif'


###############################################################################################################################################
#############################                 MATCH p = (t:Tweet)-->(b:Sentiment) RETURN nodes(p), rels(p)
#############################                 MATCH p = (t:Tweet)-->(s:Sentiment)  RETURN nodes(p)
#############################                 graph.run("MATCH p = (t:Tweet)-->(s:Sentiment)  RETURN t.annee, s.polarite").dump()
#############################                 graph.run("MATCH p = (t:Tweet)-->(s:Sentiment)  RETURN t.annee, s.polarite").data()[0]['t.annee'].encode('utf8')


###############################################################################################################################################
class listener(StreamListener) :

    def on_data(self, data) :
        try :
            decoded = json.loads(data)
            #print '@%s: %s langue : %s' % (decoded['user']['screen_name'],decoded['text'],decoded['lang'].encode('ascii', 'ignore'))
            
            #upload tweets to neo4j
            tweet = Node("Tweet", id=decoded["id"])
            graph.merge(tweet)
            tweet["text"] = decoded["text"]
            tweet["date_time"] = decoded['created_at']
            print "Apres created_at"
            datetime_object = datetime.strptime(decoded['created_at'], DATETIME_FORMAT)
            print "datetime_object"
            tweet["annee"]=str(datetime_object.year)
            print "annee"
            tweet["mois"]=str(datetime_object.month)
            tweet["jour"]=str(datetime_object.day)
	    tweet["heures"]=str(datetime_object.hour)
            tweet["minutes"]=str(datetime_object.minute)
            tweet["secondes"]=str(datetime_object.second)
            print "avant date"
            tweet["date"]=str(datetime_object.date())
	    if tweet["place_type"] : 
	    	tweet["place_type"]=str(decoded["place_type"])
	    if tweet["name"] :            
		tweet["name"]=str(decoded["name"])
	    if tweet["full_name"] : 
            	tweet["full_name"]=str(decoded["full_name"])
	    if tweet["country_code"] : 
            	tweet["country_code"]=str(decoded["country_code"])
	    if tweet["country"] : 
            	tweet["country"]=str(decoded["country"])

            print "apres date"
	    if decoded["geo"] :
		tweet["latitude"] = str(decoded['geo']['coordinates'][0])
		tweet["longitude"] = str(decoded['geo']['coordinates'][1])
            else :
                tweet["latitude"]=''
                tweet["longitude"]=''
            print "apres geo"

	    t=TextBlob(clean_tweet(clean_tweet(str(decoded["text"]))))
            print "apres textBlob"
	    tweet["lang"]=decoded["lang"]#str(t.detect_language())
            print "apres lang"

	    if  str(decoded["lang"].encode('ascii', 'ignore')) != 'en' :
		tweet["texte_traduit"]=str(traduireTweet(t))
            tweet.push()
            print "apres detect_language"
            
	    #upload User to neo4j 
            user = Node("User", username=decoded['user']["screen_name"])
            graph.merge(user)
            user["user_id"]=str(decoded['user']['id'])
            user["name"]=str(decoded['user']['name'])
            user["location"]=str(decoded['user']['location'])
            user["time_zone"]=str(decoded['user']['time_zone'])
            user["lang"]=str(decoded['user']['lang'])
            user["geo_enabled"]=str(decoded['user']['geo_enabled'])
            user["profile_image_url"]=str(decoded['user']['profile_image_url'])
            user.push()


            print user
		

	    sentiment = tweetSentiment(decoded["text"])
            sentimentNode = Node("Sentiment", polarite=sentiment)
            graph.merge(sentimentNode)

            graph.merge(Relationship(tweet, "SENTIMENT_EXPRIME", sentimentNode))
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
        except BaseException as e :
            print('failed ondata,',str(e))
            time.sleep(5)

    def on_error(self, status) :
        print(status)



auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream=Stream(auth, listener())

#twitterStream.filter(locations = [105.797482,20.995099,105.876446,21.050380]) #Hanoi
twitterStream.filter(locations = [2.224199,48.815573,2.469921,48.902145]) #Paris
#twitterStream.filter(locations = [-72.361793,18.498006,-72.207127,18.660069]) #Port-au-Prince
#twitterStream.filter(locations = [-74.259090,40.477399,-73.700272,40.917577])# New York City

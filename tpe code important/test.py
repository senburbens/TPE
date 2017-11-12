#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
from datetime import datetime
import json
from textblob import TextBlob
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re

reload(sys)
sys.setdefaultencoding('utf8')

ckey='5VzxGisdpIpIvkKooMhVuXdr2'
csecret='FpGEeXirnuUKeowq8LzM4wDIMM49iAz7ETaQvv9IyuYoqnqGQC'
atoken='846421312545275904-EvXw2ZQFkKVzkXScKE6OXGmjVeDHJBK'
asecret='c35RTMXPRyZCljw0DFyJRD1XUQgtVGtCKPfCILmpK2I3p'

DATETIME_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'#'%Y-%m-%d_%H:%M'

class listener(StreamListener) :

    def on_data(self, data) :
        try :
            decoded = json.loads(data)
	    print "\n"
            #print "Debut-------------------------------------------------------------------------"
            #print '@%s: %s langue : %s' % (decoded['user']['screen_name'],decoded['text'],decoded['lang'].encode('ascii', 'ignore'))
            print('TWEET ID : ',str(decoded['id']))
	    print('DATE ET HEURE : ',str(decoded['created_at']))
            datetime_object = datetime.strptime(decoded['created_at'], DATETIME_FORMAT)
	    #print(datetime_object)
            print(str(datetime_object.year))
            print(str(datetime_object.month))
            print(str(datetime_object.day))
	    print(str(datetime_object.hour))
            print(str(datetime_object.minute))
            print(str(datetime_object.second))
            print(str(datetime_object.date()))
            #print(dir(datetime))
	    print('USER ID : ',str(decoded['user']['id']))
	    print('USERNAME: ',str(decoded['user']['screen_name']))
	    print('ORIGINAL TEXT : ',str(decoded['text'].encode("utf-8")))
	    text_to_translate = TextBlob(self.clean_tweet(str(decoded['text']))) 
	    #print dir(translated_text)            
	    if text_to_translate.detect_language() == 'en' :
		print('TRANSLATED TEXT SAME AS ORIGINAL : ',str(text_to_translate))
		print('CLEANED TWEET : ', self.clean_tweet(str(text_to_translate)))
                print('SENTIMENT : ', self.get_tweet_sentiment(self.clean_tweet(str(text_to_translate))))
            else :
		translated_text = text_to_translate.translate(to='en')
	        print('TRANSLATED TEXT : ',str(translated_text))
	        print('CLEANED TWEET : ', self.clean_tweet(str(translated_text)))
                #print('SENTIMENT : ', self.get_tweet_sentiment(self.clean_tweet(str(translated_text))))
	        print('SENTIMENT : ', self.get_tweet_sentiment(str(translated_text)))

	    print('TWEET LANGUAGE : ',str(decoded['lang'].encode("utf-8")))
	    coordinates = decoded['geo'] 
	    if coordinates != None :
            	#print('TWEET COORDINATES : ',str(decoded['coordinates']['coordinates']))
                print("GEO : ",str(decoded['geo']))
		print('TWEET LATITUDE : ',str(decoded['geo']['coordinates'][0]))
		print('TWEET LONGITUDE : ',str(decoded['geo']['coordinates'][1]))
            else :
		print('Pas de coordonnees')

	    #if decoded['place']!= None :
	    	#print('PLACE : ',str(decoded['place']['coordinates']))

            print('GEO_ENABLED : ',str(decoded['user']['geo_enabled']))
            print('USER LOCATION : ',str(decoded['user']['location']))
            #print('USER FIELDS: ',str(decoded['user']))
            print('USER profile_image_url_https : ',str(decoded['user']['profile_image_url_https'])) 
            print('USER TIME_ZONE : ',str(decoded['user']['time_zone']))  

            print "========================================================================="
            #print data
            #print "========================================================================="
            #print encoded
            #print "Fin############################################################################"
            #tweet= data.split(',"text":"')[1]#.split('","source')[0]
            #print(tweet)
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
        #on_data(self,data) # A enlever

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])\
                                    |(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

        
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream=Stream(auth, listener())

twitterStream.filter(locations = [105.797482,20.995099,105.876446,21.050380]) #Hanoi
#twitterStream.filter(locations = [2.224199,48.815573,2.469921,48.902145]) #Paris
#twitterStream.filter(locations = [-72.361793,18.498006,-72.207127,18.660069]) #Port-au-Prince
#twitterStream.filter(locations = [-74.259090,40.477399,-73.700272,40.917577])# New York City











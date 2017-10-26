from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import json

ckey='5VzxGisdpIpIvkKooMhVuXdr2'
csecret='FpGEeXirnuUKeowq8LzM4wDIMM49iAz7ETaQvv9IyuYoqnqGQC'
atoken='846421312545275904-EvXw2ZQFkKVzkXScKE6OXGmjVeDHJBK'
asecret='c35RTMXPRyZCljw0DFyJRD1XUQgtVGtCKPfCILmpK2I3p'

class listener(StreamListener) :
    
    def on_data(self, data) :
        try :
            decoded = json.loads(data)
            #print "Debut-------------------------------------------------------------------------"
            print '@%s: %s langue : %s' % (decoded['user']['screen_name'],decoded['text'],decoded['lang'].encode('ascii', 'ignore'))
            print(str(decoded['coordinates']))
            print(str(decoded['geo']))
            print(str(decoded['user']['geo_enabled']))
            print(str(decoded['user']['location']))
            #print "========================================================================="
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
        except (BaseException, e) :
            print('failed ondata,',str(e))
            time.sleep(5)

    def on_error(self, status) :
        print(status)
        on_data(self,data) # A enlever
        
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream=Stream(auth, listener())
twitterStream.filter(locations = [105.797482,20.995099,105.876446,21.050380]) #Hanoi
#twitterStream.filter(locations = [2.224199,48.815573,2.469921,48.902145]) #Paris
#twitterStream.filter(locations = [-72.361793,18.498006,-72.207127,18.660069]) #Port-au-Prince

#twitterStream.filter(locations = [-74.259090,40.477399,-73.700272,40.917577])# New York City











import json
import urllib
import httplib
import time
import re
import sys
import math
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from anomaly import probabilisticEWMA
from collections import deque
from datetime import datetime


### These are keys from a personal account, please change them later ###
access_token = "3050139715-TjRarpLkD0omRLE8vEoE2k61BX55PPbEuYsj6ag"
access_token_secret = "S3fxhTwNckj6eawPloAOLvGMkPBQ70x1kE5B5GZiOKPI3"
consumer_key = "H8LDtkhKcVIQYsesuvAGJfZKG"
consumer_secret = "PqOup9wu87bsmHO877DLSlLVSiH3mk4KC83OJ8AO13cQJPS4lv"


class StdOutListener(StreamListener):

    def __init__(self, time_interval=60, term='trump'):
        self.sid = SentimentIntensityAnalyzer()
        self.anomalyDetector = probabilisticEWMA(term)
        self.interval = time_interval
        self.tweetBuffer = deque(maxlen=50)
        self.negCount = 0
        self.siesta = 0
        self.nightnight = 0
        self.trend = 0
        self.start = time.time()

    def on_data(self, data):

        if (time.time() - self.start) < self.interval:
            try:
                tweet = json.loads(data)['text']
                processedTweet = processTweet(tweet)
                sentiment = self.sid.polarity_scores(processedTweet)['compound']          

                if sentiment < 0.0:
                    self.negCount += 1
            except:
                pass

        else:
            # Number of negative mentions per elapsed time (in seconds)
            frequency = self.negCount / (time.time() - self.start)

            # Reseting configurations
            self.negCount = 0
            self.start = time.time()

            self.tweetBuffer.append(frequency)
            anom = self.anomalyDetector.predict(self.tweetBuffer)

            status = 0 # 0 for normal, 1 for positive anomaly, -1 for negative anomaly

            # Check if the last added data point produced an anomaly
            if anom:
                if anom[-1] == len(self.tweetBuffer)-2:
                    if self.tweetBuffer[-1] > self.tweetBuffer[-2]:
                        self.trend = 1
                        status = 1
                        #beforeSpike = self.tweetBuffer[-2]
                        #print '[' + str(datetime.now()) + '] Alert: anomaly detected'
                    else:
                        self.trend = 0
                        status = -1
            #else:
            #    if frequency < beforeSpike:
            #        self.trend = 0

            jsonData = {"status": status, "trend": self.trend, "frequency": frequency, "timestamp": datetime.utcnow().isoformat()}
            postData(jsonData)

            print "Frequency: ", frequency, " | Trend: ", self.trend, " | Status: ", status

        return True

    def on_error(self, status_code):
        print 'Error:', str(status_code)
 
        if status_code == 420:
            sleepy = 60 * math.pow(2, self.siesta)
            print "A reconnection attempt will occur in " + \
            str(sleepy/60) + " minutes."
            time.sleep(sleepy)
            self.siesta += 1
        else:
            sleepy = 5 * math.pow(2, self.nightnight)
            print "A reconnection attempt will occur in " + \
            str(sleepy) + " seconds."
            time.sleep(sleepy)
            self.nightnight += 1
        return True

def postData(data):
    try:
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        conn = httplib.HTTPConnection("qgsapp.herokuapp.com")
        conn.request("POST", "/trump", json.dumps(data), headers)
        res = conn.getresponse()
        res.read()
        conn.close()
        return True
    except:
        print "Unable to make POST request."
        return False

def processTweet(tweet):

    # Remove special characters
    tweet = tweet.encode('ascii', 'ignore')
    # Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
    # Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)
    # Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    # Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    # Trim
    tweet = tweet.strip('\'"')

    return tweet

if __name__ == '__main__':

    term = sys.argv[1]
    interval = int(sys.argv[2])*60 # time interval in seconds

    l = StdOutListener(time_interval=interval, term = term)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    while True:
        try:
            stream = Stream(api.auth, l)
            stream.filter(track=[term], languages=['en'])
        except:
            continue
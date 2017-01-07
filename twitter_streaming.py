import json
import urllib
import time
import re
import sys
import datetime
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
from anomaly import probabilisticEWMA


access_token = "3050139715-xmYY8nIHJIR8Ss0KkgChYFM5EM55GUdHWP6j1OJ"
access_token_secret = "Y1YjhMaqUi2T5RJX4o4FOoQZBEQmajT24HQs9mKV9dyeH"
consumer_key = "k16NTrZqegE2LLiw5p7SlxheN"
consumer_secret = "gMQ3jUrnBTNG5y1M54FdlQlzTGa7nhtQOl3AgS7iAFxloLnjhw"


class StdOutListener(StreamListener):

    def __init__(self, time_interval=60, term='trump'):
        self.sid = SentimentIntensityAnalyzer()
        self.anomalyDetector = probabilisticEWMA(term)
        self.interval = time_interval
        self.negCount = 0
        self.tweetBuffer = []
        self.subInterval = 10
        self.start = time.time()
        self.subStart = self.start

    def on_data(self, data):

        if (time.time() - self.start) < self.interval:

            try:
                tweet = json.loads(data)['text']
                processedTweet = processTweet(tweet)
                sentiment = self.sid.polarity_scores(processedTweet)['compound']          

                if sentiment < 0.0:
                    self.negCount += 1

                frequency = self.negCount / (time.time() - self.start) # number of negative mentions per elapsed time (in seconds)

                if (time.time() - self.subStart) >= self.subInterval:
                    frequency = self.negCount / (time.time() - self.start)
                    self.tweetBuffer.append(frequency)
                    self.subStart = time.time()

            except:
                pass
            return True

        else:

            anom = self.anomalyDetector.predict(self.tweetBuffer)

            if len(anom) > 0:
                print '[' + str(datetime.datetime.now()) + '] Alert: anomaly detected'

            #print "{} anomaly(ies) detected, {} analyzed tweets, {} negative tweets".format(len(anom), len(self.tweetBuffer), self.negCount)

            # Reseting configurations
            self.tweetBuffer = []
            self.negCount = 0
            self.start = time.time()
            return True

    def on_error(self, status):
        print status


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

    while True:
        try:
            stream = Stream(auth, l)
            stream.filter(track=[term], languages=['en'])
        except:
            continue
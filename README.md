# twitter-sentiment-watch

Real-time anomaly detection for sentiment-analyzed tweets.

## Prerequisites / Libraries
* pandas 0.17.1
* Redis
* NLTK + Vader lexicon
* Tweepy

## Usage

First set up a redis server using the following command:
```bash
redis-server
```

Run `twitter_streaming.py` with the two following parameters:
* `term` - keyword to be tracked in tweets
* `interval` - analysis time interval (in minutes)

### Example
```bash
twitter_streaming.py "donald trump" 3
```
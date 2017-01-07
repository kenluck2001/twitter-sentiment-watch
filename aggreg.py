import pandas as pd
import numpy as np
import datetime

from redis import StrictRedis

redis = StrictRedis(host='localhost', port=6379, db=0)

pd.options.mode.chained_assignment = None 



class TimeAggregation:

    def __init__( self ):
        pass


    def setdata (self, ndf):
        self.ndf = ndf


    def aggregInMinutes (self, interval=1):
        '''
            Time aggregation in minutes
        '''
        ndfgrouped = self.ndf.groupby(lambda x: (x.minute // interval) * interval)

        textDataCntDf = ndfgrouped.agg({'text': "count"})  

        timestamplist = self.ndf.resample (str(interval) +"min").ffill()#, fill_method="ffill") #list of timestamps of tweets

        #create time series
        series = pd.Series(textDataCntDf.values.T.tolist()[0], index=timestamplist.index[:len(textDataCntDf )])


        #get the tweets
        tweetlist =  ndfgrouped["text"].agg({'list':(lambda x: list(x))})

        tweetlist =  tweetlist ["list"].values.T.tolist()

        return series, tweetlist


    def aggregInHours (self, interval=1):
        '''
            Time aggregation in hours
        '''
        ndfgrouped = self.ndf.groupby(lambda x: (x.hour // interval) * interval)

        textDataCntDf = ndfgrouped.agg({'text': "count"})  

        timestamplist = self.ndf.resample (str(interval) +"H", fill_method="ffill") #list of timestamps of tweets

        #create time series
        series = pd.Series(textDataCntDf.values.T.tolist()[0], index=timestamplist.index[:len(textDataCntDf )])


        #get the tweets
        tweetlist =  ndfgrouped["text"].agg({'list':(lambda x: list(x))})

        tweetlist =  tweetlist ["list"].values.T.tolist()

        return series, tweetlist


    def aggregInDays (self, interval=1):
        '''
            Time aggregation in days
        '''
        ndfgrouped = self.ndf.groupby(lambda x: (x.day // interval) * interval)

        textDataCntDf = ndfgrouped.agg({'text': "count"})  

        timestamplist = self.ndf.resample (str(interval) +"D", fill_method="ffill") #list of timestamps of tweets

        #create time series
        series = pd.Series(textDataCntDf.values.T.tolist()[0], index=timestamplist.index[:len(textDataCntDf )])


        #get the tweets
        tweetlist =  ndfgrouped["text"].agg({'list':(lambda x: list(x))})

        tweetlist =  tweetlist ["list"].values.T.tolist()

        return series, tweetlist



if __name__ == "__main__":  
    file = open('data.json', 'r')

    json_str = file.read()

    df = pd.read_json(json_str)

    ndf = df [1:]

    ndf.timestamp = pd.to_datetime(ndf.timestamp, unit ='s')

    ndf = ndf.set_index('timestamp')

    tAggObj = TimeAggregation()
    tAggObj.setdata (ndf)

    objVal = tAggObj.aggregInMinutes (  )
    print "Time series in minutes"
    print objVal[0]
    print "Time series ( values )"
    print objVal[0].values

    """
    print "Time series ( values )"
    print objVal[0].index[0]
    print objVal[0].index[1]

    objVal = tAggObj.aggregInHours ( )
    print "Time series in hours"
    print objVal[0]


    objVal = tAggObj.aggregInDays ( )
    print "Time series in days"
    print objVal[0]
    """





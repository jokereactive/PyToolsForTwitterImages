# Author: Sarthak Ahuja
# Fetch unlimited images for a specific keyword using the twitter REST API via tweepy

####################################  SETUP  ###################################

import tweepy
import shutil
import requests
import sys
import jsonpickle
import os

API_KEY = "yhPQ4qmnUXbYJX5SubPZO417i"
API_SECRET = "mZRTdGIJkC49dGoOayzKcvFDd1fnbxNPmhia4Q7hHGBmV96YiX"

host = "localhost"                  
port = 27017
database = "WMVIV"                              #You need to create this 

auth = tweepy.AppAuthHandler(API_KEY, API_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True,
                   wait_on_rate_limit_notify=True)
 
if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)
    
################################  IMAGE DOWNLOAD  #############################

def saveToFile(tweets, tweetRepoFile):
    with open(tweetRepoFile, 'a') as f:
        for tweet in tweets:    
            f.write(jsonpickle.encode(tweet._json, unpicklable=False) +'\n')
            
#def saveToMongoDB(tweets, collection):
    ## To be Implemented
    # db = Tweet2Mongo(host, port, database, collection)

def extractImages(tweets, mediaRepoFolder):
    tweetCount = 0
    mediaURLRepoFile = mediaRepoFolder+'/tweets_media_URL.txt'
    with open(mediaURLRepoFile, 'a') as f:
        for tweet in tweets:
            for media in tweet.entities.get("media",[{}]):
                if media.get("type",None) == "photo":
                    image_content=requests.get(media["media_url"], stream=True)
                    with open(mediaRepoFolder+"/"+str(tweet.id)+".jpg", 'wb') as out_file:
                        shutil.copyfileobj(image_content.raw, out_file)
                    del image_content
                    f.write(jsonpickle.encode(tweet._json, unpicklable=False) +'\n')
                    tweetCount+=1
                print("Downloaded {0} images from the last {1} tweets".format(tweetCount, len(tweets)))

#def extractImageTweetsFromFile(filename, mediaRepoFolder):
    ## To be Implemented
    
#def extractImageTweetsFromMongoDB(collection, mediaRepoFolder):
    ## To be Implemented

#####################################  MAIN  ##################################

def getTweets(word):
    keyword = word
    searchQuery = '#'+keyword
    tweetRepo = './datasets/'+keyword
    tweetRepoFile = './datasets/'+keyword+'/tweets.txt'
    mediaRepoFolder = './datasets/'+keyword+'/images'

    if not os.path.exists(tweetRepo):
        os.makedirs(tweetRepo)

    if not os.path.exists(mediaRepoFolder):
        os.makedirs(mediaRepoFolder)
    
    maxTweets = 10000000 # Some arbitrary large number
    tweetsPerQry = 100  # this is the max the API permits

    # If results from a specific ID onwards are reqd, set since_id to that ID.
    # else default to no lower limit, go as far back as API allows
    sinceId = None

    # If results only below a specific ID are, set max_id to that ID.
    # else default to no upper limit, start from the most recent tweet matching the search query.
    max_id = -1L

    tweetCount = 0
    print("Downloading max {0} tweets".format(maxTweets))
    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry)
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            since_id=sinceId)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            max_id=str(max_id - 1))
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            since_id=sinceId)
            if not new_tweets:
                print("No more tweets found")
                break
            
            saveToFile(new_tweets, tweetRepoFile)
            #saveToMongoDB(new_tweets, keyword)
            tweetCount += len(new_tweets)
            print("Downloaded {0} tweets".format(tweetCount))
            
            extractImages(new_tweets, mediaRepoFolder)

            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            print("some error : " + str(e))
            break

    print ("Downloaded {0} tweets, Saved to {1}".format(tweetCount, fName))

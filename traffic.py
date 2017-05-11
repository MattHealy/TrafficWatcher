import os
import twitter
import boto3

HASHTAG = os.environ.get('TRAFFIC_HASHTAG')
BUCKET = os.environ.get('TRAFFIC_BUCKET') 
SCREEN_NAME = os.environ.get('TRAFFIC_HANDLE')

CONSUMER_KEY = os.environ.get('TRAFFIC_CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('TRAFFIC_CONSUMER_SECRET')
ACCESS_TOKEN_KEY = os.environ.get('TRAFFIC_ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = os.environ.get('TRAFFIC_ACCESS_TOKEN_SECRET')

api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)

client = boto3.client('s3')

response = client.get_object(
    Bucket=BUCKET,
    Key='latest_tweet_id')

previous_tweet = int(response.get('Body').read().decode())

latest_tweet = previous_tweet

print("Getting all tweets since {}".format(previous_tweet))

statuses = api.GetUserTimeline(screen_name=SCREEN_NAME, trim_user=True,
                               count=50, since_id=previous_tweet)

for s in reversed(statuses):

    latest_tweet = s.id

    if any([h.text == HASHTAG for h in s.hashtags]):
        # Post to our twitter feed
        print(s.id, s.text)
        status = api.PostUpdate(s.text)

# Record new marker in bucket
if latest_tweet != previous_tweet:
    print("Saving {} as latest tweet".format(latest_tweet))
    response = client.put_object(Body=str(latest_tweet).encode(),
                                 Bucket=BUCKET, Key='latest_tweet_id')

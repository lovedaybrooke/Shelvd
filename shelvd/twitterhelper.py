import tweepy

import secrets


class TwitterHelper(object):

    def __init__(self):
        super(TwitterHelper, self).__init__()
        auth = twitter.OAuth(
            consumer_key=secrets.consumer_key,
            consumer_secret=secrets.consumer_secret,
            token=secrets.token_key,
            token_secret=secrets.token_secret
        )
        self.api = twitter.Twitter(auth=auth)

    def send_response(self, message):
        self.api.direct_messages.new(user=secrets.twitter_handle, text=message)

import os
import logging

import twitter


class TwitterHelper(object):

    def __init__(self):
        super(TwitterHelper, self).__init__()
        auth = twitter.OAuth(
            consumer_key=os.environ['CONSUMER_KEY'],
            consumer_secret=os.environ['CONSUMER_SECRET'],
            token=os.environ['TOKEN'],
            token_secret=os.environ['TOKEN_SECRET']
        )
        self.api = twitter.Twitter(auth=auth)

    def send_response(self, DM_message):
        try:
            self.api.direct_messages.new(user=os.environ['TWITTER_HANDLE'], text=DM_message)
        except twitter.TwitterHTTPError, message:
            logging.info(message)

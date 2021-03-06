import json

from slackclient import SlackClient

from geowatchutil.client.base import GeoWatchClientWebHook


class GeoWatchClientSlack(GeoWatchClientWebHook):

    # Private
    url_api = "https://slack.com/api"

    def check_topic_exists(self, channel, timeout=5, verbose=True):
        exists = False

        self.join_channel(channel, verbose=verbose)

        try:
            url = "{base}/channels.info?token={authtoken}&channel={channel}".format(
                base=self.url_api,
                authtoken=self.authtoken,
                channel=channel)
            self._get(url)
            exists = True
        except:
            exists = False

        if verbose:
            if exists:
                print "Channel "+channel+" exists."
            else:
                print "Channel "+channel+" does not exist."

        return exists

    def create_channel(self, channel, shards=1, timeout=5, verbose=True):
        if self.check_channel_exists(channel, timeout=timeout, verbose=verbose):
            return False

        created = False
        try:
            url = "{base}/channels.create?token={authtoken}&name={channel}".format(
                base=self.url_api,
                authtoken=self.authtoken,
                channel=channel)
            self._get(url)
            created = True
        except:
            created = False

        if verbose:
            if created:
                print "Channel "+channel+" created."
            else:
                print "Channel "+channel+" could not be created"

        return created

    def join_channel(self, channel, verbose=True):
        if verbose:
            print "Joining channel "+channel
        print "Bots currently can't join channels.  You need to invite manually with /invite @botname"
        # https://github.com/slackhq/node-slack-client/issues/26
        # self._client.api_call("channels.join", channel="channel")

    def archive_channel(self, channel, timeout=5, verbose=True):
        if not self.check_channel_exists(channel, timeout=timeout, verbose=verbose):
            return False

        archived = False
        try:
            url = "{base}/channels.archive?token={authtoken}&channel={channel}".format(
                base=self.url_api,
                authtoken=self.authtoken,
                channel=channel)
            self._get(url)
            archived = True
        except:
            archived = False

        if verbose:
            if archived:
                print "Channel "+channel+" archived."
            else:
                print "Channel "+channel+" could not be archived."

        return archived

    def archive_channels(self, channels, ignore_errors=True, timeout=5, verbose=False):
        archived = True
        for channel in channels:
            archived = self.archive_channel(channel, timeout=timeout, verbose=verbose)
            if (not ignore_errors) and (not archived):
                break

        return archived

    def list_channels(self, exclude_archived=True, verbose=False):
        if self.authtoken:
            url = "{base}/channels.list?token={authtoken}&exclude_archived={exclude_archived}".format(
                base=self.url_api,
                authtoken=self.authtoken,
                exclude_archived=exclude_archived)
            response = self._get(url)
            data = json.loads(response)
            if verbose:
                print response
            channels = []
            for channel in data['channels']:
                channels.append(channel['name'])
            return channels
        else:
            print "No authtoken present."
            return []

    def __init__(self, url_webhook="", authtoken=None, templates=None):
        super(GeoWatchClientSlack, self).__init__(
            backend="slack",
            url_webhook=url_webhook,
            authtoken=authtoken,
            templates=templates)

        if authtoken:
            self._client = SlackClient(authtoken)
            d = None
            try:
                r = json.loads(self._client.api_call("auth.test"))
                self._user_id = r[u'user_id']
                self._user_name = r[u'user']
            except:
                print "Could not initialize Slack Client user"

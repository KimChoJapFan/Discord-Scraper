#
# Imported module functions
#

# Use our SimpleRequests module for this experimental version.
from SimpleRequests import SimpleRequest
from SimpleRequests.SimpleRequest import error

# Use the time module for generating timestamps and snowflakes.
from time import strptime, gmtime, mktime, time

# Use the os module for creating directories and writing files.
from os import makedirs, getcwd, path

# Use the mimetypes module to determine the mimetype of a file.
from mimetypes import MimeTypes

# Use the sqlite3 module to access SQLite databases.
from sqlite3 import connect

# Use the random module to choose from a list at random.
from random import choice

# Convert JSON to a Python dictionary for ease of traversal.
from json import loads

#
# Lambda functions
#

# Return a random string of a specified length.
random_str = lambda length: ''.join([choice('0123456789ABCDEF') for i in range(length)])

# Get the mimetype string from an input filename.
mimetype = lambda name: MimeTypes().guess_type(name)[0] \
    if MimeTypes().guess_type(name)[0] is not None \
    else 'application/octet-stream'

# Return a Discord snowflake from a timestamp.
snowflake = lambda timestamp: (timestamp - 1420070400000) << 22

# Return a timestamp from a Discord snowflake.
timestamp = lambda snowflake: ((snowflake >> 22) + 1420070400000) / 1000.0

# Create a time structure from an input timestamp.
timestruct = lambda timestamp: strptime(timestamp, '%d %m %Y %H:%M:%S')


#
# Global functions
#


def get_day(day, month, year):
    """Get the timestamps from 00:00 to 23:59 of the given day.

    :param day: The target day.
    :param month: The target month.
    :param year: The target year.
    """

    min_time = mktime(timestruct('%02d %02d %d 00:00:00' % (day, month, year)))
    max_time = (min_time + 86400.0) * 1000
    min_time *= 1000

    return {
        '00:00': snowflake(int(min_time)),
        '23:59': snowflake(int(max_time))
    }


def safe_name(name):
    """Convert name to a *nix/Windows compliant name.

    :param name: The filename to convert.
    """

    output = ""
    for char in name:
        if char not in '\\/<>:"|?*':
            output += char

    return output


def create_query_body(**kwargs):
    """Generate a search query string for Discord."""

    query = ""

    for key, value in kwargs.items():
        if value is True and key != 'nsfw':
            query += '&has=%s' % key[:-1]

        if key == 'nsfw':
            query += '&include_nsfw=%s' % str(value).lower()

    return query

#
# Classes
#


class DiscordConfig(object):
    """Just a class used to store configs as objects."""


class Discord:
    """Experimental Discord scraper class."""

    def __init__(self, config='config.json', apiver='v6'):
        """Discord constructor.

        :param config: The configuration JSON file.
        :param apiver: The current Discord API version.
        """

        with open(config, 'r') as configfile:
            configdata = loads(configfile.read())

        cfg = type('DiscordConfig', (object,), configdata)()
        if cfg.token == "" or cfg.token is None:
            error('You must have an authorization token set in %s' % config)
            exit(-1)

        self.api = apiver
        self.buffer = cfg.buffer

        self.headers = {
            'user-agent': cfg.agent,
            'authorization': cfg.token
        }

        self.types = cfg.types
        self.query = create_query_body(
            images=cfg.query['images'],
            files=cfg.query['files'],
            embeds=cfg.query['embeds'],
            links=cfg.query['links'],
            videos=cfg.query['videos'],
            nsfw=cfg.query['nsfw']
        )

        self.directs = cfg.directs if len(cfg.directs) > 0 else {}
        self.servers = cfg.servers if len(cfg.servers) > 0 else {}

        # Save us the time by exiting out when there's nothing to scrape.
        if len(cfg.directs) == 0 and len(cfg.servers) == 0:
            error('No servers or DMs were set to be grabbed, exiting.')
            exit(0)

    def get_server_name(self, serverid):
        """Get the server name by its ID.

        :param serverid: The server ID.
        """

        request = SimpleRequest(self.headers).request
        server = request.grab_page('https://discordapp.com/api/%s/guilds/%s' % (self.api, serverid))

        if server is not None and len(server) > 0:
            return '%s_%s' % (serverid, safe_name(server['name']))

        else:
            error('Unable to fetch server name from id, generating one instead.')
            return '%s_%s' % (serverid, random_str(12))

    def get_channel_name(self, channelid):
        """Get the channel name by its ID.

        :param channelid: The channel ID.
        """

        request = SimpleRequest(self.headers).request
        channel = request.grab_page('https://discordapp.com/api/%s/channels/%s' % (self.api, channelid))

        if channel is not None and len(channel) > 0:
            return '%s_%s' % (channelid, safe_name(channel['username']))

        else:
            error('Unable to fetch channel name from id, generating one instead.')
            return '%s_%s' % (channelid, random_str(12))

    @staticmethod
    def create_folders(server, channel):
        """Create the folder structure.

        :param server: The server name.
        :param channel: The channel name.
        """

        folder = path.join(getcwd(), 'Discord Scrapes', server, channel)
        if not path.exists(folder):
            makedirs(folder)

        return folder

    def download(self, url, folder):
        """Download the contents of a URL.

        :param url: The target URL.
        :param folder: The target folder.
        """

        request = SimpleRequest(self.headers).request
        request.set_header('user-agent', 'Mozilla/5.0 (X11; Linux x86_64) Chrome/78.0.3904.87 Safari/537.36')

        filename = safe_name('%s_%s' % (url.split('/')[-2], url.split('/')[-1]))
        if not path.exists(filename):
            request.stream_file(url, folder, filename, self.buffer)

    def check_config_mimetypes(self, source, folder):
        """Check the config settings against the source mimetype.

        :param source: Response from Discord search.
        :param folder: Folder where the data will be stored.
        """

        for attachment in source['attachments']:
            if self.types['images'] is True:
                if mimetype(attachment['url']).split('/')[0] == 'image':
                    self.download(attachment['proxy_url'], folder)

            if self.types['videos'] is True:
                if mimetype(attachment['url']).split('/')[0] == 'video':
                    self.download(attachment['proxy_url'], folder)

            if self.types['files'] is True:
                if mimetype(attachment['url']).split('/')[0] not in ['image', 'video']:
                    self.download(attachment['proxy_url'], folder)

    def grab_data(self, folder, server, channel):
        """Scan and grab the attachments."""

        tzdata = gmtime(time())

        try:
            for year in range(tzdata.tm_year, 2015, -1):
                for month in range(12, 1, -1):
                    for day in range(31, 1, -1):

                        if month > tzdata.tm_mon and year == tzdata.tm_year:
                            continue

                        if month == tzdata.tm_mon and day > tzdata.tm_mday:
                            continue

                        request = SimpleRequest(self.headers).request
                        today = get_day(day, month, year)

                        if server is not None:
                            request.set_header('referer', 'https://discordapp.com/channels/%s/%s' % (server, channel))
                            content = request.grab_page(
                                'https://discordapp.com/api/%s/guilds/%s/messages/search?channel_id=%s&min_id=%s&max_id=%s&%s' %
                                (self.api, server, channel, today['00:00'], today['23:59'], self.query)
                            )
                        else:
                            request.set_header('referer', 'https://discordapp.com/channels/@me/%s' % channel)
                            content = request.grab_page(
                                'https://discordapp.com/api/%s/channels/%s/messages/search?min_id=%s&max_id=%s&%s' %
                                (self.api, channel, today['00:00'], today['23:59'], self.query)
                            )

                        if content['messages'] is not None:
                            for messages in content['messages']:
                                for message in messages:
                                    self.check_config_mimetypes(message, folder)

        except ValueError:
            pass

    def grab_server_data(self):
        """Scan and grab the attachments within a server."""

        for server in self.servers.keys():
            for channels in self.servers.values():
                for channel in channels:
                    folder = self.create_folders(
                        self.get_server_name(server),
                        self.get_channel_name(channel)
                    )

                    self.grab_data(folder, server, channel)

    def grab_dm_data(self):
        """Scan and grab the attachments within a direct message."""

        for alias in self.directs.keys():
            for channel in self.directs.values():
                folder = self.create_folders(
                    path.join('Direct Messages', alias),
                    channel
                )

                self.grab_data(folder, None, channel)

#
# Initializer
#


if __name__ == '__main__':
    ds = Discord()
    ds.grab_server_data()
    ds.grab_dm_data()

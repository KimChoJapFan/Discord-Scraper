#
# Imported module functions
#

# Use our SimpleRequests module for this experimental version.
from SimpleRequests import SimpleRequest
from SimpleRequests.SimpleRequest import error

# Use the datetime module for generating timestamps and snowflakes.
from datetime import datetime, timedelta

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
snowflake = lambda timestamp_s: (timestamp_s * 1000 - 1420070400000) << 22

# Return a timestamp from a Discord snowflake.
timestamp = lambda snowflake_t: ((snowflake_t >> 22) + 1420070400000) / 1000.0


#
# Global functions
#


def get_day(day, month, year):
    """Get the timestamps from 00:00 to 23:59 of the given day.

    :param day: The target day.
    :param month: The target month.
    :param year: The target year.
    """

    min_time = datetime(year, month, day, 
        hour=0, minute=0, second=0).timestamp()

    max_time = datetime(year, month, day, 
        hour=23, minute=59, second=59).timestamp()

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

    def get_server_name(self, serverid, isdm=False):
        """Get the server name by its ID.

        :param serverid: The server ID.
        :param isdm: A flag to check whether we're in a DM or not.
        """

        if isdm:
            return serverid

        request = SimpleRequest(self.headers).request
        server = request.grab_page('https://discordapp.com/api/%s/guilds/%s' % (self.api, serverid))

        if server is not None and len(server) > 0:
            return '%s_%s' % (serverid, safe_name(server['name']))

        else:
            error('Unable to fetch server name from id, generating one instead.')
            return '%s_%s' % (serverid, random_str(12))

    def get_channel_name(self, channelid, isdm=False):
        """Get the channel name by its ID.

        :param channelid: The channel ID.
        :param isdm: A flag to check whether we're in a DM or not.
        """

        if isdm:
            return channelid

        request = SimpleRequest(self.headers).request
        channel = request.grab_page('https://discordapp.com/api/%s/channels/%s' % (self.api, channelid))

        if channel is not None and len(channel) > 0:
            return '%s_%s' % (channelid, safe_name(channel['name']))

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
                if mimetype(attachment['proxy_url']).split('/')[0] == 'image':
                    self.download(attachment['proxy_url'], folder)

            if self.types['videos'] is True:
                if mimetype(attachment['proxy_url']).split('/')[0] == 'video':
                    self.download(attachment['proxy_url'], folder)

            if self.types['files'] is True:
                if mimetype(attachment['proxy_url']).split('/')[0] not in ['image', 'video']:
                    self.download(attachment['proxy_url'], folder)

    @staticmethod
    def insert_text(server, channel, message):
        """Insert the text data into our SQLite database file.

        :param server: The server name.
        :param channel: The channel name.
        :param message: Our message object.
        """

        dbdir = path.join(getcwd(), 'Discord Scrapes')
        if not path.exists(dbdir):
            makedirs(dbdir)

        dbfile = path.join(dbdir, 'text.db')
        db = connect(dbfile)
        c = db.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS text_%s_%s (
            id TEXT,
            name TEXT,
            content TEXT,
            timestamp TEXT
        )''' % (server, channel))

        c.execute('INSERT INTO text_%s_%s VALUES (?,?,?,?)' % (server, channel), (
            message['author']['id'],
            '%s#%s' % (message['author']['username'], message['author']['discriminator']),
            message['content'],
            message['timestamp']
        ))

        db.commit()
        db.close()

    def grab_data(self, folder, server, channel, isdm=False):
        """Scan and grab the attachments.

        :param folder: The folder name.
        :param server: The server name.
        :param channel: The channel name.
        :param isdm: A flag to check whether we're in a DM or not.
        """

        date = datetime.today()

        while date.year >= 2015:
            request = SimpleRequest(self.headers).request
            today = get_day(date.day, date.month, date.year)

            if not isdm:
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

            try:
                if content['messages'] is not None:
                    for messages in content['messages']:
                        for message in messages:
                            self.check_config_mimetypes(message, folder)

                            if self.types['text'] is True:
                                if len(message['content']) > 0:
                                    self.insert_text(server, channel, message)
            except TypeError:
                continue
            
            date += timedelta(days=-1)

    def grab_server_data(self):
        """Scan and grab the attachments within a server."""

        for server, channels in self.servers.items():
            for channel in channels:
                folder = self.create_folders(
                    self.get_server_name(server),
                    self.get_channel_name(channel)
                )

                self.grab_data(folder, server, channel)

    def grab_dm_data(self):
        """Scan and grab the attachments within a direct message."""

        for alias, channel in self.directs.items():
            folder = self.create_folders(
                path.join('Direct Messages', alias),
                channel
            )

            self.grab_data(folder, alias, channel, True)

#
# Initializer
#


if __name__ == '__main__':
    ds = Discord()
    ds.grab_server_data()
    ds.grab_dm_data()

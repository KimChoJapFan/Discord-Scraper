#
# Imported module functions
#

# http module used to make connections to a web server.
from http.client import HTTPSConnection, HTTPConnection

# Time module used to generate timestamps for the snowflakes.
from time import time, gmtime, strptime, mktime

# OS module used to create directories and write files to them.
from os import path, makedirs, getcwd

# System module used to get the major version for the Python
#  interpreter and to print out errors.
from sys import stderr, version_info

# Mimetypes module used to determine the mimetype of a file
#  to sift through images, videos, and other content.
from mimetypes import MimeTypes

# Randomly choose a value from a list of values.
from random import choice

# Convert JSON to a Python dictionary for ease of reading
#  the configuration contents.
from json import loads

#
# Lambda functions
#

# Return a random string of a specified length.
random_str = lambda length: ''.join([choice('0123456879ABCDEF') for i in range(length)])

# Split URLs for the http.client module.
split_url = lambda url: {
    'scheme': url.split('/')[0][:-1],
    'domain': url.split('/')[2],
    'path'  : f"/{'/'.join(url.split('/')[3::])}"
}

# Get the mimetype string from an input filename.
mimetype = lambda filename: MimeTypes().guess_type(filename)[0] \
    if MimeTypes().guess_type(filename)[0] != None \
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

    Arguments:
        day   (int) -- The date (1, 2, 3, ..., 30, 31)
        month (int) -- The month (January = 1, February = 2, ...)
        year  (int) -- The year (2015, 2016, 2017, 2018, 2019, ...)

    Returns: dictionary
        00:00 (int) -- The earliest snowflake for the given day.
        23:59 (int) -- The latest   snowflake for the given day.
    """
    min_time = mktime(timestruct(f'{day:02} {month:02} {year} 00:00:00'))
    max_time = (min_time + 86400.0) * 1000
    min_time *= 1000

    return {
        '00:00': snowflake(int(min_time)),
        '23:59': snowflake(int(max_time))
    }

def safe_name(name):
    """Convert name to a *nix/Windows compliant name.

    Arguments:
        name (string) -- The input name to be converted.

    Returns: string
    """
    output = ""

    for char in name:
        if char not in '\\/<>:"|?*':
            output = f'{output}{char}'
    
    return output

def create_query_body(**kwargs):
    """Generate a search query string for Discord.

    Arguments:
        **kwargs (dict) -- Similar to sys.argv for a function.
            { "category" : True/False }

    Returns: string
    """
    query = ""

    for key, value in kwargs.items():
        if value == True and key != 'nsfw':
            query = f'{query}&has={key[:-1]}'

        if key == 'nsfw':
            query = f'{query}&include_nsfw={str(value).lower()}'

    return query

#
# Classes
#

class Request:
    """Experimental request class."""

    def __init__(self, headers = {}):
        """Class constructor.

        Arguments:
            headers  (dict) -- Store the input headers:
                { "header name" : "header value" }
        """
        self.headers = headers

    def grab_page(self, url, binary = False):
        """Grab the contents of a URL.

        Arguments:
            url  (string) -- The target URL.
            binary (bool) -- Whether to return the contents in binary formatting or not.

        Returns:
            String when binary = False
            Binary when binary = True
        """
        try:
            spliced = split_url(url)
            domain  = spliced['domain']
            urlpath = spliced['path']

            conn = HTTPSConnection(domain, 443)
            conn.request('GET', urlpath, headers=self.headers)
            resp = conn.getresponse()

            if resp.status < 400:
                return resp.read() if binary else loads(resp.read())

            else:
                stderr.write(f'\nReceived HTTP {resp.status} error: {resp.reason} on {url}')
                return {}
            
        except Exception as e:
            stderr.write(f'\nUnknown exception : {e}')
            return {}

class Discord_Scraper:
    """Experimental Discord scraper class."""

    def __init__(self, config = 'config.json'):
        """Class constructor.

        Arguments:
            config (string) -- The config filename.
        """
        with open(config, 'r') as config_file:
            config_data = loads(config_file.read())

        self.headers = {
            'user-agent':    config_data['agent'],
            'authorization': config_data['token']
        }

        self.types = config_data['types']
        self.query = create_query_body(
            images = config_data['query']['images'],
            files  = config_data['query']['files' ],
            embeds = config_data['query']['embeds'],
            links  = config_data['query']['links' ],
            videos = config_data['query']['videos'],
            nsfw   = config_data['query']['nsfw'  ]
        )

        self.directs = config_data['directs']
        self.servers = config_data['servers']
        
    def get_server_name(self, server_id):
        """Get server name by ID.

        Arguments:
            server_id (int) -- The target server ID.

        Returns: string
        """
        try:
            request = Request(self.headers)
            server  = request.grab_page(f'https://discordapp.com/api/v6/guilds/{server_id}')
            
            if len(server) > 0:
                return f"{server_id}_{safe_name(server['name'])}"

            else:
                stderr.write('\nUnable to fetch server name from id, generating one instead.')
                return f"{server_id}_{random_str(12)}"

        except Exception as e:
            stderr.write(f'\nUnable to fetch server name from id, generating one instead. {e}')
            return f"{server_id}_{random_str(12)}"

    def get_channel_name(self, channel_id):
        """Get channel name by ID.

        Arguments:
            channel_id (int) -- The target channel ID.

        Returns: string
        """
        try:
            request = Request(self.headers)
            channel = request.grab_page(f'https://discordapp.com/api/v6/channels/{channel_id}')
            
            if len(channel) > 0:
                return f"{channel_id}_{safe_name(channel['name'])}"
            
            else:
                stderr.write('\nUnable to fetch channel name from id, generating one instead.')
                return f"{channel_id}_{random_str(12)}"
        
        except Exception as e:
            stderr.write('\nUnable to fetch channel name from id, generating one instead.')
            return f"{channel_id}_{random_str(12)}"
        
    def create_folders(self, server, channel):
        """Create the folder structure.

        Arguments:
            server  (string) -- The target server  name
            channel (string) -- The target channel name

        Returns: string
        """
        folder = path.join(getcwd(), 'Discord Scrapes', server, channel)
        if not path.exists(folder):
            makedirs(folder)

        return folder

    def download(self, url, folder):
        """Download the contents of a URL.

        Arguments:
            url    (string) -- The target URL.
            folder (string) -- The target folder.
        """
        try:
            request = Request({
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
            })

            filename = safe_name(f"{url.split('/')[-2]}_{url.split('/')[-1]}")
            filedata = request.grab_page(url, True)

            if len(filedata) > 0:
                with open(path.join(folder, filename), 'wb') as bin:
                    bin.write(filedata)
            
            else:
                stderr.write(f'\nFailed to grab the contents of {url}')

        except Exception as e:
            stderr.write(f'\nUnknown exception: {e} when grabbing from {url}')


    def check_config_mimetypes(self, source, folder):
        """Check the config settings against the source mimetype.

        Arguments:
            source (dict)   -- Response from Discord search.
            folder (string) -- Folder where the data will be stored.
        """
        for attachment in source['attachments']:
            if self.types['images'] == True:
                if mimetype(attachment['url']).split('/')[0] == 'image':
                    self.download(attachment['url'], folder)

            if self.types['videos'] == True:
                if mimetype(attachment['url']).split('/')[0] == 'video':
                    self.download(attachment['url'], folder)
                
            if self.types['files'] == True:
                if mimetype(attachment['url']).split('/')[0] not in ['image', 'video']:
                    self.download(attachment['url'], folder)
    
    def grab_data(self):
        """Scan and grab the attachments within a server."""

        for server in self.servers.keys():
            for channels in self.servers.values():
                for channel in channels:
                    tzdata = gmtime(time())
                    folder = self.create_folders(
                        self.get_server_name(server),
                        self.get_channel_name(channel)
                    )

                    for year in range(tzdata.tm_year, 2015, -1):
                        for month in range(12, 1, -1):
                            for day in range(31, 1, -1):
                                if month >  tzdata.tm_mon and year == tzdata.tm_year: continue
                                if month == tzdata.tm_mon and  day  > tzdata.tm_mday: continue

                                try:
                                    headers = self.headers
                                    headers.update({
                                        'referer': f'https://discordapp.com/channels/{server}/{channel}'
                                    })

                                    today   = get_day(day, month, year)
                                    request = Request(headers)
                                    content = request.grab_page(f"https://discordapp.com/api/v6/guilds/{server}/messages/search?channel_id={channel}&min_id={today['00:00']}&max_id={today['23:59']}&{self.query}")

                                    for messages in content['messages']:
                                        for message in messages:
                                            self.check_config_mimetypes(message, folder)

                                except ValueError: pass
                                except Exception:  pass

#
# Initializer
#

if __name__ == '__main__':
    ds = Discord_Scraper()
    ds.grab_data()
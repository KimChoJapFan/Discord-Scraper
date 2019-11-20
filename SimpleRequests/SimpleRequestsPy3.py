# Give us access to http.client functions for network requests.
from http.client import HTTPConnection, HTTPSConnection, HTTPException

# Give us access to the OS module functions.
from os import makedirs, path

# Give us access to our basic SimpleRequests functions.
from .SimpleRequest import error

# Give us access to the JSON module functions.
from json import loads


# Create a new object to store our URL portions.
class URL(object):
    def __init__(self):
        self.scheme = None
        self.domain = None
        self.path = None


# Split our URLs into the three distinct portions: scheme, domain, and path.
def url_split(url):
    """Split our URLs into an object.

    :param url: The URL we want to split.
    :returns: An object for our spliced URL.
    """

    # Create an array of our URL.
    urlsplices = url.split('/')

    # Combine the portions of our URL array that makes up the path.
    urlpath = f"/{'/'.join(urlsplices[3::])}"

    # Create our URL object.
    url = URL()

    # Set our URL object properties.
    url.scheme = urlsplices[0][:-1]
    url.domain = urlsplices[2]
    url.path = urlpath

    # Return our URL object
    return url


class SimpleRequests:
    """SimpleRequests class for our scraper script."""

    def __init__(self, headers=None):
        """SimpleRequests constructor.

        :param headers: The request headers.
        """

        if headers is None:
            headers = {}

        self.headers = headers

    def set_header(self, name, value):
        """Set an HTTP request header.

        :param name: The name of our header.
        :param value: The value of our header.
        """

        # Set our header.
        self.headers.update({name: value})

    def del_header(self, name):
        """Delete an HTTP request header.

        :param name: The name of our header.
        """

        # Remove the header if it exists in the dictionary.
        if self.headers[name]:
            del self.headers[name]

    def get_response(self, url):
        """Grab the http.client response from a request.

        :param url: The URL of the page.
        """

        # Enclose our file gathering process in a try-catch condition.
        try:

            # Split our URL into the three distinct portions.
            urlsplices = url_split(url)

            # Make a connection to the URL.
            conn = HTTPSConnection(urlsplices.domain) if urlsplices.scheme == 'https' \
                else HTTPConnection(urlsplices.domain)

            # Make a simple request.
            conn.request('GET', urlsplices.path, headers=self.headers)

            # Gather our response.
            resp = conn.getresponse()

            # Return our data if we receive an HTTP 2XX or 3XX response code.
            if 199 < resp.status < 400:
                return resp

            # Otherwise raise an exception for anything else.
            raise HTTPException(f'HTTP {resp.code} {resp.reason}')

        except HTTPException as httpex:

            # Return an error message if we catch an exception.
            error(f'Unknown exception: {httpex}')
            return None

    def stream_file(self, url, filepath, filename, bbuffer=512, usebuffer=True):
        """Grab a file in chunks.

        :param url: The URL of our file.
        :param filepath: The path of our file.
        :param filename: The name of our file.
        :param bbuffer: The amount of data in bytes to stream per second.
        :param usebuffer: Set this to True to stream the file contents.
        """

        # Grab the http.client response.
        resp = self.get_response(url)

        # Skip the whole process if something went wrong.
        if resp is None:
            return False

        # Determine if our file exists.
        if not path.exists(filepath):
            makedirs(filepath)

        # Combine our filepath and filename.
        bfile = path.join(filepath, filename)

        # Gather the filesize of our file.
        filesize = int(resp.getheader('content-length'))

        # Open our file for appending the binary data.
        with open(bfile, 'ab') as filestream:

            # Just write the whole thing if we can't stream it.
            if resp.getheader('accept-ranges') != 'bytes' or not usebuffer:
                filestream.write(resp.read())
                filestream.close()
                return True

            # Initialize our filebuffer variable.
            filebuffer = bbuffer - 1

            # Iterate through the filesize by our buffer.
            for byte in range(0, filesize, bbuffer):

                # Set the byte range header.
                self.set_header('range', f'bytes={byte}-{filebuffer}' if filebuffer < filesize else f'bytes={byte}-')

                # Make another request.
                fres = self.get_response(url)

                # Close the file if something went wrong.
                if fres is None:
                    filestream.close()
                    return False

                # Write the contents of our data to the file.
                filestream.write(fres.read())

                # Increment our filebuffer variable.
                filebuffer += bbuffer

        # Return True if we got to this point.
        return True

    def grab_page(self, url, binary=False):
        """Grab the contents of a page.

        :param url: The URL of our page.
        :param binary: Set this to true for grabbing binary data.
        """

        # Grab the http.client response.
        resp = self.get_response(url)

        # Skip the whole process if something went wrong.
        if resp is None:
            return None

        # Return the contents of the http.client response.
        return resp.read() if binary else loads(resp.read())

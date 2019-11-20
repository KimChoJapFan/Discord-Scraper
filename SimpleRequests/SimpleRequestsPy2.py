# Give us access to the urllib2 functions.
from urllib2 import build_opener, install_opener, urlopen, HTTPError

# Give us access to the OS module functions.
from os import makedirs, path

# Give us access to our basic SimpleRequests functions.
from .SimpleRequest import error

# Give us access to the JSON module functions.
from json import loads


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
        """Grab the urllib2 response from a request.

        :param url: The URL of the page.
        """

        # Enclose our file gathering process in a try-catch condition.
        try:

            # Create an empty array to store our opener headers.
            opener_headers = []

            # Iterate through our headers to put them into their own tuples.
            for key, val in self.headers.items():
                opener_headers.append((key, val.encode('iso-8859-1')))

            # Build our urllib2 opener.
            opener = build_opener()

            # Add our opener headers.
            opener.addheaders = opener_headers

            # Install our opener.
            install_opener(opener)

            # Return our urlopen object.
            return urlopen(url)

        except HTTPError as httperr:

            # Return an error message if we catch an exception.
            error('Unknown exception: HTTP %s %s' % (httperr.code, httperr.reason))
            return None

    def stream_file(self, url, filepath, filename, bbuffer=512, usebuffer=True):
        """Grab a file in chunks.

        :param url: The URL of our file.
        :param filepath: The path of our file.
        :param filename: The name of our file.
        :param bbuffer: The amount of data in bytes to stream per second.
        :param usebuffer: Set this to True to stream the file contents.
        """

        # Grab the urllib2 response.
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
        filesize = int(resp.info().getheader('content-length'))

        # Open our file for appending the binary data.
        with open(bfile, 'ab') as filestream:

            # Just write the whole thing if we can't stream it.
            if resp.info().getheader('accept-ranges') != 'bytes' or not usebuffer:
                filestream.write(resp.read())
                filestream.close()
                return True

            # Initialize our filebuffer variable.
            filebuffer = bbuffer - 1

            # Iterate through the filesize by our buffer.
            for byte in range(0, filesize, bbuffer):

                # Set the byte range header.
                self.set_header('range', 'bytes=%d-%d' % (byte, filebuffer) if filebuffer < filesize else 'bytes=%d-' % byte)

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

        # Grab the urllib2 response.
        resp = self.get_response(url)

        # Skip the whole process if something went wrong.
        if resp is None:
            return None

        # Return the contents of the urllib2 response.
        return resp.read() if binary else loads(resp.read())

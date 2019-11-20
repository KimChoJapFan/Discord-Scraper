#
# Author  : Dracovian (https://github.com/Dracovian)
# Date    : November 20, 2019
# License : WTFPL
# Module  : SimpleRequest
#

# Give us access to the standard output and error streams.
from sys import stderr, version_info


# Create a function to write an error to stderr.
def error(message):
    """Write to stderr.

    :param message: The message we want to write to stderr.
    """

    # Append our message with a newline character.
    stderr.write('%s\n' % message)


# Create our SimpleRequests class
class SimpleRequest(object):
    """ The SimpleRequests class. """

    def __init__(self, headers=None):
        """SimpleRequests constructor."""

        # Determine which version of Python we're running.
        if version_info.major == 3:

            # Import our Python 3 variant of SimpleRequests
            from .SimpleRequestsPy3 import SimpleRequests
            self.request = SimpleRequests(headers)

        elif version_info.major == 2:

            # Import our Python 2 variant of SimpleRequests
            from .SimpleRequestsPy2 import SimpleRequests
            self.request = SimpleRequests(headers)

        else:

            # Throw an error since we're running with an
            #  unsupported version of the Python interpreter.
            error('Invalid version of Python detected!')

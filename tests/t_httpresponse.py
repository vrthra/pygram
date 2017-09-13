from httplib import HTTPResponse
from StringIO import StringIO
import helpers, induce

http_response_str = helpers.slurparg()

class FakeSocket():
    def __init__(self, response_str):
        self._file = StringIO(response_str)
    def makefile(self, *args, **kwargs):
        return self._file

with induce.grammar() as g:
   with induce.Tracer(http_response_str, g):
      source = FakeSocket(http_response_str)
      response = HTTPResponse(source)
      response.begin()
      print "status:", response.status
      print "single header:", response.getheader('Content-Type')
      print "content:", response.read(len(http_response_str)) # the len here will give a 'big enough' value to read the whole content


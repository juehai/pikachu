from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import defer
from twisted.internet.threads import deferToThread
from twisted.python.failure import Failure

class HelloService(Resource):
    isLeaf = True
    serviceName = "hello"

    def __init__(self, c, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.config = c

    def prepare(self, request):
        pass

    def finish(self, value, request):
        #request.setHeader('Content-Type', 'application/xhtml+xml; charset=UTF-8')
        request.setHeader('Content-Type', 'text/html; charset=UTF-8')
        if isinstance(value, Failure):
            err = value.value
            request.setResponseCode(500)
            #error = dict(error="generic", message=str(err))
            #request.write(json_encode(error) + "\n")
            error = str(err)
            request.write(error + "\n")
        else:
            request.setResponseCode(200)
            request.write(value + "\n")
        request.finish()

    def cancel(self, err, call):
        call.cancel()

    def render_GET(self, request):
        d = defer.Deferred()
        request.notifyFinish().addErrback(self.cancel, d)
        d.callback("<html><body><p>Hello World! It works.</p></body></html>")
        d.addBoth(self.finish, request)
        return NOT_DONE_YET

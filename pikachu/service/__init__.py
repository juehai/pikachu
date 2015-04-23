from twisted.web import resource
from pikachu.service.hello import HelloService

__all__ = ['site_configure']


def site_configure(c):
    root = resource.Resource()
    root.putChild(HelloService.serviceName, HelloService(c))
    return root

from twisted.web import resource
from pikachu.service.hello import HelloService
from pikachu.service.internal import InternalService, AccessTokenService

__all__ = ['site_configure']


def site_configure(c):
    root = resource.Resource()
    # internal branch
    internal_branch = InternalService(c)
    internal_branch.putChild(AccessTokenService.serviceName, AccessTokenService(c))

    # root nodes
    root.putChild(HelloService.serviceName, HelloService(c))
    root.putChild(InternalService.serviceName, internal_branch)

    return root

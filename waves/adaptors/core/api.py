from __future__ import unicode_literals

from waves.adaptors.core.adaptor import JobAdaptor


class PublicApiAdaptor(JobAdaptor):
    """ Base Class for remote public API calls"""
    def __init__(self, command=None, protocol='http', host="localhost", port='', api_base_path='', api_endpoint='',
                 **kwargs):
        super(PublicApiAdaptor, self).__init__(command, protocol, host, **kwargs)
        self.port = port
        self.api_endpoint = api_endpoint
        self.api_base_path = api_base_path

    @property
    def init_params(self):
        base = super(PublicApiAdaptor, self).init_params
        base.update(dict(port=self.port,
                         api_base_path=self.api_base_path,
                         api_endpoint=self.api_endpoint))
        return base

    @property
    def complete_url(self):
        """ Create complete url string for remote api"""
        url = "%s://%s" % (self.protocol, self.host)
        if self.port != '':
            url += ':%s' % self.port
        if self.api_base_path != '':
            url += '/%s' % self.api_base_path
        if self.api_endpoint != '':
            url += '/%s' % self.api_endpoint
        return url

    def connexion_string(self):
        return self.complete_url


class ApiKeyAdaptor(PublicApiAdaptor):
    """
    Authenticated api calls
    """
    _api_get_key = 'app_key'

    def __init__(self, command=None, protocol='http', host="localhost", port='', api_base_path='', api_endpoint='',
                 app_key=None, **kwargs):
        super(ApiKeyAdaptor, self).__init__(command, protocol, host, port, api_base_path, api_endpoint, **kwargs)
        self.app_key = app_key

    @property
    def complete_url(self):
        url = super(ApiKeyAdaptor, self).complete_url()
        url += '?%s=%s' % (self._api_get_key, self.app_key)
        return url

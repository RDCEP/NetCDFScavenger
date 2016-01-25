from scrapy.http.response.html import HtmlResponse
from scrapy.exceptions import IgnoreRequest
from scrapy import log
import re

class FilterResponses(object):
    """Limit the HTTP response types that Scrapy dowloads."""

    @staticmethod
    def is_valid_response(type_whitelist, content_type_header):
        for type_regex in type_whitelist:
            if re.search(type_regex, content_type_header):
                return True
        return False

    def process_response(self, request, response, spider):
        """
        Only allow HTTP response types that that match the given list of 
        filtering regexs
        """
        # each spider must define the variable response_type_whitelist as an
        # iterable of regular expressions. ex. (r'text', )
        type_whitelist = getattr(spider, "response_type_whitelist", None)
        content_type_header = response.headers.get('content-type', None)
        if not type_whitelist:
            return response
        elif not content_type_header:
            log.msg("no content type header: {}".format(response.url), level=log.DEBUG, spider=spider)
            raise IgnoreRequest()
        elif self.is_valid_response(type_whitelist, content_type_header):
            log.msg("valid response {}".format(response.url), level=log.DEBUG, spider=spider)
            return response
        else:
            msg = "Ignoring request {}, content-type was not in whitelist".format(response.url)
            log.msg(msg, level=log.DEBUG, spider=spider)
            raise IgnoreRequest()

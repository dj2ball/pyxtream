
# Import Flask to control IPTV via REST API
try:
    from flask import Flask
    from flask import Response as FlaskResponse
    from flask import request as FlaskRequest
    from threading import Thread
except:
    pass

class EndpointAction(object):

    def __init__(self, action, function_name):
        self.function_name = function_name
        self.action = action

    def __call__(self, **args):
        
        if args != {}:
            if self.function_name == "stream_search":
                regex_term = r"^.*{}.*$".format(args['term'])
                answer = self.action(regex_term,'JSON')
            elif self.function_name == "download_stream":
                answer = self.action(int(args['stream_id']))
            else:
                print(args)
                answer = "Hello"
            self.response = FlaskResponse(answer, status=200, headers={})
            self.response.headers["Content-Type"] = "text/json; charset=utf-8"
        else:
            answer = self.action
            self.response = FlaskResponse(answer, status=200, headers={})
            self.response.headers["Content-Type"] = "text/html; charset=utf-8"

        return self.response

class FlaskWrap(Thread):

    home_template = """
<!DOCTYPE html><html lang="en"><head></head><body>pyxtream API</body></html>
    """

    def __init__(self, name, xtream: object, home_html_template: str = None):

        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        self.app = Flask(name)
        self.xt = xtream
        Thread.__init__(self)
        
        # Configure Thread
        self.setName("pyxtream REST API")
        self.daemon = True

        # Load HTML Home Template if any
        if home_html_template != None:
            self.home_template = home_html_template

        # Add all endpoints
        self.add_endpoint(endpoint='/', endpoint_name='home', handler=[self.home_template,""])
        self.add_endpoint(endpoint='/stream_search/<term>', endpoint_name='stream_search', handler=[self.xt.search_stream,"stream_search"])
        self.add_endpoint(endpoint='/download_stream/<stream_id>/', endpoint_name='download_stream', handler=[self.xt.download_video,"download_stream"])

    def run(self):
        self.app.run(debug=True, use_reloader=False)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(*handler))

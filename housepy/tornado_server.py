#!/usr/bin/env python

import os, re, filters, strings, datetime, hashlib, oauth2, __main__
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
import json as jsonlib
import jinja2
from jinja2 import Environment, FileSystemLoader
from housepy import config, log

class Application(tornado.web.Application):
    
    def __init__(self, handlers):
                
        settings = {
            'template_path': os.path.abspath(os.path.join(os.path.dirname(__main__.__file__), "templates")),
            'static_path': os.path.abspath(os.path.join(os.path.dirname(__main__.__file__), "static"))
        }
        
        if 'tornado' in config:
            tornado_settings = config['tornado']
            for key in tornado_settings.keys():
                settings[key] = tornado_settings[key]        

        tornado.web.Application.__init__(self, handlers, **settings)
        
        if 'mysql' in config:
            log.info("--> tornado initializing mysql")
            import database
            try:
                self.db = database.Connection()
            except Exception as e:
                log.error("Could not connect to MySQL: %s" % log.exc(e))   
        elif 'mongo' in config:    
            log.info("--> tornado initializing mongo")
            try:
                mongo = config['mongo']
                import pymongo                
                connection = pymongo.Connection(mongo['host'])
                self.db = connection[mongo['database']]
            except Exception as e:
                log.error("Could not connect to mongo: %s" % log.exc(e))
        if 'redis' in config:
            log.info("--> tornado initializing redis")
            import redis
            self.redis = redis.StrictRedis()
        if 'memcache' in config:
            log.info("--> torando initializing memcache")
            import memcache
            self.cache = memcache.Client([config['memcache']['address'] + ":" + str(config['memcache']['port'])])
            
        self.jobs = None    
        if 'beanstalk' in config:    
            log.info("--> tornado initializing beanstalk")
            import jobs
            self.jobs = jobs.Jobs()  
            
        # intialize oauth server
        try:
            self.oauth_server = oauth2.Server(signature_methods={'HMAC-SHA1': oauth2.SignatureMethod_HMAC_SHA1()})                                                    
        except ImportError:
            self.oauth_server = None
            
        Application.instance = self          
        
    def log_request(self, handler):
        """Writes a completed HTTP request to the logs."""
        if handler.get_status() < 400:
            log_method = log.info
        elif handler.get_status() < 500:
            log_method = log.warning
        else:
            log_method = log.error
        request_time = 1000.0 * handler.request.request_time()
        if 'verbose' in config['tornado'] and config['tornado']['verbose']:            
            log_method("%d (%s) %s %s %.2fms", handler.get_status(), handler.request.remote_ip, handler.request.method, handler.request.uri, request_time)
    
        
class render_jinja:

    def __init__(self, *a, **kwargs):
        extensions = kwargs.pop('extensions', [])
        globals = kwargs.pop('globals', {})

        self._lookup = Environment(loader=FileSystemLoader(*a, **kwargs), extensions=extensions)
        self._lookup.globals.update(globals)

    def __getitem__(self, name):
        t = self._lookup.get_template(name)
        return t.render
                       


class Handler(tornado.web.RequestHandler):
    """Adding custom output methods.""" 
    
    def initialize(self):
        log.info("---------- %s %s %s" % (self.request.remote_ip, self.request.method, self.request.uri))
        self.xsrf_form_html()    
        
    def get_current_user(self): # supports tornado auth
       return self.get_secure_cookie("user") 

    @property
    def user(self):
        try:
            return jsonlib.loads(self.get_secure_cookie('user'))
        except:
            return None
    
    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    @property
    def cache(self):
        return self.application.cache
        
    @property
    def jobs(self):
        return self.application.jobs    
        
    @property
    def oauth_server(self):    
        return self.application.oauth_server                
                        
    def render(self, template_name, template_values=None, **kwargs):      # using jinja2 templates instead of tornados to keep consistency
        if type(template_values) == dict:
            template_values.update(kwargs)
        else:
            template_values = kwargs
        template_values['uri'] = self.request.uri
        if 'log_templates' in config['tornado'] and config['tornado']['log_templates']:    
            log.info("TEMPLATE %s: %s" % (template_name, template_values))
        else:    
            log.info("TEMPLATE %s" % template_name)            
        for key in config: 
            if type(config[key]) is list and 0 in config[key] and type(config[key][0]) is dict:
                for param in config[key][0]:
                    template_values[key + "_" + param] = str(config[key][0][param])
            else:
                template_values[key] = config[key]                       
        template_values['template_name'] = template_name                         
        if 'user' not in template_values:
            template_values['user'] = self.user
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__main__.__file__), "templates"))
        renderer = render_jinja(template_dir)
        renderer._lookup.filters.update(filters.filters)
        output = (renderer[template_name](template_values)).encode('utf-8')
        suffix = strings.suffix('.', template_name)
        if suffix == "html":
            self.html(output)
        else:
            self.text(output)          
        
    def json(self, data, filename=False):
        try:
            import numpy as np
        except Exception:    
            output = jsonlib.dumps(data, indent=4, default=lambda obj: str(obj))               
        else:    
            output = jsonlib.dumps(data, indent=4, default=lambda obj: str(obj) if type(obj) != np.ndarray else list(obj))
        self.set_header("Content-Type", "text/plain")
        if filename:
            self.set_header("Content-Disposition", "attachment; filename=%s" % filename)
        self.write(output)
        log.info("200 text/plain (JSON)")

    def xml(self, xml, filename=False):    
        self.set_header("Content-Type", "application/xml")
        if filename:
            self.set_header("Content-Disposition", "attachment; filename=%s" % filename)
        self.write(xml)
        log.info("200 application/xml")                            

    def html(self, html):
        self.set_header("Content-Type", "text/html")
        self.write(html)    
        log.info("200 text/html")                

    def text(self, string):
        self.set_header("Content-Type", "text/plain")
        self.write(string)
        log.info("200 text/plain")            

    def csv(self, string, filename):
        self.set_header("Content-Type", "text/csv")
        self.set_header("Content-Disposition", "attachment; filename=%s" % filename)
        self.write(string)
        log.info("200 text/csv")    

    def file(self, filename):
        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition", "attachment; filename=%s" % filename.split('/')[-1])
        self.set_header("Content-Length", "%s" % os.path.getsize(filename))    
        self.write(open(filename, 'r').read())
        log.info("200 application/octet-stream (%s)" % filename)        

    def image(self, image):
        import imaging
        self.set_header("Content-Type", "image/png")
        self.set_header("Expires", "Thu, 15 Apr 2050 20:00:00 GMT")
        if type(image) != str:
            image = imaging.to_string(image)            
        self.write(image)
        log.info("200 image/png")            

    def temp_image(self, image):
        import imaging
        self.set_header("Content-Type", "image/png")     
        self.set_header("Cache-Control", "no-cache")
        if type(image) != str:
            image = imaging.to_string(image)                    
        self.write(image)
        log.info("200 image/png (temporary)")            

    def error(self, message="Error"):
        self.set_header("Status", "400 Bad Request")
        self.write("400: %s" % message)
        log.error("400: %s" % message)
        self.send_error(400, message=message)

    def not_found(self):
        log.warning("404: Page not found")
        raise tornado.web.HTTPError(404)        
        
    def get_error_html(self, status_code, message="Error", **kwargs):
        if status_code == 404:
            message = "Not found"
        return "%(code)d: %(message)s" % {"code": status_code, "message": message} 
        
    def redirect(self, url):
        log.info("--> redirecting to %s" % url)
        tornado.web.RequestHandler.redirect(self, url)                   


def start(handlers):
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__main__.__file__), "templates"))
    if not os.path.isdir(template_dir):
        os.makedirs(template_dir)
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__main__.__file__), "static"))
    if not os.path.isdir(static_dir):
        os.makedirs(static_dir)    
    tornado.options.logging = "none"
    ssl_options = None
    if 'ssl_options' in config['tornado']:
        ssl_options = {'certfile': config['tornado']['ssl_options']['certfile'], 'keyfile': config['tornado']['ssl_options']['keyfile']}
    log.info("Starting tornado server on port %s" % config['tornado']['port'])
    http_server = tornado.httpserver.HTTPServer(Application(handlers), ssl_options=ssl_options, xheaders=True)
    http_server.listen(config['tornado']['port'])
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":

    from controllers.home import Home
    handlers = [
        (r"/", Home),
    ]    
    start(handlers)

import util, datetime, strings, urllib

def strslice(s, length):
    if not isinstance(s, basestring):
        s = str(s)
    return s[:length]

def good_decimal(num):
    return util.good_decimal(num)
    
def good_datetime(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)        
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def good_time(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)        
    return dt.strftime("%H:%M:%S")
    
def zfill(num, digits=3):
    return str(num).zfill(digits)

def strip_html(s):
    return strings.strip_html(s)

def linkify(text, extra_params=""):
    from tornado.escape import linkify
    return linkify(text, extra_params=extra_params)    

def nl2br(s):
    return '<br />'.join(s.splitlines())       

def slugify(s):
    return strings.slugify(s)

def urlencode(s):    
    return urllib.quote(strings.safestr(s))

filters = {'strslice': strslice, 'good_decimal': good_decimal, 'good_datetime': good_datetime, 'good_time': good_time, 'zfill': zfill, 'strip_html': strip_html, 'linkify': linkify, 'nl2br': nl2br, 'slugify': slugify, 'urlencode': urlencode}


# built-in filters I like:
#
# int
# e (html escape)
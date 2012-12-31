""" Utilities that dont fit in other modules
"""

from log import log

def num_args(f):
    """Returns the number of arguments received by the given function"""
    import inspect
    return len(inspect.getargspec(f).args)  
    
def smooth(_l, n=1):
    """Smooths the values in a list n times. You probably should be using housepy.science. Are the functions equivalent?"""
    l = list(_l)
    for t in range(n):
        for i in range(1, len(l) - 1):
            l[i] = (l[i - 1] + l[i] + l[i + 1]) / 3.0
    return l

def fake_file(data):
    """Writes data to a StringIO object and returns the pointer"""
    import cStringIO
    f = cStringIO.StringIO()
    f.write(data)
    f.seek(0)
    return f
    
def dictsort(value, arg):
    """Takes a list of dicts, returns that list sorted by the property given in the argument."""
    decorated = [(resolve_variable('var.' + arg, {'var' : item}), item) for item in value]
    decorated.sort()
    return [item[1] for item in decorated]
    
def format_time(seconds):
    """Return a string formatted with colons from a seconds value"""
    if type(seconds) != int:
        seconds = float(seconds)
    minutes = int(seconds // 60)
    seconds = seconds - (minutes * 60)        
    hours = minutes // 60
    minutes = minutes - (hours * 60)        
    days = int(hours // 24)
    hours = int(hours - (days * 24))
    
    time = []
    if days:
        time.append("%s:" % days)
    if hours or days:
        time.append("%s:" % str(hours).zfill(2))
    if minutes or hours or days:
        time.append("%s:" % str(minutes).zfill(2))
    if type(seconds) == int:    
        if not minutes and not hours and not days:
            time.append(":%s" % str(seconds).zfill(2))        
        elif seconds or minutes or hours or days:
            time.append("%s" % str(seconds).zfill(2))
    else:
        if not minutes and not hours and not days:
            time.append(":%s" % str("%f" % seconds).zfill(2))        
        elif seconds or minutes or hours or days:
            time.append("%s" % str("%f" % seconds).zfill(2))
    time = "".join(time)
               
    return time

def to_utc(dt, tz="America/New_York"):
    import pytz
    local = pytz.timezone(tz)
    dt = local.localize(dt)
    dt = dt.astimezone(pytz.utc)
    return dt
    
def good_decimal(num):
    """Returns a string with exact rounded decimals from a float"""
    from decimal import Decimal
    return str(Decimal(str(num)).quantize(Decimal('.01')))    
    
def is_int(num):
    """Return True if the value is an int"""
    try:
        int(num)
    except Exception:
        return False
    else:
        return True
        
def write_file(filename, content, binary=False):
    import codecs
    mode = 'wb' if binary else 'w'
    f = codecs.open(filename, mode, 'utf-8')
    f.write(content)
    f.close()    
    
def soup(string, **kwargs):
    """Create a BeautifulSoup parse object from a string"""
    from lib.BeautifulSoup import BeautifulSoup    
    return BeautifulSoup(string, **kwargs)
    
def parse_date(string):
    """Return a datetime with a best guess of the supplied string, using dateutil"""
    from lib.dateutil import parser
    try:
        dt = parser.parse(string)
    except ValueError, e:
        log.warning(e)
        dt = None
    return dt
    
def geohash_encode(pt):
    """Geohash a point (lon, lat)"""
    from lib import geohash
    return geohash.encode(pt[1], pt[0])
    
def geohash_decode(string):
    """Decode a geohash into a point (lon, lat)"""
    from lib import geohash
    return geohash.decode(string)
    
def chunk(l, size):    
    def ck(l, size):
        for i in xrange(0, len(l), size):
            yield l[i:i + size] 
    return list(ck(l, size))

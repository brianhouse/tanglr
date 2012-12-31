import re
from log import log

def wordcount(s):
    return len(s.split())
        
def filesizeformat(bytes):
    """Format the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB, 102
        bytes, etc).
    """
    try:
        bytes = float(bytes)
    except TypeError:
        return "0 bytes"
    if bytes < 1024:
        return "%d byte%s" % (bytes, bytes != 1 and 's' or '')
    if bytes < 1024 * 1024:
        return "%.1f KB" % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return "%.1f MB" % (bytes / (1024 * 1024))
    return "%.1f GB" % (bytes / (1024 * 1024 * 1024))
            
def strip_html(s, keep_links=False):
    if keep_links:
        s = re.sub(r'</[^aA].*?>', '', s) 
        s = re.sub(r'<[^/aA].*?>', '', s)        
        return s
    else:    
        return re.sub(r'<.*?>', '', s)        
    
def singlespace(s): 
    p = re.compile(r'\s+')
    return p.sub(' ', s)    
    
def remove_linebreaks(s):
    s = s.splitlines()
    s = ' '.join(s)
    return singlespace(s).strip()
    
def depunctuate(s, exclude=None, replacement=''):
    import string
    p = string.punctuation
    if exclude:
        for c in exclude:
            p = p.replace(c, '')    
    regex = re.compile('[%s]' % re.escape(p))
    return regex.sub(replacement, s) 

def nl2br(s):
    return '<br />'.join(s.splitlines())       

def br2nl(s):
    return '\n'.join(s.split('<br />'))     
    
def prefix(delim, s):
    return s.split(delim)[0]
    
def suffix(delim, s):
    return s.split(delim)[-1]
        
def location_cap(location):
    if not location:
        return None
    tokens = location.split(',')
    for token in tokens:    
        t = [i.title() if len(i) > 2 and i.upper() != "USA" else i.upper() for i in token.split(' ')]
        tokens[tokens.index(token)] = ' '.join(t)   
    return ','.join(tokens)

def pluralize(value, arg='s'):
    """Returns a plural suffix if the value is not 1, for '1 vote' vs. '2 votes'
        By default, 's' is used as a suffix; if an argument is provided, that string
        is used instead. If the provided argument contains a comma, the text before
        the comma is used for the singular case.
    """
    if not ',' in arg:
        arg = ',' + arg
    bits = arg.split(',')
    if len(bits) > 2:
        return ''
    singular_suffix, plural_suffix = bits[:2]
    try:
        if int(value) != 1:
            return plural_suffix
    except ValueError: # invalid string that's not a number
        pass
    except TypeError: # value isn't a string or a number; maybe it's a list?
        try:
            if len(value) != 1:
                return plural_suffix
        except TypeError: # len() of unsized object
            pass
    return singular_suffix

def slugify(value):
    """Converts to lowercase, removes non-alpha chars and converts spaces to underscores"""
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[\s]+', '_', value)

def unslugify(value):
    value = value.replace('_', ' ')
    return titlecase(value)

def random_string(length=64):
    import random
    rs = []
    for i in xrange(length):
        rs.append(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"))
    return ''.join(rs)        
    
def safeuni(s):
    if isinstance(s, unicode):
        return s
    if not isinstance(s, basestring):
        if hasattr(obj, '__unicode__'):
            return unicode(s)
        else:
            return str(s).decode('utf-8')
    try:
        s = unicode(s, errors='strict', encoding='utf-8')   # unicode() is expecting a utf-8 bytestring (unicode itself is not utf-8 or anything else)
    except UnicodeDecodeError, e:
        log.warning(e)
        s = unicode(s, errors='ignore', encoding='utf-8')   # dump anything that doesnt make sense in utf-8
    return s

def safestr(s):
    if isinstance(s, str):
        return s
    if isinstance(s, unicode):
        try:
            s = s.encode('utf-8')   
        except UnicodeEncodeError, e:
            log.error(log.exc(e))
            return ""
        return s
    return str(s)

def titlecase(value):
    """Converts a string into titlecase
    """
    return re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), value.title())
    
def unescape_xml(text):
    text = text.replace('&amp;', '&')     
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')        
    text = text.replace('&gt;', '>')
    text = text.replace('&quot', '"')
    text = text.replace('&#39;', "'")
    return text
    
def linkify(text, extra_params=""):
    from tornado.escape import linkify
    return linkify(text, extra_params=extra_params)
    
def remove_non_ascii(s):        
    return "".join(i for i in s if ord(i) < 128)    
    
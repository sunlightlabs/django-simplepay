from urllib import quote
import datetime
import urllib2

def _quote_encode_dict(d):
    return "&".join("%s=%s" % (k, quote(v).replace('/', '%2F')) for k, v in d.iteritems())

def generate_signature():
    pass

def is_valid_signature(qs, endpoint):
    
    if isinstance(qs, dict):
        qs = _quote_encode_dict(qs)
    
    now = datetime.datetime.utcnow()
    
    params = {
        'UrlEndPoint': endpoint,
        'HttpParameters': qs,
        'Action': 'VerifySignature',
        'Timestamp': now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        'Version': '2008-09-17',
    }
    
    try:
        urllib2.urlopen("https://fps.amazonaws.com/?%s" % _quote_encode_dict(params)).read()
        return True
    except urllib2.HTTPError:
        return False
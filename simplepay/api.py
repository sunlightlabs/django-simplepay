from urllib import quote
import datetime
import urllib2

def _quote_encode_dict(d):
    return "&".join("%s=%s" % (k, quote(v)) for k, v in d.iteritems())

def generate_signature():
    pass

def is_valid_signature(params, endpoint):
    
    now = datetime.datetime.utcnow()
    
    params = {
        'UrlEndPoint': endpoint,
        'HttpParameters': _quote_encode_dict(params),
        'Action': 'VerifySignature',
        'Timestamp': now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        'Version': '2008-09-17',
    }
    
    qs = _quote_encode_dict(params)
    print urllib2.urlopen("https://fps.sandbox.amazonaws.com/?%s" % qs).read()
    
    return False
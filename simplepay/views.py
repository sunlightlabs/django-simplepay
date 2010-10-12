from django.http import HttpResponse
from simplepay import ACCESS_KEY, SECRET_KEY, HOST, PATH
from simplepay.models import SimplePayButton
from urllib import quote
import datetime
import json
import urllib2

def _quote_encode_dict(d):
    return "&".join("%s=%s" % (k, quote(v)) for k, v in d.iteritems())

def button(request, button_id):
    
    btn = SimplePayButton.objects.get(pk=int(button_id)).get_real_obj()
    form_class = btn.get_form_class()
    form_data = btn.as_formdata()
    
    if 'amount' in request.GET:
        form_data['amount'] = request.GET['amount']
        
    form = form_class(form_data)
    form.generate_signature()
    
    if not form.is_valid():
        pass
        
    return HttpResponse(json.dumps(form.cleaned_data), content_type="application/json")

def ipn(request, reference_id=None):
    
    now = datetime.datetime.utcnow()
    
    params = {
        'UrlEndPoint': request.build_absolute_uri(),
        'HttpParameters': _quote_encode_dict(request.POST),
        'Action': 'VerifySignature',
        'Timestamp': now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        'Version': '2008-09-17',
        # 'Signature': 'null',
        # 'SignatureVersion': '2',
        # 'SignatureMethod': 'HmacSHA256',
        # 'AWSAccessKeyId': ACCESS_KEY,
    }
    
    qs = _quote_encode_dict(params)
    print urllib2.urlopen("https://fps.sandbox.amazonaws.com/?%s" % qs).read()
    
    return HttpResponse('blah')
    
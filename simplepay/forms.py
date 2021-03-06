from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from simplepay import HOST, PATH, ACCESS_KEY, SECRET_KEY
from urllib import quote
import base64
import hashlib
import hmac
import uuid

EXCLUDE_FROM_SIGNATURE = ('signature',)

class SignatureField(forms.CharField):
    
    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = forms.HiddenInput
        super(SignatureField, self).__init__(*args, **kwargs)

class SimplePayForm(forms.Form):
    abandonUrl = forms.URLField(widget=forms.HiddenInput, required=False, verify_exists=False)
    accessKey = forms.CharField(widget=forms.HiddenInput)
    amount = forms.CharField()
    cobrandingStyle = forms.CharField(widget=forms.HiddenInput, required=False)
    collectShippingAddress = forms.CharField(widget=forms.HiddenInput, required=False)
    description = forms.CharField(widget=forms.HiddenInput)
    immediateReturn = forms.CharField(widget=forms.HiddenInput, required=False)
    ipnUrl = forms.URLField(widget=forms.HiddenInput, required=False, verify_exists=False)
    processImmediate = forms.CharField(widget=forms.HiddenInput)
    referenceId = forms.CharField(widget=forms.HiddenInput, required=False)
    returnUrl = forms.URLField(widget=forms.HiddenInput, required=False, verify_exists=False)
    signature = SignatureField(required=False)
    signatureMethod = forms.CharField(widget=forms.HiddenInput)
    signatureVersion = forms.CharField(widget=forms.HiddenInput)
    
    def __init__(self, data=None, **kwargs):
        
        defaults = {
            'accessKey': ACCESS_KEY,
            'processImmediate': '1',
            'signatureMethod': 'HmacSHA256',
            'signatureVersion': '2',
        }
        defaults.update(data or {})
        
        if not defaults.get('referenceId', None):
            defaults['referenceId'] = uuid.uuid4().hex
        
        super(SimplePayForm, self).__init__(defaults, **kwargs)
    
    def generate_signature(self):
        
        values = []
        for field in sorted(self, cmp=lambda x, y: cmp(x.name, y.name)):
            if field.name not in EXCLUDE_FROM_SIGNATURE:
                if field.data:
                    values.append("%s=%s" % (field.name, quote(str(field.data) or '').replace('/', '%2F')))
                else:
                    del self.fields[field.name]
        
        to_sign = 'POST\n%s\n%s\n%s' % (HOST, PATH, "&".join(values))
        sig = base64.encodestring(hmac.new(SECRET_KEY, to_sign, hashlib.sha256).digest()).strip()
        
        self.data['signature'] = sig
    
    def set_urls(self, request):
        
        ref_id = self.data['referenceId']
        
        self.data['abandonUrl'] = request.build_absolute_uri(
            reverse('simplepay_abandon', args=[ref_id]))
        self.data['ipnUrl'] = request.build_absolute_uri(
            reverse('simplepay_ipn', args=[ref_id]))
        self.data['returnUrl'] = request.build_absolute_uri(
            reverse('simplepay_complete', args=[ref_id]))
        
        return self
        

class PaymentForm(SimplePayForm):
    pass
    
class DonationForm(SimplePayForm):
    donationType = forms.CharField(widget=forms.HiddenInput, required=False)
    isDonationWidget = forms.CharField(widget=forms.HiddenInput)
    minimumDonationAmount = forms.CharField(widget=forms.HiddenInput, required=False)
    
    def __init__(self, data=None, *args, **kwargs):
        data = data or {}
        data['isDonationWidget'] = '1'
        super(DonationForm, self).__init__(data, *args, **kwargs)
    
    # minimumDonationAmount is required if donationType is minimumAmount

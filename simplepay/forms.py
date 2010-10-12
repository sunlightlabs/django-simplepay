from django import forms
from django.conf import settings
from simplepay import HOST, PATH, ACCESS_KEY, SECRET_KEY
from urllib import quote
import base64
import hashlib
import hmac

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
        super(SimplePayForm, self).__init__(defaults, **kwargs)
    
    def generate_signature(self):
        
        values = []
        for field in sorted(self, cmp=lambda x, y: cmp(x.name, y.name)):
            if field.name not in EXCLUDE_FROM_SIGNATURE:
                if field.data:
                    values.append("%s=%s" % (field.name, quote(field.data or '')))
                else:
                    del self.fields[field.name]
        
        to_sign = 'POST\n%s\n%s\n%s' % (HOST, PATH, "&".join(values))
        sig = base64.encodestring(hmac.new(SECRET_KEY, to_sign, hashlib.sha256).digest()).strip()
        
        self.data['signature'] = sig
        

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

# 
# class IpnForm(forms.Form):
#     buyerName = forms.CharField()
#     operation = forms.CharField()
#     paymentMethod = forms.CharField()
#     paymentReason = forms.CharField()
#     recipientEmail = forms.CharField(required=False)
#     recipientName = forms.CharField()
#     referenceId = forms.CharField(required=False)
#     signature = forms.CharField()
#     status = forms.CharField()
#     transactionAmount = forms.CharField()
#     transactionDate = forms.CharField()
#     transactionId = forms.CharField()
#     
#     def verify_signature(self):
#         pass
    
from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from simplepay.forms import PaymentForm, DonationForm

def index(request):
    
    dform = DonationForm({
        'amount': '23.30',
        'description': 'donation to Sunlight Foundation',
    })
    dform.generate_signature()
    
    pform = PaymentForm({
        'amount': '23.30',
        'description': 'donation to Sunlight Foundation',
    })
    pform.generate_signature()
    
    return render_to_response('simplepay/test.html', {'pform': pform, 'dform': dform})

urlpatterns = patterns('simplepay.views',
    url(r'^button/(?P<button_id>\d+)/$', 'button'),
    url(r'^$', index),
)
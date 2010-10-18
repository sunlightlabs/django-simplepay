from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.shortcuts import render_to_response
from simplepay import api
from simplepay.forms import DonationForm, PaymentForm
from simplepay.models import DonationButton, PaymentButton, SimplePayButton, Transaction
from urllib import quote

def index(request):
    
    forms = []
    for txn in Transaction.objects.all():
        form = txn.get_form()
        form.set_urls(request)
        form.generate_signature()
        forms.append(form)
    
    return render_to_response('simplepay/test.html', {'forms': forms})

urlpatterns = patterns('simplepay.views',
    url(r'^button/(?P<button_id>\d+)/$', 'button'),
    url(r'^(?P<reference_id>\w{32})/$', 'complete', name='simplepay_complete'),
    url(r'^(?P<reference_id>\w{32})/abandon/$', 'abandon', name='simplepay_abandon'),
    url(r'^(?P<reference_id>\w{32})/ipn/$', 'ipn', name='simplepay_ipn'),
    url(r'^$', index),
)
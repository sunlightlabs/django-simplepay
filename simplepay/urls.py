from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from simplepay.forms import DonationForm, PaymentForm
from simplepay.models import DonationButton, PaymentButton, SimplePayButton

def index(request):
    
    forms = []
    for btn in SimplePayButton.objects.all():
        form = btn.get_form()
        form.generate_signature()
        forms.append(form)
        print form
    
    return render_to_response('simplepay/test.html', {'forms': forms})

urlpatterns = patterns('simplepay.views',
    url(r'^button/(?P<button_id>\d+)/$', 'button'),
    url(r'^ipn/(?P<reference_id>\d+)/$', 'ipn'),
    url(r'^ipn/$', 'ipn'),
    url(r'^$', index),
)
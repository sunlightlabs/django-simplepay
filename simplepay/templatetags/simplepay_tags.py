from django import template
from django.forms import Form
from django.template.loader import render_to_string
from simplepay import HOST, PATH
from simplepay.forms import SimplePayForm, PaymentForm, DonationForm

register = template.Library()

@register.simple_tag
def simplepay_form(obj):
    
    if hasattr(obj, 'get_form'):
        obj = obj.get_form()
    
    if isinstance(obj, DonationForm):
        return _render_form(obj, 'simplepay/form_donation.html')
    elif isinstance(obj, PaymentForm):
        return _render_form(obj, 'simplepay/form_payment.html')

def _render_form(form, template):
    return render_to_string(template, {
        'form': form,
        'host': HOST,
        'path': PATH,
    })
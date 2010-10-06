from django import template
from django.template.loader import render_to_string
from simplepay import HOST, PATH
from simplepay.forms import PaymentForm, DonationForm

register = template.Library()

@register.simple_tag
def donation_form(form):
    if not isinstance(form, DonationForm):
        raise ValueError('DonationForm is required')
    return _render_form(form, 'simplepay/form_donation.html')
    
@register.simple_tag
def payment_form(form):
    if not isinstance(form, PaymentForm):
        raise ValueError('PaymentForm is required')
    return _render_form(form, 'simplepay/form_payment.html')

def _render_form(form, template):
    return render_to_string(template, {
        'form': form,
        'host': HOST,
        'path': PATH,
    })
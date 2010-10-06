from decimal import Decimal
from django.db import models
from simplepay.forms import DonationForm, PaymentForm
import uuid

COBRANDING_STYLES = [(s, s) for s in ('logo','banner')]
DONATION_TYPES = (
    ('fixedAmount', 'Fixed Amount'),
    ('minimumAmount', 'Minimum Amount'),
    ('anyAmount', 'Any Amount'),
)
TRANSACTION_STATUSES = (
    ('pending', 'Pending'),
    ('complete', 'Complete'),
    ('cancelled', 'Cancelled'),
    ('failed', 'Failed'),
)
EXCLUDED_FIELDS = ('id','simplepaybutton_ptr')

def camelcase(s):
    parts = s.split('_')
    return unicode(parts[0] + "".join(s.title() for s in parts[1:]))

def coerce_type(v):
    if isinstance(v, bool):
        return u'1' if v else u'0'
    elif isinstance(v, Decimal):
        return u"%s" % v
    else:
        return v

class CurrencyField(models.DecimalField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        try:
           return super(CurrencyField, self).to_python(value).quantize(Decimal("0.01"))
        except AttributeError:
           return None

class SimplePayButton(models.Model):
    amount = CurrencyField(decimal_places=2, max_digits=6, blank=True, null=True)
    description = models.CharField(max_length=128)
    cobranding_style = models.CharField(max_length=8, choices=COBRANDING_STYLES, blank=True)
    process_immediate = models.BooleanField(default=True)
    collect_shipping_address = models.BooleanField(default=False)
    immediate_return = models.BooleanField(default=False)
    abandon_url = models.URLField(verify_exists=False, blank=True)
    return_url = models.URLField(verify_exists=False, blank=True)
    ipn_url = models.URLField(verify_exists=False, blank=True)
    
    class Meta:
        ordering = ('description',)
    
    def __unicode__(self):
        self.as_formdata()
        return "$%s %s" % (self.amount, self.description)
    
    def as_formdata(self):
        data = {}
        for field in self._meta.fields:
            if field.name not in EXCLUDED_FIELDS:
                value = getattr(self, field.name)
                if value:
                    data[camelcase(field.name)] = coerce_type(value)
        return data
    
    def get_real_obj(self):
        obj = getattr(self, 'donationbutton', None)
        if obj is None:
            obj = getattr(self, 'paymentbutton', None)
        return obj
    
    def get_form_class(self):
        if isinstance(self, DonationButton) or hasattr(self, 'donationbutton'):
            form_class = DonationForm
        elif isinstance(self, PaymentButton) or hasattr(self, 'paymentbutton'):
            form_class = PaymentForm
        else:
            raise ValueError('no form is associated with %s' % self.__class__.__name__)
        return form_class

class PaymentButton(SimplePayButton):
    pass

class DonationButton(SimplePayButton):
    donation_type = models.CharField(max_length=16, choices=DONATION_TYPES)
    minimum_donation_amount = CurrencyField(decimal_places=2, max_digits=6, blank=True, null=True)

class Transaction(models.Model):
    button = models.ForeignKey(SimplePayButton, related_name="transactions")
    reference_id = models.CharField(max_length=128)
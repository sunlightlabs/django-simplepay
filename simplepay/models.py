from decimal import Decimal
from django.db import models
from simplepay.forms import DonationForm, PaymentForm
import datetime
import uuid

COBRANDING_STYLES = [(s, s) for s in ('logo','banner')]
DONATION_TYPES = (
    ('fixedAmount', 'Fixed Amount'),
    ('minimumAmount', 'Minimum Amount'),
    ('anyAmount', 'Any Amount'),
)
TRANSACTION_STATUSES = (
    ('A', 'Abandoned'),
    ('ME', 'Merchant error'),
    ('PS', 'Success'),
    ('PF', 'Failed'),
    ('PI', 'Initiated'),
    ('PR', 'Reserve success'),
    ('RS', 'Refund success'),
    ('RF', 'Refund error'),
    ('SE', 'Service error'),
    ('SF', 'Subscription failed'),
    ('SI', 'Subscription initiated'),
    ('SR', 'Fee accepted'),
    ('SS', 'Subscription complete'),
    ('UE', 'Donation amount less than minimum'),
    ('UF', 'Invalid subscription payment method'),
    ('US', 'Updated subscription payment method'),
    ('XX', 'Not yet sent to payment'),
)
EXCLUDED_FIELDS = ('id','simplepaybutton_ptr')

#
# utility methods and classes
#

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
    
def generate_reference_id():
    return uuid.uuid4().hex
    
#
# field for currency
#

class CurrencyField(models.DecimalField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        try:
           return super(CurrencyField, self).to_python(value).quantize(Decimal("0.01"))
        except AttributeError:
           return None

#
# actual models
#

class SimplePayButton(models.Model):
    amount = CurrencyField(decimal_places=2, max_digits=6, blank=True, null=True)
    description = models.CharField(max_length=128)
    cobranding_style = models.CharField(max_length=8, choices=COBRANDING_STYLES, blank=True)
    process_immediate = models.BooleanField(default=True)
    collect_shipping_address = models.BooleanField(default=False)
    immediate_return = models.BooleanField(default=False)
    
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
    
    def get_form(self, data=None):
        form_data = self.as_formdata()
        form_data.update(data or {})
        form_class = self.get_form_class()
        return form_class(form_data)

class PaymentButton(SimplePayButton):
    pass

class DonationButton(SimplePayButton):
    donation_type = models.CharField(max_length=16, choices=DONATION_TYPES)
    minimum_donation_amount = CurrencyField(decimal_places=2, max_digits=6, blank=True, null=True)

class Transaction(models.Model):
    button = models.ForeignKey(SimplePayButton, related_name="transactions")
    reference_id = models.CharField(max_length=32, default=generate_reference_id)
    amount = CurrencyField(decimal_places=2, max_digits=6, blank=True, null=True)
    status = models.CharField(max_length=2, choices=TRANSACTION_STATUSES, default='XX')
    date_created = models.DateTimeField(default=datetime.datetime.utcnow)
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)
    
    def __unicode__(self):
        return self.reference_id
    
    def save(self, **kwargs):
        self.timestamp = datetime.datetime.utcnow()
        super(Transaction, self).save(**kwargs)
    
    def get_form(self, data=None):
        data = data or {}
        data['referenceId'] = self.reference_id
        if self.amount:
            data['amount'] = self.amount
        return self.button.get_form(data)

class Message(models.Model):
    transaction = models.ForeignKey(Transaction, related_name="messages")
    content = models.TextField()
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)
    
    class Meta:
        ordering = ('-timestamp',)
    
    def __unicode__(self):
        return self.timestamp.isoformat()
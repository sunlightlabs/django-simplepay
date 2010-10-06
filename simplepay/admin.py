from django.contrib import admin
from simplepay.models import DonationButton, PaymentButton, Transaction

admin.site.register(DonationButton)
admin.site.register(PaymentButton)
admin.site.register(Transaction)
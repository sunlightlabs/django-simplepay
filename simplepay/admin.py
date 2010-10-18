from django.contrib import admin
from simplepay.models import DonationButton, PaymentButton, Transaction, Message

class MessageInline(admin.TabularInline):
    model = Message

class TransactionAdmin(admin.ModelAdmin):
    inlines = (MessageInline,)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('timestamp','transaction','content')

admin.site.register(DonationButton)
admin.site.register(PaymentButton)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Message, MessageAdmin)
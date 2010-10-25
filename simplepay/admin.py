from django.contrib import admin
from simplepay.models import DonationButton, PaymentButton, Transaction, Message

class MessageInline(admin.TabularInline):
    model = Message

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('short_reference_id','short_amazon_id','status','amount','name','email','date_created','date_processed')
    list_filter = ('status',)
    inlines = (MessageInline,)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('timestamp','transaction','content')

admin.site.register(DonationButton)
admin.site.register(PaymentButton)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Message, MessageAdmin)
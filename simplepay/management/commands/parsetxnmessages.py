from django.core.management.base import BaseCommand, CommandError
from simplepay.models import Transaction
from simplepay.views import _parse_date
try:
    import json
except ImportError:
    import simplejson as json

class Command(BaseCommand):
    args = ''
    help = 'Populate new 0.2 fields from existing messages'
    
    def handle(self, *args, **options):
        
        for txn in Transaction.objects.all():
            
            try:
                
                msg = txn.messages.all()[0]
                data = json.loads(msg.content)
                
                if 'transactionId' in data and not txn.amazon_id:
                    txn.amazon_id = data['transactionId']
                
                if 'buyerName' in data and not txn.name:
                    txn.name = data['buyerName']
                
                if 'buyerEmail' in data and not txn.email:
                    txn.email = data['buyerEmail']
                
                if 'transactionDate' in data and not txn.date_processed:
                    txn.date_processed = _parse_date(data['transactionDate'])
                
                txn.save()
                
            except IndexError:
                pass
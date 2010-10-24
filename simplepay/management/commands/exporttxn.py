from django.core.management.base import BaseCommand, CommandError
from simplepay.models import Transaction
import csv
import datetime
import sys

FIELDS = ('reference_id','amazon_id','name','email','amount','date_created','date_processed','status')

def _str(o):
    if o is None:
        return u''
    elif isinstance(o, basestring):
        return o
    else:
        return unicode(o)

def _parse_date(s):
    return datetime.datetime(int(s[:4]), int(s[4:6]), int(s[6:]))

def _endofday(dt):
    return dt.replace(hour=23, minute=59, second=59)
    
class Command(BaseCommand):
    args = '(<from_yyyymmdd> (<to_yyyymmdd>))'
    help = 'Export transactions to CSV'
    
    def handle(self, *args, **options):
        
        writer = csv.DictWriter(sys.stdout, FIELDS)
        writer.writerow(dict((f, f) for f in FIELDS))
        
        if not args:
            txns = Transaction.objects.all()
        else:
            start = _parse_date(args[0])
            end = _endofday(_parse_date(args[1]) if len(args) > 1 else datetime.datetime.utcnow())
            txns = Transaction.objects.filter(date_created__range=(start, end))
        
        for txn in txns:
            writer.writerow(dict((f, _str(getattr(txn, f, ''))) for f in FIELDS))
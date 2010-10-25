from django.core.management.base import BaseCommand, CommandError
from simplepay.models import Transaction

class Command(BaseCommand):
    args = ''
    help = 'Populate new 0.2 fields from existing messages'
    
    def handle(self, *args, **options):
        
        pass
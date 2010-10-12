from django.conf import settings

PRODUCTION_HOST = 'authorize.payments.amazon.com'
SANDBOX_HOST = 'authorize.payments-sandbox.amazon.com'

IS_SANDBOX = getattr(settings, 'SIMPLEPAY_SANDBOX', False)

HOST = getattr(settings, 'SIMPLEPAY_HOST', SANDBOX_HOST if IS_SANDBOX else PRODUCTION_HOST)
PATH = getattr(settings, 'SIMPLEPAY_PATH', '/pba/paypipeline')

ACCESS_KEY = getattr(settings, 'SIMPLEPAY_KEY', '')
SECRET_KEY = getattr(settings, 'SIMPLEPAY_SECRET', '')

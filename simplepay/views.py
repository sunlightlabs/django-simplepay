from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.views.decorators.csrf import csrf_exempt
from simplepay import ACCESS_KEY, SECRET_KEY, HOST, PATH
from simplepay import api
from simplepay.models import SimplePayButton, Transaction, Message
import datetime
try:
    import json
except ImportError:
    import simplejson as json

REDIRECT = getattr(settings, 'SIMPLEPAY_COMPLETE_REDIRECT', None)

def _parse_date(ds):
    ts = int(ds)
    return datetime.datetime.fromtimestamp(ts)

def button(request, button_id):
    """ Return a JSON representation of button values.
    
        If the amount parameters is passed, update and sign the button
        with the new amount.
    """
    
    btn = SimplePayButton.objects.get(pk=int(button_id)).get_real_obj()
    form_class = btn.get_form_class()
    form_data = btn.as_formdata()
    
    if 'amount' in request.GET:
        form_data['amount'] = request.GET['amount']
        
    form = form_class(form_data)
    form.set_urls(request)
    form.generate_signature()
    
    if not form.is_valid():
        pass
        
    return HttpResponse(json.dumps(form.cleaned_data), content_type="application/json")

def transaction(request, reference_id):
    
    txn = get_object_or_404(Transaction, reference_id=reference_id)
    
    form = txn.get_form()
    
    if 'amount' in request.GET:
        form.data['amount'] = request.GET['amount']
        
    form.set_urls(request)
    form.generate_signature()

    if not form.is_valid():
        pass
        
    return HttpResponse(json.dumps(form.cleaned_data), content_type="application/json")


def abandon(request, reference_id):
    """ Users that cancel a transaction are passed to this URL by Amazon. Arguments that
        are passed are used to update the transaction and stored as a message from Amazon.
        
        If SIMPLEPAY_COMPLETE_REDIRECT is defined in settings.py, the user will
        be redirected to this URL. Otherwise the simplepay.transaction_complete.html
        template will be displayed to the user.
    """
    
    if not api.is_valid_signature(request.META['QUERY_STRING'], request.build_absolute_uri()):
        return HttpResponseBadRequest('invalid parameters')
        
    _update_transaction(reference_id, request.GET)

    if REDIRECT:
        return HttpResponseRedirect(SIMPLEPAY_COMPLETE_REDIRECT)
    return render_to_response('simplepay/transaction_abandoned.html')


def complete(request, reference_id):
    """ Upon completion of a transaction, users are sent back to this URL.
    
        If SIMPLEPAY_COMPLETE_REDIRECT is defined in settings.py, the user will
        be redirected to this URL. Otherwise the simplepay.transaction_complete.html
        template will be displayed to the user.
    """
    
    if not api.is_valid_signature(request.META['QUERY_STRING'], request.build_absolute_uri()):
        return HttpResponseBadRequest('invalid parameters')
        
    _update_transaction(reference_id, request.GET)

    if REDIRECT:
        return HttpResponseRedirect(REDIRECT)
    return render_to_response('simplepay/transaction_complete.html')

@csrf_exempt
def ipn(request, reference_id):
    """ Process an IPN response from Amazon.
    """
    
    print "IPN", reference_id, request.POST
    
    if api.is_valid_signature(request.POST, request.build_absolute_uri()):
        _update_transaction(reference_id, request.POST)
    
    return HttpResponse('Thanks, Amazon!')


def _update_transaction(reference_id, data):
    
    try:
        txn = Transaction.objects.get(reference_id=reference_id)
    except Transaction.DoesNotExist:
        button = SimplePayButton.objects.get(description=data.get('paymentReason', ''))
        txn = Transaction(
            reference_id=reference_id,
            button=button,
        )
    
    if 'status' in data:
        txn.status = data['status']
    
    if 'transactionAmount' in data:
        amt = data['transactionAmount']
        if ' ' in amt:
            amt = amt.split(' ')[1]
        txn.amount = amt
    
    if 'transactionDate' in data:
        txn.date_processed = _parse_date(data['transactionDate'])

    if 'transactionId' in data:
        txn.amazon_id = data['transactionId']
    
    if 'buyerName' in data:
        txn.name = data['buyerName']
    
    if 'buyerEmail' in data:
        txn.email = data['buyerEmail']
    
    txn.save()
    
    message = Message(content=json.dumps(data))
    txn.messages.add(message)
    
from django.http import HttpResponse
from simplepay import ACCESS_KEY, SECRET_KEY, HOST, PATH
from simplepay import api
from simplepay.models import SimplePayButton
import json

def button(request, button_id):
    
    btn = SimplePayButton.objects.get(pk=int(button_id)).get_real_obj()
    form_class = btn.get_form_class()
    form_data = btn.as_formdata()
    
    if 'amount' in request.GET:
        form_data['amount'] = request.GET['amount']
        
    form = form_class(form_data)
    form.generate_signature()
    
    if not form.is_valid():
        pass
        
    return HttpResponse(json.dumps(form.cleaned_data), content_type="application/json")

def abandon(request, reference_id):
    print request.GET
    return HttpResponse('abandon')

def complete(request, reference_id):
    print request.GET
    return HttpResponse('complete')

def ipn(request, reference_id):

    if request.method == 'POST':
        print request.POST
        api.is_valid_signature(request.POST, request.build_absolute_uri())
    
    
    
    return HttpResponse('ipn')
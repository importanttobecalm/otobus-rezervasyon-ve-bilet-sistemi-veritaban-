# yourappname/views.py
from django.shortcuts import render

def giris(request):
    return render(request, 'yourappname/giris.html')

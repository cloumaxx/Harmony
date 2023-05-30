from django.shortcuts import render

# Create your views here.

def pantalla_inicial(request):
    return render(request, "pantalla_inicial/pantalla_inicial.html")

def pantalla_login(request):
    return render(request, "pantalla_login/pantalla_login.html")
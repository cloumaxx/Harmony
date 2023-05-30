from django.urls import path
from . import views

urlpatterns = [
    path("", views.pantalla_login, name="login"),
    path("pantalla_incial", views.pantalla_inicial, name="pantalla_inicial"),
]
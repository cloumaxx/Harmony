
from django.urls import path
from . import views
from . import models
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("generar_respuesta_openai/<str:entrada>", views.generar_respuesta_openai, name="generar_respuesta_openai"),
    path('chat/', views.chat, name='chat'),

]
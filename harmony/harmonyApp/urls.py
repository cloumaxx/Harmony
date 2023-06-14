from django.urls import path
from . import views

urlpatterns = [
    path("", views.pantalla_login, name="login"),
    path("pantalla_login", views.pantalla_login, name="pantalla_login"),
    path("pantalla_incial/<str:usuario_id>/", views.pantalla_inicial, name="pantalla_inicial"),
    path("pantalla_registro", views.pantalla_registro, name="pantalla_registro"),
    path("pantalla_perfil_usuario/<str:usuario_id>/", views.pantalla_perfil_usuario, name="pantalla_perfil_usuario"),
    path('actualizar_usuario/<str:usuario_id>/', views.actualizar_usuario, name='actualizar_usuario'),
    
    path('pantalla_foro/<str:usuario_id>/', views.pantalla_foro, name='pantalla_foro'),
    path('pantalla_nuevo_comentario/<str:usuario_id>/', views.pantalla_nuevo_comentario, name='pantalla_nuevo_comentario'),
    path('pantalla_foro/<str:usuario_id>/comentario/<str:comentario_id>/incrementar_likes/', views.incrementar_likes, name='incrementar_likes'),

]
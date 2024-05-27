from django.urls import path
from . import views

urlpatterns = [
    path("", views.pantalla_inicial, name="pantalla_inicial"),
    path("pantalla_inicial", views.pantalla_inicial, name="pantalla_inicial"),
    path("pantalla_login", views.pantalla_login, name="pantalla_login"),
    path("logout_view", views.logout_view, name="logout_view"),
    path("pantalla_menu_inicial/<str:usuario_id>/", views.pantalla_menu_inicial, name="pantalla_menu_inicial"),
    path("pantalla_registro", views.pantalla_registro, name="pantalla_registro"),
    path("pantalla_perfil_usuario/<str:usuario_id>/", views.pantalla_perfil_usuario, name="pantalla_perfil_usuario"),
    path('editar_usuario/<str:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('calificar_app/<str:usuario_id>/', views.calificarApp, name='calificarApp'),
    path('pantalla_estadisticas/<str:usuario_id>/', views.pantalla_estadisticas, name='pantalla_estadisticas'),

    path('pantalla_chatbot/<str:usuario_id>/posicion/<int:posicion>/', views.pantalla_chatbot, name='pantalla_chatbot'),
    path('pantalla_chatbot/<str:usuario_id>/crearNuevoChat/', views.crearNuevoChat, name='crearNuevoChat'),
    path('pantalla_chatbot/<str:usuario_id>/enviarMensajeChatBot/<int:posicion>/', views.enviarMensajeChatBot, name='enviarMensajeChatBot'),
    path('pantalla_chatbot/<str:usuario_id>/vaciarChat/<int:posicion>/', views.vaciarChat, name='vaciarChat'),
    path('pantalla_chatbot/<str:usuario_id>/eliminarChat/<int:posicion>/', views.eliminarChat, name='eliminarChat'),
    path('pantalla_foro/<str:usuario_id>/', views.pantalla_foro, name='pantalla_foro'),
    path('pantalla_nuevo_comentario/<str:usuario_id>/', views.pantalla_nuevo_comentario, name='pantalla_nuevo_comentario'),
    path('pantalla_foro/<str:usuario_id>/comentario/<str:comentario_id>/incrementar_likes/', views.incrementar_likes, name='incrementar_likes'),
    path('pantalla_foro/<str:usuario_id>/comentario/<str:comentario_id>/replica/<str:pos>/incrementar_likes_replica/', views.incrementar_likes_replica, name='incrementar_likes_replica'),

    path('pantalla_foro/<str:usuario_id>/comentario/<str:comentario_id>/editar_comentario/', views.editar_comentario, name='editar_comentario'),
    path('pantalla_foro/<str:usuario_id>/comentario/<str:comentario_id>/borrar_comentario/', views.borrar_comentario, name='borrar_comentario'),
    path('pantalla_foro/<str:usuario_id>/comentario/<str:comentario_id>/borrar_replica/<int:pos>', views.borrar_replica, name='borrar_replica'),

    path('agregar_replica/<str:usuario_id>/comentario/<str:comentario_id>/agregar_replica/',views.agregar_replica,name="agregar_replica")
]
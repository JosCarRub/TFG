from django.urls import path
from .views import *

urlpatterns = [
    path('', Landing.as_view(), name='landing'),

#REGISTRO
    path('registro',UserRegister.as_view(), name='registro' ),

#PERFIL
    path('perfil', Perfil.as_view(), name='perfil'),
    path('update_profile',UserUpdateProfile.as_view(), name='update_profile'),
    




    path('home', Home.as_view(), name='home'),
    #SECCIONES
    path('buscar_partidos', BuscarPartidos.as_view(), name='buscar_partidos'),
    path('crear_partidos', CrearPartidos.as_view(), name='crear_partidos'),
    path('torneos', Torneos.as_view(), name='torneos'),
    path('canchas', Canchas.as_view(), name='canchas'),
    path('estadisticas', Estadisticas.as_view(), name='estadisticas'),

    



]
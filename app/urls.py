from django.urls import path
from .views import *

urlpatterns = [
    path('', Landing.as_view(), name='landing'),

#REGISTRO
    path('login', Login.as_view(), name='login'),
    



    path('perfil', Perfil.as_view(), name='perfil'),

    path('home', Home.as_view(), name='home'),
    #SECCIONES
    path('buscar_partidos', BuscarPartidos.as_view(), name='buscar_partidos'),
    path('crear_partidos', CrearPartidos.as_view(), name='crear_partidos'),
    path('torneos', Torneos.as_view(), name='torneos'),
    path('canchas', Canchas.as_view(), name='canchas'),
    path('estadisticas', Estadisticas.as_view(), name='estadisticas'),

    



]
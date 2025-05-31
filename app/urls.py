from django.urls import path
from .views import *

urlpatterns = [


##---------- COMMONS --------------------------------------------------------------------------------------------

    path('', Landing.as_view(), name='landing'),
    path('home', Home.as_view(), name='home'),
    path('estadisticas', Estadisticas.as_view(), name='estadisticas'),

#---------- REGISTRO --------------------------------------------------------------------------------------------
    path('registro',UserRegister.as_view(), name='registro' ),

##---------- PERFIL --------------------------------------------------------------------------------------------
    path('perfil', Perfil.as_view(), name='perfil'),
    path('update_profile',UserUpdateProfile.as_view(), name='update_profile'),
    
##---------- PARTIDOS --------------------------------------------------------------------------------------------
    path('crear_partidos', CrearPartidos.as_view(), name='crear_partidos'),
    path('buscar_partidos/', BuscarPartidos.as_view(), name='buscar_partidos'),
    path('partido/<uuid:partido_id>/inscribirse/', InscribirsePartidoView.as_view(), name='inscribirse_partido'),
    path('partido/<uuid:pk>/', DetallePartidoView.as_view(), name='detalle_partido'),
    path('partido/<uuid:pk>/registrar_resultado/', RegistrarResultadoPartidoView.as_view(), name='registrar_resultado_partido'),


##---------- CANCHAS --------------------------------------------------------------------------------------------
    path('canchas/', CanchasView.as_view(), name='canchas_lista'), 
    path('canchas/registrar/', RegistrarCanchaView.as_view(), name='canchas_registrar'),
    path('cancha/<uuid:pk_cancha>/', DetalleCanchaView.as_view(), name='detalle_cancha'),


]
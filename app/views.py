from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView ,TemplateView, CreateView, DetailView, UpdateView, DeleteView, FormView
from django.contrib import messages
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import *




# LANDING
class Landing(TemplateView):
    template_name = 'landing.html'

#REGISTRO
class Login(TemplateView):
    form_class = UserCreationForm
    template_name = 'registration/login.html'
    success_url = ('home')


    def form_valid(self, form):
        return super().form_valid(form)
    
class UserRegister(TemplateView):
    form_class = UserCreationForm
    template_name = 'registration/user_register.html'
    success_url = reverse_lazy('login')


    def form_valid(self, form):
        return super().form_valid(form)
    
    
#HOME
class Home(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

#PERFIL
class Perfil(TemplateView):
    template_name = 'perfil.html'

#SECCIONES
class BuscarPartidos(TemplateView):
    template_name = 'buscar_partidos.html'

class Torneos(TemplateView):
    template_name = 'torneos.html'

class CrearPartidos(TemplateView):
    template_name = 'crear_partidos.html'

class Canchas(TemplateView):
    template_name = 'canchas.html'

class Estadisticas(TemplateView):
    template_name = 'estadisticas.html'



    # def historial_elo(self):

    #     return self.get_user_historialElo.order_by('fecha')[:30]







    # @receiver(post_save, sender=Partido)
    # def actualizar_calificaciones_post_save(sender, instance, created, **kwargs):
    #     if instance.estado == 'FINALIZADO' and not instance.calificacion_actualizada:
    #         instance.actualizar_calificaciones()




    # def finalizar_partido(request, partido_id):
    #     partido = get_object_or_404(Partido, id=partido_id)

    #     if partido.estado != 'FINALIZADO':
    #         partido.estado = 'FINALIZADO'
    #         partido.save()

    #         if not partido.calificacion_actualizada:
    #             partido.actualizar_calificaciones()
    #             messages.success(request, 'El partido fue finalizado y se actualizaron las calificaciones.')
    #         else:
    #             messages.info(request, 'Este partido ya tenía las calificaciones actualizadas.')

    #     else:
    #         messages.warning(request, 'Este partido ya estaba finalizado.')

    #     return redirect('detalle_partido', partido_id=partido.id)
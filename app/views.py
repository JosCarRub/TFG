from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView ,TemplateView, CreateView, DetailView, UpdateView, DeleteView, FormView
from django.contrib import messages
from django.contrib.auth.views import LoginView

from .forms import UserRegisterForm, UserUpdateProfilelForm
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import *


# LANDING
class Landing(TemplateView):
    template_name = 'landing.html'

#REGISTRO
class UserRegister(CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/registro.html'
    success_url = reverse_lazy('login')


    def form_valid(self, form):
        messages.success(self.request, "¡Registro completado! Ahora puedes iniciar sesión.")
        return super().form_valid(form)
    
    
#HOME
class Home(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

#PERFIL
class Perfil(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'perfil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class UserUpdateProfile(LoginRequiredMixin, UpdateView):

    model = User
    form_class = UserUpdateProfilelForm
    template_name = 'update_profile.html'
    success_url = reverse_lazy('perfil')

    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):

        messages.success(self.request, '¡Tu perfil ha sido actualizado con éxito!')

        return super().form_valid(form)
    
    def form_invalid(self, form):

        messages.error(self.request, 'No ha sido posible actuliazar tu perfil, revisa los campos que has querido actulizar por que debe haber un error.')

        return super().form_invalid(form)
    


    

#SECCIONES
class BuscarPartidos(LoginRequiredMixin, TemplateView):
    template_name = 'buscar_partidos.html'

class Torneos(LoginRequiredMixin, TemplateView):
    template_name = 'torneos.html'

class CrearPartidos(LoginRequiredMixin, TemplateView):
    template_name = 'crear_partidos.html'

class Canchas(LoginRequiredMixin, TemplateView):
    template_name = 'canchas.html'

class Estadisticas(LoginRequiredMixin, TemplateView):
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
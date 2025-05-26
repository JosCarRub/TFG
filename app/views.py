from datetime import timezone
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView ,TemplateView, CreateView, DetailView, UpdateView, DeleteView, FormView
from django.contrib import messages
from django.contrib.auth.views import LoginView

from .forms import *
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
    success_url = reverse_lazy('home')


    def form_valid(self, form):
        messages.success(self.request, "¡Registro completado! Ahora puedes iniciar sesión.")
        return super().form_valid(form)
    
    
#HOME
class Home(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

#PERFIL
class Perfil(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'perfil/perfil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class UserUpdateProfile(LoginRequiredMixin, UpdateView):

    model = User
    form_class = UserUpdateProfilelForm
    template_name = 'perfil/update_profile.html'
    success_url = reverse_lazy('perfil')

    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):

        messages.success(self.request, '¡Tu perfil ha sido actualizado con éxito!')

        return super().form_valid(form)
    
    def form_invalid(self, form):

        messages.error(self.request, 'No ha sido posible actuliazar tu perfil, revisa los campos que has querido actulizar por que debe haber un error.')

        return super().form_invalid(form)



#PARTIDOS
class CrearPartidos(LoginRequiredMixin, CreateView):
    model = Partido
    form_class = PartidoForm
    template_name = 'partidos/crear_partidos.html'
    success_url = reverse_lazy('buscar_partidos')

    def form_valid(self, form):
        # Asignar el creador
        form.instance.creador = self.request.user
        
        # Asignar la fecha calculada desde cleaned_data al campo 'fecha' de la instancia
        # Esto es crucial porque 'fecha' no está en Meta.fields del formulario.
        if 'fecha' in form.cleaned_data:
            form.instance.fecha = form.cleaned_data['fecha']
        else:
            # Esto no debería ocurrir si la validación en clean() es correcta
            # pero es una salvaguarda o un punto para depurar.
            messages.error(self.request, "Error interno: No se pudo determinar la fecha del partido.")
            return self.form_invalid(form)

        # Ahora, cuando super().form_valid() llame a form.save(),
        # form.instance.fecha ya tendrá el valor correcto.
        response = super().form_valid(form) 
        
        # self.object se establece por super().form_valid()
        if self.object:
            self.object.jugadores.add(self.request.user)
        
        messages.success(self.request, f"¡Partido en '{self.object.cancha.nombre_cancha}' creado con éxito para el {self.object.fecha.strftime('%d/%m/%Y a las %H:%M')}!")
        return response
    

class BuscarPartidos(LoginRequiredMixin, TemplateView):
    template_name = 'partidos/buscar_partidos.html'

    
#CANCHAS
class CanchasView(LoginRequiredMixin, ListView):
    model = Cancha
    template_name = 'canchas/canchas_lista.html' # Nueva plantilla para listar
    context_object_name = 'canchas_list'
    paginate_by = 9 # O el número que prefieras

    def get_queryset(self):
        
        return Cancha.objects.filter(disponible=True).order_by('nombre_cancha')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Descubre Nuestras Canchas"
        return context
    
class RegistrarCanchaView(LoginRequiredMixin, CreateView):
    model = Cancha
    form_class = CanchasForm
    template_name = 'canchas/registro_canchas.html' 
    success_url = reverse_lazy('canchas_lista') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Registrar Nueva Cancha"
        return context

    def form_valid(self, form):
        # Aquí podrías añadir lógica si el usuario que crea es el "propietario"
        # form.instance.propietario = self.request.user # Si tuvieras un campo así en el modelo Cancha
        cancha = form.save()
        messages.success(self.request, f"¡Cancha '{cancha.nombre_cancha}' registrada con éxito!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Hubo errores al registrar la cancha. Por favor, revisa el formulario.")
        return super().form_invalid(form)


    

#SECCIONES


class Torneos(LoginRequiredMixin, TemplateView):
    template_name = 'torneos.html'


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
from datetime import timezone
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView ,TemplateView, CreateView, DetailView, UpdateView, DeleteView, FormView, View
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.db.models import Count, Case, When, BooleanField
from django.shortcuts import get_object_or_404, redirect



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
        form.instance.creador = self.request.user
        
        if 'fecha' in form.cleaned_data:
            form.instance.fecha = form.cleaned_data['fecha']
        else:
            messages.error(self.request, "Error: Fecha del partido no procesada.")
            return self.form_invalid(form)

        # Asignar fecha_limite_inscripcion si vino del formulario
        # Si es None, el método save() del modelo Partido lo calculará por defecto
        if 'fecha_limite_inscripcion' in form.cleaned_data:
            form.instance.fecha_limite_inscripcion = form.cleaned_data['fecha_limite_inscripcion']
        
        response = super().form_valid(form)
        
        if self.object:
            self.object.jugadores.add(self.request.user)
        
        messages.success(self.request, f"¡Partido en '{self.object.cancha.nombre_cancha}' creado con éxito para el {self.object.fecha.strftime('%d/%m/%Y a las %H:%M')}!")
        return response
    

class BuscarPartidos(LoginRequiredMixin, ListView):
    model = Partido
    template_name = 'partidos/buscar_partidos.html'
    context_object_name = 'partidos_info_list' # Cambiado para evitar confusión con el original
    paginate_by = 9

    def get_queryset(self):
        ahora = django_timezone.now()
        # Partidos programados que aún no han pasado su fecha límite de inscripción efectiva
        # y que tienen plazas disponibles.
        queryset = Partido.objects.filter(
            estado='PROGRAMADO',
            # fecha_limite_inscripcion_efectiva > ahora (esto se hará con annotate y Case/When)
            # o podemos filtrar después de anotar
        ).annotate(
            num_jugadores_inscritos=Count('jugadores'),
            # Calculamos la fecha_limite_efectiva aquí para poder filtrar
            # Si fecha_limite_inscripcion es NULL, usamos fecha - 1 hora
            limite_inscripcion_calculada=Case(
                When(fecha_limite_inscripcion__isnull=False, then=models.F('fecha_limite_inscripcion')),
                default=models.ExpressionWrapper(models.F('fecha') - timedelta(hours=1), output_field=models.DateTimeField())
            )
        ).filter(
            limite_inscripcion_calculada__gt=ahora, # Inscripción aún no ha cerrado
            num_jugadores_inscritos__lt=models.F('max_jugadores') # Plazas disponibles
        ).order_by('fecha')
        
        # No excluimos los partidos del usuario aquí, lo manejaremos en el contexto

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Esto ya poblará 'partidos_info_list'
        context['titulo_pagina'] = "Encuentra Partidos"
        
        # Procesar la lista de partidos para añadir información contextual
        partidos_procesados = []
        # 'object_list' es el nombre por defecto que ListView usa para el queryset paginado
        # si no se define context_object_name o si se quiere el queryset original.
        # En nuestro caso, ListView ya usa 'partidos_info_list' por context_object_name.
        for partido in context['partidos_info_list']: 
            es_creador = (partido.creador == self.request.user)
            esta_inscrito = self.request.user in partido.jugadores.all()
            
            # Usamos la propiedad del modelo para determinar si la inscripción está abierta
            # La propiedad ya considera el estado, el límite y las plazas.
            inscripcion_esta_abierta = partido.inscripcion_abierta 

            plazas_disponibles = partido.max_jugadores - partido.num_jugadores_inscritos

            partidos_procesados.append({
                'partido': partido,
                'es_creador': es_creador,
                'esta_inscrito': esta_inscrito,
                'inscripcion_esta_abierta': inscripcion_esta_abierta,
                'plazas_disponibles': plazas_disponibles,
            })
        context['partidos_info_list'] = partidos_procesados # Reemplazamos con la lista procesada
        return context

class DetallePartidoView(LoginRequiredMixin, DetailView):
    model = Partido
    template_name = 'partidos/detalle_partido.html' 
    context_object_name = 'partido'
    pk_url_kwarg = 'pk' # Si en tu URL usas <uuid:pk> o <int:pk>

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partido = self.get_object()
        context['titulo_pagina'] = f"Detalles del Partido en {partido.cancha.nombre_cancha}"
        context['es_creador'] = (partido.creador == self.request.user)
        context['esta_inscrito'] = self.request.user in partido.jugadores.all()
        context['inscripcion_esta_abierta'] = partido.inscripcion_abierta
        context['jugadores_inscritos_list'] = partido.jugadores.all().order_by('nombre')
        context['plazas_disponibles'] = partido.max_jugadores - partido.jugadores.count()
        return context

    
class InscribirsePartidoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        partido_id = kwargs.get('partido_id') # Asumiendo que pasas el ID del partido en la URL
        partido = get_object_or_404(Partido, id_partido=partido_id, estado='PROGRAMADO') # Usar id_partido
        usuario = request.user

        # Verificar si ya está inscrito (doble check, aunque el queryset de búsqueda ya lo excluye)
        if usuario in partido.jugadores.all():
            messages.warning(request, "Ya estás inscrito en este partido.")
            return redirect('buscar_partidos') # O a la página de detalle del partido

        # Verificar si hay plazas
        if partido.jugadores.count() >= partido.max_jugadores:
            messages.error(request, "Lo sentimos, este partido ya está lleno.")
            return redirect('buscar_partidos')

        # Crear la inscripción (o simplemente añadir al ManyToManyField)
        # Opción 1: Solo añadir al ManyToManyField 'jugadores' del Partido
        partido.jugadores.add(usuario)
        messages.success(request, f"¡Te has inscrito correctamente al partido en {partido.cancha.nombre_cancha}!")

        # Opción 2: Si quieres usar tu modelo Inscripcion (más formal)
        # if not Inscripcion.objects.filter(jugador=usuario, partido=partido).exists():
        #     Inscripcion.objects.create(
        #         jugador=usuario,
        #         partido=partido,
        #         tipo='JUGADOR_PARTIDO', # Asegúrate que este valor coincida con tus choices
        #         estado='ACEPTADA' # O 'PENDIENTE' si requiere aprobación del creador
        #     )
        #     partido.jugadores.add(usuario) # Aún necesitas añadirlo al M2M para el conteo fácil
        #     messages.success(request, f"¡Solicitud de inscripción enviada para el partido en {partido.cancha.nombre_cancha}!")
        # else:
        #     messages.warning(request, "Ya tienes una inscripción para este partido.")

        return redirect('buscar_partidos') # O a 'mis_partidos' o detalle del partido



    
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
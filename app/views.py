from datetime import timezone
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView ,TemplateView, CreateView, DetailView, UpdateView, DeleteView, FormView, View
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.db.models import Count, Case, When, BooleanField
from django.shortcuts import get_object_or_404, redirect

from django.contrib.auth import get_user_model


from .forms import *
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import *
User = get_user_model() 

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

class DetallePartidoView(LoginRequiredMixin, DetailView): # DetailView puede manejar POST si lo sobrescribes
    model = Partido
    template_name = 'partidos/detalle_partido.html'
    context_object_name = 'partido'
    pk_url_kwarg = 'pk' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partido = self.get_object()
        usuario_actual = self.request.user

        context['titulo_pagina'] = f"Detalles: {partido.cancha.nombre_cancha} - {partido.fecha.strftime('%d/%m %H:%M')}"
        context['es_creador'] = (partido.creador == usuario_actual)
        context['esta_inscrito'] = usuario_actual in partido.jugadores.all()
        context['inscripcion_esta_abierta'] = partido.inscripcion_abierta
        
        jugadores_inscritos_list = partido.jugadores.all().order_by('nombre')
        context['jugadores_inscritos_list'] = jugadores_inscritos_list
        context['plazas_disponibles'] = partido.max_jugadores - partido.jugadores.count()

        if context['es_creador'] and partido.estado == 'PROGRAMADO':
            # Pasar el formulario de asignación de equipos al contexto
            # Pasamos los jugadores inscritos y el partido para pre-rellenar si ya hay equipos
            context['form_asignar_equipos'] = AsignarEquiposForm(
                jugadores_inscritos=jugadores_inscritos_list,
                partido=partido 
            )
        return context

    def post(self, request, *args, **kwargs):
        partido = self.get_object()
        usuario_actual = request.user

        if partido.creador != usuario_actual:
            messages.error(request, "No tienes permiso para modificar este partido.")
            return redirect('detalle_partido', pk=partido.id_partido)

        if partido.estado != 'PROGRAMADO':
            messages.error(request, "Solo se pueden asignar equipos a partidos programados.")
            return redirect('detalle_partido', pk=partido.id_partido)

        # Procesar el formulario de asignación de equipos
        form_asignar = AsignarEquiposForm(request.POST, jugadores_inscritos=partido.jugadores.all(), partido=partido)

        if form_asignar.is_valid():
            jugadores_equipo_local_ids = []
            jugadores_equipo_visitante_ids = []

            for jugador_obj in partido.jugadores.all(): # 'jugador_obj' para evitar confusión con la variable 'jugador' del bucle en el template
                asignacion = form_asignar.cleaned_data.get(f'jugador_{jugador_obj.id}')
                if asignacion == 'local':
                    jugadores_equipo_local_ids.append(jugador_obj.id)
                elif asignacion == 'visitante':
                    jugadores_equipo_visitante_ids.append(jugador_obj.id)
            
            

            # Crear o actualizar equipos temporales para el partido
            # Equipo Local
            if partido.equipo_local:
                equipo_local = partido.equipo_local
                
                equipo_local.jugadores.set(User.objects.filter(id__in=jugadores_equipo_local_ids))
            else:
                equipo_local = Equipo.objects.create(
                    nombre_equipo=f"Locales - {partido.cancha.nombre_cancha} {partido.fecha.strftime('%d%m%y%H%M')}",
                    capitan=partido.creador,
                    tipo_equipo='PARTIDO'
                )
                equipo_local.jugadores.set(User.objects.filter(id__in=jugadores_equipo_local_ids)) # Igual aquí
                partido.equipo_local = equipo_local

            # Equipo Visitante
            if partido.equipo_visitante:
                equipo_visitante = partido.equipo_visitante
                equipo_visitante.jugadores.set(User.objects.filter(id__in=jugadores_equipo_visitante_ids)) # Igual aquí
            else:
                equipo_visitante = Equipo.objects.create(
                    nombre_equipo=f"Visitantes - {partido.cancha.nombre_cancha} {partido.fecha.strftime('%d%m%y%H%M')}",
                    capitan=partido.creador, 
                    tipo_equipo='PARTIDO'
                )
                equipo_visitante.jugadores.set(User.objects.filter(id__in=jugadores_equipo_visitante_ids)) # Igual aquí
                partido.equipo_visitante = equipo_visitante
            
            partido.save()
            messages.success(request, "Equipos asignados correctamente al partido.")
            return redirect('detalle_partido', pk=partido.id_partido)
        else:
            # Si el formulario no es válido, re-renderizar la página con los errores
            # Es un poco más complejo pasar el form con errores de vuelta al DetailView
            # Una forma es guardar los errores en messages o re-renderizar el contexto.
            for field, errors in form_asignar.errors.items():
                for error in errors:
                    messages.error(request, f"Error en asignación: {error}")
            # Recargamos el contexto para que el formulario con errores se muestre
            context = self.get_context_data(**kwargs) # Obtener contexto base
            context['form_asignar_equipos'] = form_asignar # Sobrescribir con el form con errores
            return self.render_to_response(context)


    
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

        return redirect('buscar_partidos') # O a 'mis_partidos' o detalle del partido
    
class RegistrarResultadoPartidoView(LoginRequiredMixin, FormView):
    form_class = ResultadoPartidoForm
    template_name = 'partidos/registrar_resultado.html' # Nueva plantilla

    def dispatch(self, request, *args, **kwargs):
        """
        Asegura que solo el creador del partido pueda acceder y
        que el partido esté en un estado adecuado (PROGRAMADO o EN_CURSO).
        """
        self.partido = get_object_or_404(Partido, id_partido=kwargs['pk'])
        if self.partido.creador != request.user:
            messages.error(request, "No tienes permiso para registrar el resultado de este partido.")
            return redirect('detalle_partido', pk=self.partido.id_partido)
        if self.partido.estado == 'FINALIZADO':
            messages.info(request, "Este partido ya ha finalizado y tiene un resultado registrado.")
            return redirect('detalle_partido', pk=self.partido.id_partido)
        if self.partido.estado == 'CANCELADO':
            messages.warning(request, "No se puede registrar resultado para un partido cancelado.")
            return redirect('detalle_partido', pk=self.partido.id_partido)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partido'] = self.partido
        context['titulo_pagina'] = f"Registrar Resultado para: Partido en {self.partido.cancha.nombre_cancha}"
        # Pre-rellenar el formulario si ya hay goles (aunque no debería si no está finalizado)
        if self.partido.goles_local is not None:
            context['form'].fields['goles_local'].initial = self.partido.goles_local
        if self.partido.goles_visitante is not None:
            context['form'].fields['goles_visitante'].initial = self.partido.goles_visitante
        return context

    def form_valid(self, form):
        goles_local = form.cleaned_data['goles_local']
        goles_visitante = form.cleaned_data['goles_visitante']

        partido = self.partido
        partido.goles_local = goles_local
        partido.goles_visitante = goles_visitante
        partido.estado = 'FINALIZADO'
        partido.save() # Guardar los goles y el nuevo estado

        # Actualizar calificaciones ELO
        # Solo si la modalidad no es AMISTOSO y los equipos están definidos
        if partido.modalidad != 'AMISTOSO' and partido.equipo_local and partido.equipo_visitante:
            partido.actualizar_calificaciones() # Llama a tu método del modelo
            messages.success(self.request, "Resultado registrado y calificaciones ELO actualizadas.")
        else:
            if partido.modalidad == 'AMISTOSO':
                messages.success(self.request, "Resultado del partido amistoso registrado (ELO no afectado).")
            else:
                messages.warning(self.request, "Resultado registrado, pero no se pudieron actualizar las calificaciones ELO (faltan equipos o es amistoso).")
        
        return redirect('detalle_partido', pk=partido.id_partido)

    def get_success_url(self):
        # Este método es llamado por FormView si no se especifica en form_valid un redirect
        # pero como ya hacemos redirect en form_valid, podemos omitirlo o hacerlo más genérico.
        return reverse_lazy('detalle_partido', kwargs={'pk': self.partido.id_partido})



    
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

class DetalleCanchaView(LoginRequiredMixin, DetailView):
    model = Cancha
    template_name = 'canchas/detalle_cancha.html' # Nueva plantilla
    context_object_name = 'cancha'
    pk_url_kwarg = 'pk_cancha' # Para que coincida con la URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cancha = self.get_object()
        context['titulo_pagina'] = f"Detalles de la Cancha: {cancha.nombre_cancha}"
        
        # Próximos partidos en esta cancha
        context['proximos_partidos'] = Partido.objects.filter(
            cancha=cancha,
            fecha__gte=django_timezone.now(), # Usar django_timezone.now()
            estado='PROGRAMADO'
        ).order_by('fecha')[:10] # Limitar a los próximos 10, por ejemplo

        # Podrías añadir un formulario para reservar directamente si es privada y lo implementas
        # context['form_reserva'] = ...
        return context
    

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
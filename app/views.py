from datetime import timezone as django_timezone
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView ,TemplateView, CreateView, DetailView, UpdateView, DeleteView, FormView, View
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.db.models import Count, Case, When, F, Q, DateTimeField, ExpressionWrapper
from django.shortcuts import get_object_or_404, redirect


from django.contrib.auth import get_user_model

from app.forms import AsignarEquiposForm, CanchasForm, PartidoForm, ResultadoPartidoForm, UserRegisterForm, UserUpdateProfilelForm


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
    # success_url se define en get_success_url para redirigir al detalle

    def get_form_kwargs(self):
        """Pasar el usuario al formulario si es necesario para filtrar querysets."""
        kwargs = super().get_form_kwargs()
        # kwargs['user'] = self.request.user # Descomentar si PartidoForm necesita el usuario
        return kwargs

    def form_valid(self, form):

        form.instance.creador = self.request.user
        
        # La fecha y fecha_limite_inscripcion ya deberían estar en cleaned_data
        # gracias al método clean() del formulario.
        if 'fecha' in form.cleaned_data:
            form.instance.fecha = form.cleaned_data['fecha']
        else:
            messages.error(self.request, "Error crítico: La fecha del partido no se pudo procesar.")
            return self.form_invalid(form)

        if 'fecha_limite_inscripcion' in form.cleaned_data and form.cleaned_data['fecha_limite_inscripcion'] is not None:
            form.instance.fecha_limite_inscripcion = form.cleaned_data['fecha_limite_inscripcion']
        # Si es None, el save() del modelo Partido lo calculará
        
        # Si se seleccionaron equipos permanentes en el form, se asignan aquí
        # Esto asume que tu PartidoForm tiene campos 'equipo_local' y 'equipo_visitante' que son ModelChoiceFields
        # y que están en Meta.fields o los asignas desde cleaned_data
        if form.cleaned_data.get('equipo_local'):
            form.instance.equipo_local = form.cleaned_data['equipo_local']
        if form.cleaned_data.get('equipo_visitante'):
            form.instance.equipo_visitante = form.cleaned_data['equipo_visitante']

        self.object = form.save() # Guardar el partido
        
        # Añadir al creador como jugador
        self.object.jugadores.add(self.request.user)

        # Si se seleccionaron equipos permanentes, añadir sus jugadores al partido (si hay plazas)
        # Esta lógica podría ser más compleja (ej. no añadir si el jugador ya está)
        if self.object.equipo_local:
            for jugador in self.object.equipo_local.jugadores.all():
                if self.object.jugadores.count() < self.object.max_jugadores:
                    self.object.jugadores.add(jugador) 
                else: break
        if self.object.equipo_visitante:
             for jugador in self.object.equipo_visitante.jugadores.all():
                if self.object.jugadores.count() < self.object.max_jugadores:
                    self.object.jugadores.add(jugador)
                else: break
        
        messages.success(self.request, f"¡Partido en '{self.object.cancha.nombre_cancha}' creado con éxito para el {self.object.fecha.strftime('%d/%m/%Y a las %H:%M')}!")
        return redirect(self.get_success_url()) # Usar redirect con get_success_url

    def get_success_url(self):
        return reverse('detalle_partido', kwargs={'pk': self.object.id_partido})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Organizar Nuevo Partido (Duración: 1 hora)"
        return context

class BuscarPartidos(LoginRequiredMixin, ListView):
    model = Partido
    template_name = 'partidos/buscar_partidos.html'
    context_object_name = 'partidos_info_list'
    paginate_by = 9

    def get_queryset(self):
        ahora = django_timezone.now()
        queryset = Partido.objects.filter(
            estado='PROGRAMADO'
        ).annotate(
            num_jugadores_inscritos=Count('jugadores'),
            limite_inscripcion_calculada=Case(
                When(fecha_limite_inscripcion__isnull=False, then=F('fecha_limite_inscripcion')),
                default=ExpressionWrapper(F('fecha') - timedelta(hours=1), output_field=DateTimeField())
            )
        ).filter(
            limite_inscripcion_calculada__gt=ahora,
            num_jugadores_inscritos__lt=F('max_jugadores')
        ).select_related('cancha', 'creador').prefetch_related('jugadores').order_by('fecha')
        # No excluimos partidos del creador aquí, se maneja en el template/contexto
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Encuentra Partidos"
        
        partidos_procesados = []
        for partido_obj in context['partidos_info_list']: # ListView usa object_list, pero context_object_name lo renombra
            es_creador = (partido_obj.creador == self.request.user)
            esta_inscrito = self.request.user in partido_obj.jugadores.all()
            inscripcion_esta_abierta = partido_obj.inscripcion_abierta 
            plazas_disponibles = partido_obj.max_jugadores - partido_obj.num_jugadores_inscritos

            partidos_procesados.append({
                'partido': partido_obj,
                'es_creador': es_creador,
                'esta_inscrito': esta_inscrito,
                'inscripcion_esta_abierta': inscripcion_esta_abierta,
                'plazas_disponibles': plazas_disponibles,
            })
        context['partidos_info_list'] = partidos_procesados
        return context

class DetallePartidoView(LoginRequiredMixin, DetailView):
    model = Partido
    template_name = 'partidos/detalle_partido.html'
    context_object_name = 'partido'
    pk_url_kwarg = 'pk' # Coincide con <uuid:pk> en tu URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partido = self.get_object()
        usuario_actual = self.request.user

        context['titulo_pagina'] = f"Detalles: {partido.cancha.nombre_cancha} - {partido.fecha.strftime('%d/%m %H:%M')}"
        context['es_creador'] = (partido.creador == usuario_actual)
        context['esta_inscrito'] = usuario_actual in partido.jugadores.all() # Verifica si el usuario está en el M2M
        context['inscripcion_esta_abierta'] = partido.inscripcion_abierta
        
        jugadores_inscritos_list = partido.jugadores.all().order_by('nombre')
        context['jugadores_inscritos_list'] = jugadores_inscritos_list
        context['plazas_disponibles'] = partido.max_jugadores - partido.jugadores.count()

        if context['es_creador'] and partido.estado == 'PROGRAMADO' and not partido.equipo_local:
            # Solo mostrar el form de asignación si el usuario es creador, el partido está programado
            # Y AÚN NO SE HAN ASIGNADO EQUIPOS PERMANENTES (si esa es la lógica que quieres)
            # O si quieres permitir re-asignar, quita la condición de not partido.equipo_local
            context['form_asignar_equipos'] = AsignarEquiposForm(
                jugadores_inscritos=jugadores_inscritos_list,
                partido=partido 
            )
        else:
            context['form_asignar_equipos'] = None
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
        
        # Si el partido ya tiene equipos permanentes asignados, no permitir re-asignar con este form
        if partido.equipo_local and partido.equipo_visitante and \
           partido.equipo_local.tipo_equipo == 'PERMANENTE' and partido.equipo_visitante.tipo_equipo == 'PERMANENTE':
            messages.info(request, "Este partido ya tiene equipos permanentes asignados. Para cambiar jugadores, edita los equipos directamente.")
            return redirect('detalle_partido', pk=partido.id_partido)


        form_asignar = AsignarEquiposForm(request.POST, jugadores_inscritos=partido.jugadores.all(), partido=partido)

        if form_asignar.is_valid():
            jugadores_equipo_local_ids = []
            jugadores_equipo_visitante_ids = []

            for jugador_obj in partido.jugadores.all():
                asignacion = form_asignar.cleaned_data.get(f'jugador_{jugador_obj.id}')
                if asignacion == 'local':
                    jugadores_equipo_local_ids.append(jugador_obj.id)
                elif asignacion == 'visitante':
                    jugadores_equipo_visitante_ids.append(jugador_obj.id)
            
            # Validación básica de número de jugadores (opcional, como dijiste que no por ahora)
            # if len(jugadores_equipo_local_ids) < 1 or len(jugadores_equipo_visitante_ids) < 1:
            #     messages.error(request, "Debes asignar al menos un jugador a cada equipo para guardar la formación.")
            #     context = self.get_context_data(**kwargs)
            #     context['form_asignar_equipos'] = form_asignar
            #     return self.render_to_response(context)

            # Crear o actualizar equipos de tipo 'PARTIDO'
            sufijo_nombre = f"{partido.cancha.nombre_cancha[:10]}_{partido.fecha.strftime('%d%m%y%H%M')}"

            # Equipo Local
            if partido.equipo_local and partido.equipo_local.tipo_equipo == 'PARTIDO':
                equipo_local = partido.equipo_local
            else:
                equipo_local = Equipo.objects.create(
                    nombre_equipo=f"Locales - {sufijo_nombre}",
                    capitan=partido.creador, tipo_equipo='PARTIDO'
                )
            equipo_local.jugadores.set(User.objects.filter(id__in=jugadores_equipo_local_ids))
            partido.equipo_local = equipo_local

            # Equipo Visitante
            if partido.equipo_visitante and partido.equipo_visitante.tipo_equipo == 'PARTIDO':
                equipo_visitante = partido.equipo_visitante
            else:
                equipo_visitante = Equipo.objects.create(
                    nombre_equipo=f"Visitantes - {sufijo_nombre}",
                    capitan=partido.creador, tipo_equipo='PARTIDO'
                )
            equipo_visitante.jugadores.set(User.objects.filter(id__in=jugadores_equipo_visitante_ids))
            partido.equipo_visitante = equipo_visitante
            
            partido.save()
            messages.success(request, "Equipos asignados correctamente al partido.")
            return redirect('detalle_partido', pk=partido.id_partido)
        else:
            context = self.get_context_data(**kwargs)
            context['form_asignar_equipos'] = form_asignar
            messages.error(request, "Hubo errores al asignar los equipos. Revisa las asignaciones.")
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
    











#EQUIPOS

class CrearEquipoPermanenteView(LoginRequiredMixin, CreateView):
    model = Equipo
    form_class = EquipoPermanenteForm
    template_name = 'equipos/crear_equipo_permanente.html' # Nueva plantilla
    # success_url = reverse_lazy('lista_mis_equipos') # O al detalle del equipo creado

    def form_valid(self, form):
        form.instance.capitan = self.request.user
        form.instance.tipo_equipo = 'PERMANENTE'
        form.instance.activo = True 
        
        self.object = form.save() # Guardar el equipo primero

        # Añadir al capitán como jugador del equipo
        self.object.jugadores.add(self.request.user)

        # Si tienes 'jugadores_iniciales' en el form:
        # jugadores_iniciales = form.cleaned_data.get('jugadores_iniciales')
        # if jugadores_iniciales:
        #     self.object.jugadores.add(*jugadores_iniciales)
        
        messages.success(self.request, f"¡Equipo '{self.object.nombre_equipo}' creado con éxito!")
        return redirect(reverse_lazy('detalle_equipo', kwargs={'pk': self.object.id_equipo}))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Crear Nuevo Equipo Permanente"
        return context

class MisEquiposListView(LoginRequiredMixin, ListView):
    model = Equipo
    template_name = 'equipos/mis_equipos_lista.html' # Nueva plantilla
    context_object_name = 'equipos_list'
    paginate_by = 10

    def get_queryset(self):
        # Equipos permanentes donde el usuario es capitán O es un jugador
        return Equipo.objects.filter(
            tipo_equipo='PERMANENTE',
            activo=True
        ).filter(
            Q(capitan=self.request.user) | Q(jugadores=self.request.user)
        ).distinct().order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Mis Equipos Permanentes"
        return context

class DetalleEquipoView(LoginRequiredMixin, DetailView):
    model = Equipo
    template_name = 'equipos/detalle_equipo.html' # Nueva plantilla
    context_object_name = 'equipo'
    pk_url_kwarg = 'pk' # Asumiendo que la URL usa <uuid:pk>

    def get_queryset(self):
        # Solo permitir ver equipos permanentes activos
        return super().get_queryset().filter(tipo_equipo='PERMANENTE', activo=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipo = self.get_object()
        context['titulo_pagina'] = f"Perfil del Equipo: {equipo.nombre_equipo}"
        context['es_capitan'] = (equipo.capitan == self.request.user)
        context['es_miembro'] = self.request.user in equipo.jugadores.all()
        # Aquí podrías añadir estadísticas del equipo, próximos partidos, etc.
        # context['partidos_jugados_equipo'] = Partido.objects.filter(Q(equipo_local=equipo) | Q(equipo_visitante=equipo), estado='FINALIZADO').order_by('-fecha')
        return context
    
# app/views.py
class EditarEquipoPermanenteView(LoginRequiredMixin, UpdateView):
    model = Equipo
    form_class = EquipoPermanenteForm # Puedes reusar el mismo form
    template_name = 'equipos/editar_equipo_permanente.html' # Nueva plantilla
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        # El capitán solo puede editar sus equipos permanentes y activos
        return super().get_queryset().filter(capitan=self.request.user, tipo_equipo='PERMANENTE', activo=True)

    def form_valid(self, form):
        messages.success(self.request, f"Equipo '{form.instance.nombre_equipo}' actualizado con éxito.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('detalle_equipo', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f"Editar Equipo: {self.object.nombre_equipo}"
        return context







    

#SECCIONES





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
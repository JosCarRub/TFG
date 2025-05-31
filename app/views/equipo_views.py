from django.views.generic import CreateView,UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from app.forms.equipo_forms import EquipoPermanenteForm
from app.models.equipo import Equipo
from app.models.user import User
#from django.contrib.auth import get_user_model; User = get_user_model()

class CrearEquipoPermanenteView(LoginRequiredMixin, CreateView):
    model = Equipo
    form_class = EquipoPermanenteForm
    template_name = 'equipos/crear_equipo_permanente.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user # Pasar usuario al form para filtrar miembros_iniciales
        return kwargs

    def form_valid(self, form):
        form.instance.capitan = self.request.user
        form.instance.tipo_equipo = 'PERMANENTE'
        form.instance.activo = True
        
        self.object = form.save() 
        self.object.jugadores.add(self.request.user) # El capitán es miembro

        miembros_iniciales = form.cleaned_data.get('miembros_iniciales')
        if miembros_iniciales:
            self.object.jugadores.add(*miembros_iniciales)
        
        messages.success(self.request, f"¡Equipo '{self.object.nombre_equipo}' creado con éxito!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('detalle_equipo', kwargs={'pk': self.object.id_equipo})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Crear Nuevo Equipo Permanente"
        return context

class MisEquiposListView(LoginRequiredMixin, ListView):
    model = Equipo
    template_name = 'equipos/mis_equipos_lista.html'
    context_object_name = 'equipos_list'
    paginate_by = 12

    def get_queryset(self):
        return Equipo.objects.filter(
            tipo_equipo='PERMANENTE',
            activo=True
        ).filter(
            Q(capitan=self.request.user) | Q(jugadores=self.request.user)
        ).distinct().order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Mis Equipos"
        return context

class DetalleEquipoView(LoginRequiredMixin, DetailView):
    model = Equipo
    template_name = 'equipos/detalle_equipo.html'
    context_object_name = 'equipo'
    pk_url_kwarg = 'pk' # Coincide con <uuid:pk> en tu URL

    def get_queryset(self):
        return super().get_queryset().filter(tipo_equipo='PERMANENTE', activo=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipo = self.get_object()
        context['titulo_pagina'] = f"Perfil del Equipo: {equipo.nombre_equipo}"
        context['es_capitan'] = (equipo.capitan == self.request.user)
        context['es_miembro'] = self.request.user in equipo.jugadores.all()
        # Aquí podrías añadir próximos partidos del equipo, historial, etc.
        # context['proximos_partidos_equipo'] = Partido.objects.filter(
        #     Q(equipo_local=equipo) | Q(equipo_visitante=equipo),
        #     estado='PROGRAMADO',
        #     fecha__gte=django_timezone.now()
        # ).order_by('fecha')[:5]
        return context

class EditarEquipoPermanenteView(LoginRequiredMixin, UpdateView):
    model = Equipo
    form_class = EquipoPermanenteForm
    template_name = 'equipos/editar_equipo_permanente.html'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        # Solo el capitán puede editar su equipo permanente y activo
        return super().get_queryset().filter(
            capitan=self.request.user, 
            tipo_equipo='PERMANENTE', 
            activo=True
        )
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user # Para el __init__ del form si es necesario
        # Para pre-rellenar miembros_iniciales en edición (si lo quieres permitir)
        # Si 'miembros_iniciales' es solo para la creación, no necesitas esto.
        # Si quieres permitir editar la lista de miembros aquí, el campo debería llamarse
        # 'jugadores' y usar un widget adecuado. Por ahora, EquipoPermanenteForm
        # tiene 'miembros_iniciales' que es más para la creación.
        # Para editar miembros, usualmente se hace en una sección separada de "Gestionar Miembros".
        return kwargs

    def form_valid(self, form):
        # La lógica de añadir/quitar jugadores al editar es más compleja
        # que solo usar form.cleaned_data.get('miembros_iniciales').
        # Por ahora, este form solo edita los campos básicos del equipo.
        # La gestión de miembros (añadir/quitar) se haría en otra vista/lógica.
        messages.success(self.request, f"Equipo '{form.instance.nombre_equipo}' actualizado con éxito.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('detalle_equipo', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f"Editar Equipo: {self.object.nombre_equipo}"
        return context

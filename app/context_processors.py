
def common_user_info(request):
    context = {}
    if request.user.is_authenticated:
        context['current_user_nombre'] = request.user.nombre
        context['current_user_posicion'] = request.user.get_posicion_display() if request.user.posicion else "Sin especificar"
        if request.user.imagen_perfil:
            context['current_user_avatar_url'] = request.user.imagen_perfil.url
        else:
            # Lógica para avatar por defecto según nivel
            
            if request.user.calificacion >= 1500:
                context['current_user_avatar_url'] = '/static/images/avatar_pro.png' 
            elif request.user.calificacion >= 1200:
                context['current_user_avatar_url'] = '/static/images/avatar_mid.png' 
            else:
                context['current_user_avatar_url'] = '/static/images/avatar_default.png' 
    return context
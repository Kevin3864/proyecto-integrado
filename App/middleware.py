from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from django.utils import timezone


class SessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Si el usuario NO está logueado → nada que hacer
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Obtiene el tiempo de última actividad guardado en la sesión
        last_activity = request.session.get("last_activity")
        now = timezone.now()

        # Tiempo máximo de inactividad (en segundos)
        max_idle_time = getattr(settings, "SESSION_COOKIE_AGE", 600)

        if last_activity:
            # Convertir string ISO a datetime
            last_activity_time = timezone.datetime.fromisoformat(last_activity)

            # Verificar si ya pasó más tiempo del permitido
            if (now - last_activity_time).total_seconds() > max_idle_time:
                # Limpiar sesión completa
                request.session.flush()

                # Mensaje de sesión expirada
                messages.error(
                    request,
                    getattr(settings, "SESSION_EXPIRED_MESSAGE",
                            "Tu sesión ha expirado por inactividad.")
                )

                return redirect("login")

        # Si todo está bien, actualizamos el timestamp
        request.session["last_activity"] = now.isoformat()

        return self.get_response(request)

"""
URL configuration for proyectoint project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
# Importamos las vistas de autenticación de Django
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # --- Panel de Administración ---
    path('admin/', admin.site.urls),

    # --- Rutas de la aplicación principal (App) ---
    path('', include('App.urls')),

    # --- AUTENTICACIÓN (Login / Logout) ---
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # --- RECUPERACIÓN DE CONTRASEÑA ---
    
    # 1. Formulario para solicitar el correo
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"), 
         name='password_reset'),

    # 2. Mensaje de confirmación de envío
    path('reset_password_sent/', 
         auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), 
         name='password_reset_done'),

    # 3. Link de cambio de contraseña (llega al correo)
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), 
         name='password_reset_confirm'),

    # 4. Mensaje de éxito al cambiar la contraseña
    path('reset_password_complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), 
         name='password_reset_complete'),
]

# --- Configuración para servir archivos multimedia en desarrollo (DEBUG=True) ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views


urlpatterns = [

    # ------------------------------
    # 1. HOME
    # ------------------------------
    path('', views.home, name='home'),


    # ------------------------------
    # 2. MOTORISTAS
    # ------------------------------
    path('motoristas/', views.listar_motoristas, name='listar_motoristas'),
    path('motorista/agregar/', views.agregar_motorista, name='agregar_motorista'),
    path('motorista/editar/<int:pk>/', views.editar_motorista, name='editar_motorista'),
    path('motorista/eliminar/<int:pk>/', views.eliminar_motorista, name='eliminar_motorista'),
    path('motorista/reemplazar/<int:pk>/', views.reemplazar_motorista, name='reemplazar_motorista'),


    # ------------------------------
    # 3. MOTOS
    # ------------------------------
    path('motos/', views.listar_motos, name='listar_motos'),
    path('moto/agregar/', views.agregar_moto, name='agregar_moto'),
    path('moto/editar/<int:pk>/', views.editar_moto, name='editar_moto'),
    path('moto/eliminar/<int:pk>/', views.eliminar_moto, name='eliminar_moto'),


    # ------------------------------
    # 4. FARMACIAS
    # ------------------------------
    path('farmacias/', views.listar_farmacias, name='listar_farmacias'),
    path('farmacia/agregar/', views.agregar_farmacia, name='agregar_farmacia'),
    path('farmacia/editar/<int:pk>/', views.editar_farmacia, name='editar_farmacia'),
    path('farmacia/eliminar/<int:pk>/', views.eliminar_farmacia, name='eliminar_farmacia'),


    # ------------------------------
    # 5. ASIGNACIONES
    # ------------------------------
    path('asignaciones/', views.listar_asignaciones, name='listar_asignaciones'),
    path('asignacion/agregar/', views.agregar_asignacion, name='agregar_asignacion'),
    path('asignacion/eliminar/<int:pk>/', views.eliminar_asignacion, name='eliminar_asignacion'),


    # ------------------------------
    # 6. MOVIMIENTOS
    # ------------------------------
    path('movimientos/', views.listar_movimientos, name='listar_movimientos'),
    path('movimientos/historial/', views.historial_movimientos, name='historial_movimientos'),

    path('movimiento/agregar/', views.agregar_movimiento, name='agregar_movimiento'),
    path('movimiento/editar/<int:pk>/', views.editar_movimiento, name='editar_movimiento'),
    path('movimiento/anular/<int:pk>/', views.anular_movimiento, name='anular_movimiento'),
    path('movimiento/reemplazar/<int:pk>/', views.reemplazar_movimiento, name='reemplazar_movimiento'),

    # Cambio de estado
    path('movimiento/cambiar_estado/<int:pk>/', views.cambiar_estado_movimiento, name='cambiar_estado_movimiento'),


    # ------------------------------
    # 7. REPORTES
    # ------------------------------
    path('reportes/', views.generar_reportes, name='generar_reportes'),
    path('reporte/<int:pk>/', views.ver_reporte_individual, name='ver_reporte_individual'),
    path('reporte/<int:pk>/pdf/', views.reporte_individual_pdf, name='reporte_individual_pdf'),

]

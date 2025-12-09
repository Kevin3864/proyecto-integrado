from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone 
from datetime import datetime
# --- ¡IMPORTADO! ---
from django.contrib.auth.decorators import login_required # <-- Mejor Práctica: Seguridad (Patrón 1)
from django.db.models import Count # Para los reportes
from .models import (
    Motorista, Moto, Farmacia, TipoMovimiento, Asignacion, Movimiento,
    Region, Provincia, Comuna
)
from django.db.models import Q # <-- Mejor Práctica: Para consultas complejas (OR)

from .forms import (
    MotoristaForm, MotoForm, FarmaciaForm, AsignacionForm, MovimientoForm, 
    ReemplazoMovimientoForm, CambioEstadoForm, ReporteForm
)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse



# --- Vista Principal (Ahora protegida) ---
@login_required
def home(request):
    """
    Renderiza la página de inicio (lobby/dashboard) de la aplicación.
    Solo accesible para usuarios autenticados.
    
    Template: templatesApp/home.html
    """
    context = {
        'titulo': 'Administracion'
    }
    return render(request, 'templatesApp/home.html', context)

# --- Mantenedor de Motoristas ---
@login_required
def listar_motoristas(request):
    """
    Muestra la lista de todos los motoristas que están 'esta_activo'=True.
    Incluye una barra de búsqueda que filtra por múltiples campos (Q objects).
    
    Template: templatesApp/listar_motoristas.html
    """
    query = request.GET.get('q', '') 
    
    # Mejor Práctica: El queryset base filtra por motoristas activos
    motoristas = Motorista.objects.filter(esta_activo=True) 

    if query:
        # Mejor Práctica: Se usa Q objects para filtros complejos (OR)
        motoristas = motoristas.filter(
            Q(nombres__icontains=query) | 
            Q(apellido_paterno__icontains=query) |
            Q(apellido_materno__icontains=query) | 
            Q(email__icontains=query) |
            Q(rut__icontains=query)
        )
    
    context = {
        'motoristas': motoristas.order_by('nombres'),
        'query': query 
    }
    return render(request, 'templatesApp/listar_motoristas.html', context)

@login_required
def agregar_motorista(request):
    """
    Maneja la creación de un nuevo motorista.
    - GET: Muestra el formulario 'MotoristaForm'.
    - POST: Valida y guarda el nuevo motorista.
    
    Template: templatesApp/agregar.html
    """
    if request.method == 'POST':
        # Se incluye request.FILES para manejar la subida de 'licencia_archivo'
        form = MotoristaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Motorista agregado exitosamente!')
            return redirect('listar_motoristas')
    else:
        # Es un GET, se crea un formulario vacío
        form = MotoristaForm()
        
    context = {
        'form': form, 
        'titulo': 'Agregar Motorista'
    }
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def editar_motorista(request, pk):
    """
    Maneja la edición de un motorista existente (identificado por su pk).
    - GET: Muestra el 'MotoristaForm' pre-rellenado con los datos del motorista.
    - POST: Valida y guarda los cambios.
    
    Template: templatesApp/agregar.html
    """
    # get_object_or_404 es una Mejor Práctica: maneja el error si el ID no existe
    motorista = get_object_or_404(Motorista, pk=pk)
    
    if request.method == 'POST':
        # Se pasa 'instance=motorista' para indicarle a Django que es una edición
        form = MotoristaForm(request.POST, request.FILES, instance=motorista)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Motorista {motorista.nombres} actualizado exitosamente!')
            return redirect('listar_motoristas')
    else:
        # Es un GET, se muestra el formulario con los datos actuales
        form = MotoristaForm(instance=motorista)
        
    context = {
        'form': form, 
        'titulo': f'Editar Motorista: {motorista.nombres} {motorista.apellido_paterno}'
    }
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def eliminar_motorista(request, pk):
    """
    Maneja la eliminación (borrado físico) de un motorista.
    - GET: Muestra la página de confirmación.
    - POST: Elimina el registro de la base de datos.
    
    Template: templatesApp/confirmar_eliminar.html
    """
    motorista = get_object_or_404(Motorista, pk=pk)
    
    if request.method == 'POST':
        nombre = f"{motorista.nombres} {motorista.apellido_paterno}" # Guardar nombre para el mensaje
        motorista.delete() # Borrado físico
        messages.warning(request, f'Motorista {nombre} ha sido eliminado.')
        return redirect('listar_motoristas')
        
    context = {
        'objeto': motorista, 
        'tipo': 'Motorista', 
        'url_lista': 'listar_motoristas'
    }
    return render(request, 'templatesApp/confirmar_eliminar.html', context)

# --- Mantenedor de Motos ---
# (Las vistas de Moto, Farmacia y Asignacion siguen el mismo patrón CRUD:
# Listar, Agregar, Editar, Eliminar)
@login_required
def listar_motos(request):
    """
    Muestra la lista de todas las motos con filtro de búsqueda.
    Template: templatesApp/listar_motos.html
    """
    query = request.GET.get('q', '')
    if query:
        motos = Moto.objects.filter(Q(patente__icontains=query) | Q(modelo__icontains=query))
    else:
        motos = Moto.objects.all()
    context = {'motos': motos, 'query': query}
    return render(request, 'templatesApp/listar_motos.html', context)

@login_required
def agregar_moto(request):
    """
    Maneja la creación de una nueva moto.
    Template: templatesApp/agregar.html
    """
    if request.method == 'POST':
        form = MotoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Moto agregada exitosamente!')
            return redirect('listar_motos')
    else:
        form = MotoForm()
    context = {'form': form, 'titulo': 'Agregar Moto'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def editar_moto(request, pk):
    """
    Maneja la edición de una moto existente.
    Template: templatesApp/agregar.html
    """
    moto = get_object_or_404(Moto, pk=pk)
    if request.method == 'POST':
        form = MotoForm(request.POST, instance=moto)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Moto {moto.patente} actualizada exitosamente!')
            return redirect('listar_motos')
    else:
        form = MotoForm(instance=moto)
    context = {'form': form, 'titulo': f'Editar Moto: {moto.patente}'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def eliminar_moto(request, pk):
    """
    Maneja la eliminación de una moto.
    Template: templatesApp/confirmar_eliminar.html
    """
    moto = get_object_or_404(Moto, pk=pk)
    if request.method == 'POST':
        patente = moto.patente
        moto.delete()
        messages.warning(request, f'Moto {patente} ha sido eliminada.')
        return redirect('listar_motos')
    context = {'objeto': moto, 'tipo': 'Moto', 'url_lista': 'listar_motos'}
    return render(request, 'templatesApp/confirmar_eliminar.html', context)

# --- Mantenedor de Farmacias ---
@login_required
def listar_farmacias(request):
    """
    Muestra la lista de todas las farmacias con filtro de búsqueda.
    Template: templatesApp/listar_farmacias.html
    """
    query = request.GET.get('q', '')
    if query:
        farmacias = Farmacia.objects.filter(Q(nombre__icontains=query) | Q(direccion__icontains=query))
    else:
        farmacias = Farmacia.objects.all()
    context = {'farmacias': farmacias, 'query': query}
    return render(request, 'templatesApp/listar_farmacias.html', context)

@login_required
def agregar_farmacia(request):
    """
    Maneja la creación de una nueva farmacia, usando el FarmaciaForm
    que incluye la lógica de selección de Región/Provincia.
    Template: templatesApp/agregar.html
    """
    if request.method == 'POST':
        form = FarmaciaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Farmacia agregada exitosamente!')
            return redirect('listar_farmacias')
    else:
        form = FarmaciaForm()
    context = {'form': form, 'titulo': 'Agregar Farmacia'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def editar_farmacia(request, pk):
    """
    Maneja la edición de una farmacia existente.
    Template: templatesApp/agregar.html
    """
    farmacia = get_object_or_404(Farmacia, pk=pk)
    if request.method == 'POST':
        form = FarmaciaForm(request.POST, instance=farmacia)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Farmacia {farmacia.nombre} actualizada exitosamente!')
            return redirect('listar_farmacias')
    else:
        form = FarmaciaForm(instance=farmacia)
    context = {'form': form, 'titulo': f'Editar Farmacia: {farmacia.nombre}'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def eliminar_farmacia(request, pk):
    """
    Maneja la eliminación de una farmacia.
    Template: templatesApp/confirmar_eliminar.html
    """
    farmacia = get_object_or_404(Farmacia, pk=pk)
    if request.method == 'POST':
        nombre = farmacia.nombre
        farmacia.delete()
        messages.warning(request, f'Farmacia {nombre} ha sido eliminada.')
        return redirect('listar_farmacias')
    context = {'objeto': farmacia, 'tipo': 'Farmacia', 'url_lista': 'listar_farmacias'}
    return render(request, 'templatesApp/confirmar_eliminar.html', context)

# --- VISTAS PARA ASIGNACIONES ---
@login_required
def listar_asignaciones(request):
    """
    Muestra la relación Muchos-a-Muchos entre Motoristas y Farmacias.
    Template: templatesApp/listar_asignaciones.html
    """
    # Mejor Práctica: select_related optimiza la consulta para obtener
    # los datos de motorista y farmacia en una sola query.
    asignaciones = Asignacion.objects.select_related('motorista', 'farmacia').all()
    context = {'asignaciones': asignaciones, 'titulo': 'Gestión de Asignaciones'}
    return render(request, 'templatesApp/listar_asignaciones.html', context)

@login_required
def agregar_asignacion(request):
    """
    Maneja la creación de una nueva asignación Motorista-Farmacia.
    Template: templatesApp/agregar.html
    """
    if request.method == 'POST':
        form = AsignacionForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, '¡Asignación guardada exitosamente!')
                return redirect('listar_asignaciones')
            except Exception as e:
                # Captura el error si se viola el 'unique_together'
                form.add_error(None, f"Error al guardar: Esta asignación ya existe.")
    else:
        form = AsignacionForm()
    context = {'form': form, 'titulo': 'Agregar Asignación'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def eliminar_asignacion(request, pk):
    """
    Maneja la eliminación de una asignación.
    Template: templatesApp/confirmar_eliminar.html
    """
    asignacion = get_object_or_404(Asignacion, pk=pk)
    if request.method == 'POST':
        asignacion.delete()
        messages.warning(request, 'Asignación eliminada.')
        return redirect('listar_asignaciones')
    context = {'objeto': asignacion, 'tipo': 'Asignación', 'url_lista': 'listar_asignaciones'}
    return render(request, 'templatesApp/confirmar_eliminar.html', context)

# --- VISTAS PARA MOVIMIENTOS ---
@login_required
def listar_movimientos(request):
    """
    Vista principal de operaciones. Muestra la lista de movimientos ACTIVOS
    (excluyendo 'anulado') y permite filtrar por ubicación.
    
    Mejor Práctica:
    - select_related: Optimiza la consulta de farmacia y sus relaciones.
    - Filtros Dependientes: La lógica carga solo las provincias/comunas
      relevantes a la selección del usuario.
    
    Template: templatesApp/listar_movimientos.html
    """
    
    # 1. Obtener los valores de los filtros (si existen)
    region_id = request.GET.get('region')
    provincia_id = request.GET.get('provincia')
    comuna_id = request.GET.get('comuna')

    # 2. Queryset base (sin anular)
    #    Mejor Práctica: select_related para optimizar.
    movimientos = Movimiento.objects.select_related(
        'farmacia__comuna__provincia__region', 'motorista', 'tipo_movimiento'
    ).exclude(status='anulado')

    # 3. Aplicar filtros a los movimientos
    #    Se usa la relación anidada (farmacia__comuna__provincia_id)
    if comuna_id:
        movimientos = movimientos.filter(farmacia__comuna_id=comuna_id)
    elif provincia_id:
        movimientos = movimientos.filter(farmacia__comuna__provincia_id=provincia_id)
    elif region_id:
        movimientos = movimientos.filter(farmacia__comuna__provincia__region_id=region_id)
    
    # --- Lógica de Filtros Dependientes ---
    regiones = Region.objects.all().order_by('nombre')
    provincias = Provincia.objects.none() # Vacío por defecto
    comunas = Comuna.objects.none()     # Vacío por defecto

    if region_id:
        # Si hay región, carga solo sus provincias
        provincias = Provincia.objects.filter(region_id=region_id).order_by('nombre')
    if provincia_id:
        # Si hay provincia, carga solo sus comunas
        comunas = Comuna.objects.filter(provincia_id=provincia_id).order_by('nombre')
    # --- Fin Lógica de Filtros ---
    
    context = {
        'movimientos': movimientos.order_by('-fecha_hora'),
        'titulo': 'Listado General de Movimientos',
        'regiones': regiones, 'provincias': provincias, 'comunas': comunas,
        'selected_region': int(region_id) if region_id else None,
        'selected_provincia': int(provincia_id) if provincia_id else None,
        'selected_comuna': int(comuna_id) if comuna_id else None,
    }
    return render(request, 'templatesApp/listar_movimientos.html', context)

@login_required
def historial_movimientos(request):
    """
    Muestra TODOS los movimientos (incluidos 'anulado') en modo solo lectura.
    Permite filtrar por Farmacia (Origen o Destino) y por Rango de Fechas.
    
    Template: templatesApp/historial_movimientos.html
    """
    # 1. Obtener valores de filtro
    farmacia_id = request.GET.get('farmacia_id')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # 2. Queryset base (todos los movimientos)
    movimientos = Movimiento.objects.select_related(
        'farmacia', 'farmacia_destino', 'motorista', 'tipo_movimiento'
    ).all()
    
    # 3. Aplicar filtros
    if farmacia_id:
        # Mejor Práctica: Q object para buscar en Origen O Destino
        movimientos = movimientos.filter(
            Q(farmacia_id=farmacia_id) | Q(farmacia_destino_id=farmacia_id)
        )
    if fecha_desde:
        # '__gte' = "greater than or equal to" (mayor o igual que)
        movimientos = movimientos.filter(fecha_hora__gte=fecha_desde) 
    if fecha_hasta:
        # '__lte' = "less than or equal to" (menor o igual que)
        # Se añade T23:59:59 para incluir el día completo
        movimientos = movimientos.filter(fecha_hora__lte=f'{fecha_hasta}T23:59:59')

    # 4. Obtener datos para los menús del filtro
    farmacias_para_filtro = Farmacia.objects.all().order_by('nombre')
    
    context = {
        'movimientos': movimientos.order_by('-fecha_hora'),
        'titulo': 'Historial General de Movimientos',
        'farmacias_para_filtro': farmacias_para_filtro,
        'filtro_farmacia_id': int(farmacia_id) if farmacia_id else None,
        'filtro_fecha_desde': fecha_desde,
        'filtro_fecha_hasta': fecha_hasta,
    }
    return render(request, 'templatesApp/historial_movimientos.html', context)


@login_required
def agregar_movimiento(request):
    """
    Maneja la creación de un nuevo movimiento.
    Implementa la lógica de negocio de "Disponibilidad de Motorista".
    
    Template: templatesApp/agregar.html
    """
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            form.save() # El 'default' en el modelo lo pondrá 'en_ruta'
            messages.success(request, '¡Movimiento registrado exitosamente!')
            return redirect('listar_movimientos')
    else:
        # --- Lógica de Negocio: Disponibilidad ---
        # 1. Comprueba si hay motoristas disponibles ANTES de mostrar el formulario.
        # (La lógica de filtro está en el __init__ de MovimientoForm)
        form = MovimientoForm()
        
        # 2. Si el queryset filtrado (en el forms.py) está vacío
        if not form.fields['motorista'].queryset.exists():
            messages.error(request, 'No hay motoristas disponibles para registrar un nuevo movimiento. Todos están "En Ruta".')
            return redirect('listar_movimientos') # Regresa a la lista con el error
        # --- Fin Lógica de Negocio ---

    context = {'form': form, 'titulo': 'Registrar Nuevo Movimiento'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def editar_movimiento(request, pk):
    """
    Maneja la edición de un movimiento (ej. cambiar observación o motorista).
    La lógica de disponibilidad de motorista también aplica aquí (en el 'forms.py').
    
    Template: templatesApp/agregar.html
    """
    movimiento = get_object_or_404(Movimiento, pk=pk)
    if request.method == 'POST':
        form = MovimientoForm(request.POST, instance=movimiento)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Movimiento actualizado exitosamente!')
            return redirect('listar_movimientos')
    else:
        form = MovimientoForm(instance=movimiento)
    context = {'form': form, 'titulo': f'Editar Movimiento (ID: {movimiento.pk})'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def anular_movimiento(request, pk):
    """
    Maneja la anulación de un movimiento (cambio de estado a 'anulado').
    No es un borrado físico (DELETE), es un borrado lógico (UPDATE).
    
    Template: templatesApp/confirmar_eliminar.html
    """
    movimiento = get_object_or_404(Movimiento, pk=pk)
    
    # --- Lógica de Negocio: Reglas de Anulación ---
    # No se puede anular un movimiento que ya está finalizado.
    estados_no_anulables = ['entregado', 'fallido', 'anulado']
    if movimiento.status in estados_no_anulables:
        messages.error(request, f'No se puede anular un movimiento que ya está "{movimiento.get_status_display()}".')
        return redirect('listar_movimientos')
    
    # Si pasa el filtro, significa que es 'en_ruta' y se puede anular.
    if request.method == 'POST':
        movimiento.status = 'anulado'
        
        # Mejor Práctica: Guardar registro de quién y cuándo anuló
        fecha_hora_actual = timezone.now().strftime("%d/%m/%Y %H:%M")
        usuario = request.user.username if request.user.is_authenticated else 'sistema'
        nota = f"\n[ANULADO {fecha_hora_actual} por {usuario}]"
        
        if movimiento.observacion: movimiento.observacion += nota
        else: movimiento.observacion = nota
        movimiento.save() # Guarda el nuevo estado y la observación
        
        messages.warning(request, f'El Movimiento #{movimiento.pk} ha sido anulado.')
        return redirect('listar_movimientos')
    
    context = {
        'objeto': movimiento, 
        'tipo': f'Movimiento #{movimiento.pk} (Anular)', 
        'url_lista': 'listar_movimientos'
    }
    return render(request, 'templatesApp/confirmar_eliminar.html', context)

@login_required
def reemplazar_motorista(request, pk):
    """
    Vista para la Gestión de Motoristas (Mantenedor).
    Desactiva un motorista ('esta_activo' = False) y crea uno nuevo,
    vinculándolos a través del campo 'reemplaza_a'.
    
    Template: templatesApp/agregar.html
    """
    motorista_original = get_object_or_404(Motorista, pk=pk)

    if request.method == 'POST':
        form = MotoristaForm(request.POST, request.FILES) 
        if form.is_valid():
            # 1. Guarda el nuevo motorista
            nuevo_motorista = form.save(commit=False)
            nuevo_motorista.reemplaza_a = motorista_original # Asigna la relación
            nuevo_motorista.esta_activo = True 
            nuevo_motorista.save() 

            # 2. Desactiva el motorista original
            motorista_original.esta_activo = False
            motorista_original.save()

            messages.success(request, f'Motorista {nuevo_motorista.nombres} ha reemplazado exitosamente a {motorista_original.nombres}.')
            return redirect('listar_motoristas')
    else:
        form = MotoristaForm() # Formulario vacío para el nuevo motorista

    context = {
        'form': form,
        'titulo': f'Reemplazar a: {motorista_original.nombres} {motorista_original.apellido_paterno}',
        'subtitulo': 'Se creará un nuevo motorista y se desactivará el original.'
    }
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def reemplazar_movimiento(request, pk):
    """
    Vista para la Gestión de Movimientos (Operación).
    Cambia el 'motorista_id' de un movimiento 'en_ruta' por otro disponible.
    
    Template: templatesApp/reemplazar_movimiento.html
    """
    movimiento = get_object_or_404(Movimiento, pk=pk)
    motorista_original = movimiento.motorista

    # --- Lógica de Negocio: Reglas de Reemplazo ---
    estados_no_reemplazables = ['entregado', 'fallido', 'anulado']
    if movimiento.status in estados_no_reemplazables:
        messages.error(request, f'No se puede reemplazar el motorista de un movimiento que ya está "{movimiento.get_status_display()}".')
        return redirect('listar_movimientos')

    if request.method == 'POST':
        # Se pasa 'instance=movimiento' para que el form actualice este objeto
        form = ReemplazoMovimientoForm(request.POST, instance=movimiento)
        
        if form.is_valid():
            nuevo_movimiento = form.save(commit=False) 
            
            # Mejor Práctica: Guardar historial del reemplazo
            nuevo_movimiento.motorista_original = motorista_original
            fecha_hora_actual = timezone.now().strftime("%d/%m/%Y %H:%M")
            nota = f"\n[REEMPLAZO {fecha_hora_actual}: {motorista_original.nombres} -> {nuevo_movimiento.motorista.nombres}]"
            
            if nuevo_movimiento.observacion: nuevo_movimiento.observacion += nota
            else: nuevo_movimiento.observacion = nota
            nuevo_movimiento.save()
            
            messages.success(request, f'Se ha reemplazado a {motorista_original.nombres} por {nuevo_movimiento.motorista.nombres} en el movimiento.')
            return redirect('listar_movimientos')
    
    else: # request.method == 'GET'
        # --- Lógica de Negocio: Disponibilidad ---
        # Comprueba si hay motoristas disponibles ANTES de mostrar el formulario.
        form = ReemplazoMovimientoForm(instance=movimiento)
        
        try:
            # (La lógica de filtro está en el __init__ de ReemplazoMovimientoForm)
            if not form.fields['motorista'].queryset.exists():
                messages.error(request, f'No hay motoristas disponibles para reemplazar a {motorista_original.nombres} en este momento.')
                return redirect('listar_movimientos')
        except Exception as e:
            messages.error(request, f'Error al filtrar motoristas disponibles: {e}')
            return redirect('listar_movimientos')

    context = {
        'form': form, 
        'titulo': f'Reemplazar Motorista del Movimiento #{movimiento.pk}',
        'subtitulo': f'Original: {motorista_original.nombres} | Farmacia: {movimiento.farmacia.nombre}'
    }
    return render(request, 'templatesApp/reemplazar_movimiento.html', context)


@login_required
def cambiar_estado_movimiento(request, pk):
    """
    Recibe el POST del modal (pop-up) para cambiar el estado 
    de un movimiento ('en_ruta' -> 'entregado' / 'fallido').
    
    Esta vista no renderiza un template, solo procesa el POST y redirige.
    """
    movimiento = get_object_or_404(Movimiento, pk=pk)
    
    if request.method == 'POST':
        form = CambioEstadoForm(request.POST, instance=movimiento)
        
        if form.is_valid():
            # Mejor Práctica: Guardar registro de quién y cuándo cambió el estado
            nuevo_estado = form.cleaned_data['status']
            fecha_hora_actual = timezone.now().strftime("%d/%m/%Y %H:%M")
            usuario = request.user.username if request.user.is_authenticated else 'sistema'
            nota = f"\n[ESTADO CAMBIADO A: {nuevo_estado.upper()} por {usuario}]"

            movimiento = form.save(commit=False)
            if movimiento.observacion: movimiento.observacion += nota
            else: movimiento.observacion = nota
            movimiento.save() # Guarda estado Y observación
            
            messages.success(request, f'El estado del Movimiento #{movimiento.pk} ha sido actualizado a "{movimiento.get_status_display()}".')
        
        else:
            # Si el formulario falla (ej. estado inválido), informa el error
            errores = form.errors.as_text()
            messages.error(request, f'Error al cambiar el estado del Movimiento #{movimiento.pk}: {errores}')

    # Redirige siempre a la lista de movimientos (en caso de GET o POST)
    return redirect('listar_movimientos')

# --- VISTA DE REPORTES ---

# -----------------------------
#   IMPORTACIONES DE REPORTES
# -----------------------------
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.http import HttpResponse
import datetime


# -----------------------------
#   GENERADOR DE REPORTES
# -----------------------------
@login_required
def generar_reportes(request):
    fecha_hoy = timezone.now().date()
    qs = Movimiento.objects.all()

    titulo_reporte = f"Reporte Anual: {fecha_hoy.year}"
    form = ReporteForm(request.GET)

    if form.is_valid():
        tipo = form.cleaned_data['tipo_reporte']
        fecha = form.cleaned_data['fecha']

        # -------- REPORTE DIARIO --------
        if tipo == 'diario':
            inicio = timezone.make_aware(
                datetime.datetime.combine(fecha, datetime.time.min)
            )
            fin = timezone.make_aware(
                datetime.datetime.combine(fecha, datetime.time.max)
            )
            qs = qs.filter(fecha_hora__range=(inicio, fin))
            titulo_reporte = f"Reporte Diario: {fecha.strftime('%d/%m/%Y')}"

        # -------- REPORTE MENSUAL --------
        elif tipo == 'mensual':
            from calendar import monthrange
            anio, mes = fecha.year, fecha.month
            ultimo_dia = monthrange(anio, mes)[1]

            inicio = timezone.make_aware(datetime.datetime(anio, mes, 1, 0, 0))
            fin = timezone.make_aware(datetime.datetime(anio, mes, ultimo_dia, 23, 59, 59))

            qs = qs.filter(fecha_hora__range=(inicio, fin))
            titulo_reporte = f"Reporte Mensual: {fecha.strftime('%B %Y')}"

        # -------- REPORTE ANUAL --------
        else:
            qs = qs.filter(fecha_hora__year=fecha.year)
            titulo_reporte = f"Reporte Anual: {fecha.year}"

    else:
        qs = qs.filter(fecha_hora__year=fecha_hoy.year)
        form = ReporteForm(initial={'tipo_reporte': 'anual', 'fecha': fecha_hoy})

    # ----- Filtros geográficos -----
    region_id = request.GET.get('region')
    provincia_id = request.GET.get('provincia')
    comuna_id = request.GET.get('comuna')

    if comuna_id:
        qs = qs.filter(farmacia__comuna_id=comuna_id)
    elif provincia_id:
        qs = qs.filter(farmacia__comuna__provincia_id=provincia_id)
    elif region_id:
        qs = qs.filter(farmacia__comuna__provincia__region_id=region_id)

    regiones = Region.objects.all().order_by('nombre')
    provincias = Provincia.objects.none()
    comunas = Comuna.objects.none()

    if region_id:
        provincias = Provincia.objects.filter(region_id=region_id)
    if provincia_id:
        comunas = Comuna.objects.filter(provincia_id=provincia_id)

    total_movimientos = qs.count()
    resumen_estados = qs.values('status').annotate(total=Count('id'))
    resumen_tipos = qs.values('tipo_movimiento__nombre').annotate(total=Count('id'))

    movimientos = qs.select_related('motorista', 'farmacia', 'tipo_movimiento').order_by('-fecha_hora')

    return render(request, 'templatesApp/reportes.html', {
        'form': form,
        'movimientos': movimientos,
        'total_movimientos': total_movimientos,
        'resumen_estados': resumen_estados,
        'resumen_tipos': resumen_tipos,
        'titulo_reporte': titulo_reporte,
        'titulo': 'Generador de Reportes',
        'regiones': regiones,
        'provincias': provincias,
        'comunas': comunas,
        'selected_region': int(region_id) if region_id else None,
        'selected_provincia': int(provincia_id) if provincia_id else None,
        'selected_comuna': int(comuna_id) if comuna_id else None,
    })


# -----------------------------
#   REPORTE INDIVIDUAL (HTML)
# -----------------------------
@login_required
def ver_reporte_individual(request, pk):
    mov = Movimiento.objects.select_related(
        'motorista',
        'farmacia',
        'tipo_movimiento',
        'motorista_original',
        'farmacia_destino'
    ).get(pk=pk)

    moto = mov.motorista.motos_asignadas.first()

    return render(request, 'templatesApp/ver_reporte_individual.html', {
        'mov': mov,
        'moto': moto,
        'titulo': f"Reporte del Movimiento #{mov.pk}"
    })


# -----------------------------
#   REPORTE INDIVIDUAL PDF
# -----------------------------
@login_required
def reporte_individual_pdf(request, pk):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    mov = Movimiento.objects.select_related(
        'motorista', 'farmacia', 'tipo_movimiento',
        'motorista_original', 'farmacia_destino'
    ).get(pk=pk)

    moto = mov.motorista.motos_asignadas.first()
    farmacia = mov.farmacia

    comuna = farmacia.comuna.nombre if farmacia.comuna else "—"
    provincia = farmacia.comuna.provincia.nombre if farmacia.comuna and farmacia.comuna.provincia else "—"
    region = farmacia.comuna.provincia.region.nombre if farmacia.comuna and farmacia.comuna.provincia and farmacia.comuna.provincia.region else "—"

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename=\"reporte_movimiento_{mov.pk}.pdf\"'

    pdf = SimpleDocTemplate(response, pagesize=letter, leftMargin=40, rightMargin=40)
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_bold = styles['Heading4']

    elements = []

    # ===============================
    #      TÍTULO PRINCIPAL
    # ===============================
    elements.append(Paragraph(f"<b>Reporte Individual — Movimiento #{mov.pk}</b>", styles['Title']))
    elements.append(Spacer(1, 0.25 * inch))

    # ===============================
    #      INFORMACIÓN GENERAL
    # ===============================
    elements.append(Paragraph("<b>Información General</b>", style_bold))
    elements.append(Spacer(1, 0.1 * inch))

    info_general = [
        ["ID Movimiento", str(mov.pk)],
        ["Estado", mov.get_status_display()],
        ["Tipo de Movimiento", mov.tipo_movimiento.nombre],
        ["Fecha y Hora", mov.fecha_hora.strftime("%d/%m/%Y %H:%M:%S")],
    ]

    table_general = Table(info_general, colWidths=[150, 350])
    table_general.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))

    elements.append(table_general)
    elements.append(Spacer(1, 0.3 * inch))

    # ===============================
    #       MOTORISTA / MOTO
    # ===============================
    elements.append(Paragraph("<b>Motorista / Vehículo</b>", style_bold))
    elements.append(Spacer(1, 0.1 * inch))

    info_motorista = [
        ["Motorista", f"{mov.motorista.nombres} {mov.motorista.apellido_paterno or ''}".strip()],
        ["Moto", f"{moto.patente} — {moto.modelo}" if moto else "Sin moto asignada"],
    ]

    table_motorista = Table(info_motorista, colWidths=[150, 350])
    table_motorista.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))

    elements.append(table_motorista)
    elements.append(Spacer(1, 0.3 * inch))

    # ===============================
    #        UBICACIÓN ORIGEN
    # ===============================
    elements.append(Paragraph("<b>Origen / Ubicación</b>", style_bold))
    elements.append(Spacer(1, 0.1 * inch))

    info_origen = [
        ["Farmacia Origen", farmacia.nombre],
        ["Dirección", farmacia.direccion],
        ["Teléfono", farmacia.telefono or "—"],
        ["Comuna", comuna],
        ["Provincia", provincia],
        ["Región", region],
    ]

    table_origen = Table(info_origen, colWidths=[150, 350])
    table_origen.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))

    elements.append(table_origen)
    elements.append(Spacer(1, 0.3 * inch))

    # ===============================
    #        DESTINO SI APLICA
    # ===============================
    if mov.farmacia_destino:
        fd = mov.farmacia_destino
        comuna_d = fd.comuna.nombre if fd.comuna else "—"
        provincia_d = fd.comuna.provincia.nombre if fd.comuna and fd.comuna.provincia else "—"
        region_d = fd.comuna.provincia.region.nombre if fd.comuna and fd.comuna.provincia and fd.comuna.provincia.region else "—"

        elements.append(Paragraph("<b>Destino (Traslado)</b>", style_bold))
        elements.append(Spacer(1, 0.1 * inch))

        info_destino = [
            ["Farmacia Destino", fd.nombre],
            ["Dirección", fd.direccion],
            ["Comuna", comuna_d],
            ["Provincia", provincia_d],
            ["Región", region_d],
        ]

        table_destino = Table(info_destino, colWidths=[150, 350])
        table_destino.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))

        elements.append(table_destino)
        elements.append(Spacer(1, 0.3 * inch))

    # ===============================
    #        OBSERVACIÓN
    # ===============================
    if mov.observacion:
        elements.append(Paragraph("<b>Observación</b>", style_bold))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(mov.observacion.replace("\n", "<br/>"), style_normal))
        elements.append(Spacer(1, 0.3 * inch))

    pdf.build(elements)
    return response

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone 
# --- ¡IMPORTADO! ---
from django.contrib.auth.decorators import login_required # <-- Mejor Práctica: Seguridad (Patrón 1)
from .models import (
    Motorista, Moto, Farmacia, TipoMovimiento, Asignacion, Movimiento,
    Region, Provincia, Comuna
)
from django.db.models import Q # <-- Mejor Práctica: Para consultas complejas (OR)

from .forms import (
    MotoristaForm, MotoForm, FarmaciaForm, AsignacionForm, MovimientoForm, 
    ReemplazoMovimientoForm, CambioEstadoForm,
)

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

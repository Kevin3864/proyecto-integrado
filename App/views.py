from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone 
# --- ¡IMPORTADO! ---
from django.contrib.auth.decorators import login_required # <-- Para proteger las vistas
from .models import (
    Motorista, Moto, Farmacia, TipoMovimiento, Asignacion, Movimiento,
    Region, Provincia, Comuna
)
from django.db.models import Q

from .forms import (
    MotoristaForm, MotoForm, FarmaciaForm, AsignacionForm, MovimientoForm, 
    ReemplazoMovimientoForm, CambioEstadoForm,
)

# --- Vista Principal (Ahora protegida) ---
@login_required
def home(request):
    context = {
        'titulo': 'Administracion'
    }
    return render(request, 'templatesApp/home.html', context)

# --- Mantenedor de Motoristas ---
@login_required
def listar_motoristas(request):
    query = request.GET.get('q', '') 
    motoristas = Motorista.objects.filter(esta_activo=True) 
    if query:
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
    if request.method == 'POST':
        form = MotoristaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Motorista agregado exitosamente!')
            return redirect('listar_motoristas')
    else:
        # --- Lógica de Comprobación Añadida ---
        # (Esto es de una corrección anterior, se mantiene)
        ocupados_pks = Movimiento.objects.filter(status='en_ruta').values_list('motorista_id', flat=True).distinct()
        disponibles = Motorista.objects.filter(esta_activo=True).exclude(pk__in=ocupados_pks)
        if not disponibles.exists():
            messages.error(request, 'No hay motoristas disponibles para registrar un nuevo motorista. Todos están "En Ruta".')
            return redirect('listar_motoristas')
        form = MotoristaForm()
        # --- Fin Lógica Añadida ---

    context = {'form': form, 'titulo': 'Agregar Motorista'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def editar_motorista(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    if request.method == 'POST':
        form = MotoristaForm(request.POST, request.FILES, instance=motorista)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Motorista {motorista.nombres} actualizado exitosamente!')
            return redirect('listar_motoristas')
    else:
        form = MotoristaForm(instance=motorista)
    context = {'form': form, 'titulo': f'Editar Motorista: {motorista.nombres} {motorista.apellido_paterno}'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def eliminar_motorista(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    nombre = f"{motorista.nombres} {motorista.apellido_paterno}"
    if request.method == 'POST':
        motorista.delete()
        messages.warning(request, f'Motorista {nombre} ha sido eliminado.')
        return redirect('listar_motoristas')
    context = {'objeto': motorista, 'tipo': 'Motorista', 'url_lista': 'listar_motoristas'}
    return render(request, 'templatesApp/confirmar_eliminar.html', context)

# --- Mantenedor de Motos ---
@login_required
def listar_motos(request):
    query = request.GET.get('q', '')
    if query:
        motos = Moto.objects.filter(Q(patente__icontains=query) | Q(modelo__icontains=query))
    else:
        motos = Moto.objects.all()
    context = {'motos': motos, 'query': query}
    return render(request, 'templatesApp/listar_motos.html', context)

@login_required
def agregar_moto(request):
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
    moto = get_object_or_404(Moto, pk=pk)
    patente = moto.patente
    if request.method == 'POST':
        moto.delete()
        messages.warning(request, f'Moto {patente} ha sido eliminada.')
        return redirect('listar_motos')
    context = {'objeto': moto, 'tipo': 'Moto', 'url_lista': 'listar_motos'}
    return render(request, 'templatesApp/confirmar_eliminar.html', context)

# --- Mantenedor de Farmacias ---
@login_required
def listar_farmacias(request):
    query = request.GET.get('q', '')
    if query:
        farmacias = Farmacia.objects.filter(Q(nombre__icontains=query) | Q(direccion__icontains=query))
    else:
        farmacias = Farmacia.objects.all()
    context = {'farmacias': farmacias, 'query': query}
    return render(request, 'templatesApp/listar_farmacias.html', context)

@login_required
def agregar_farmacia(request):
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
    farmacia = get_object_or_404(Farmacia, pk=pk)
    nombre = farmacia.nombre
    if request.method == 'POST':
        farmacia.delete()
        messages.warning(request, f'Farmacia {nombre} ha sido eliminada.')
        return redirect('listar_farmacias')
    context = {'objeto': farmacia, 'tipo': 'Farmacia', 'url_lista': 'listar_farmacias'}
    return render(request, 'templatesApp/confirmar_eliminar.html', context)

# --- VISTAS PARA ASIGNACIONES ---
@login_required
def listar_asignaciones(request):
    asignaciones = Asignacion.objects.select_related('motorista', 'farmacia').all()
    context = {'asignaciones': asignaciones, 'titulo': 'Gestión de Asignaciones'}
    return render(request, 'templatesApp/listar_asignaciones.html', context)

@login_required
def agregar_asignacion(request):
    if request.method == 'POST':
        form = AsignacionForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, '¡Asignación guardada exitosamente!')
                return redirect('listar_asignaciones')
            except Exception as e:
                form.add_error(None, f"Error al guardar: Esta asignación ya existe.")
    else:
        form = AsignacionForm()
    context = {'form': form, 'titulo': 'Agregar Asignación'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def eliminar_asignacion(request, pk):
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
    region_id = request.GET.get('region')
    provincia_id = request.GET.get('provincia')
    comuna_id = request.GET.get('comuna')

    movimientos = Movimiento.objects.select_related(
        'farmacia__comuna__provincia__region', 'motorista', 'tipo_movimiento'
    ).exclude(status='anulado')

    if comuna_id:
        movimientos = movimientos.filter(farmacia__comuna_id=comuna_id)
    elif provincia_id:
        movimientos = movimientos.filter(farmacia__comuna__provincia_id=provincia_id)
    elif region_id:
        movimientos = movimientos.filter(farmacia__comuna__provincia__region_id=region_id)
    
    regiones = Region.objects.all().order_by('nombre')
    provincias = Provincia.objects.none()
    comunas = Comuna.objects.none()
    if region_id:
        provincias = Provincia.objects.filter(region_id=region_id).order_by('nombre')
    if provincia_id:
        comunas = Comuna.objects.filter(provincia_id=provincia_id).order_by('nombre')

    context = {
        'movimientos': movimientos.order_by('-fecha_hora'),
        'titulo': 'Listado General de Movimientos',
        'regiones': regiones, 'provincias': provincias, 'comunas': comunas,
        'selected_region': int(region_id) if region_id else None,
        'selected_provincia': int(provincia_id) if provincia_id else None,
        'selected_comuna': int(comuna_id) if comuna_id else None,
    }
    return render(request, 'templatesApp/listar_movimientos.html', context)

# --- === VISTA ACTUALIZADA (historial_movimientos) === ---
@login_required
def historial_movimientos(request):
    """
    Muestra TODOS los movimientos, con filtros por Farmacia y Fecha.
    """
    # 1. Obtener los valores de los filtros (si existen)
    farmacia_id = request.GET.get('farmacia_id')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # 2. Queryset base (todos los movimientos)
    movimientos = Movimiento.objects.select_related(
        'farmacia', 'motorista', 'tipo_movimiento'
    ).all()
    
    # 3. Aplicar filtros
    if farmacia_id:
        movimientos = movimientos.filter(farmacia_id=farmacia_id)
        
    if fecha_desde:
        # '__gte' significa "mayor o igual que"
        movimientos = movimientos.filter(fecha_hora__gte=fecha_desde) 
        
    if fecha_hasta:
        # '__lte' significa "menor o igual que"
        movimientos = movimientos.filter(fecha_hora__lte=fecha_hasta)

    # 4. Obtener todas las farmacias para el menú desplegable del filtro
    farmacias_para_filtro = Farmacia.objects.all().order_by('nombre')
    
    context = {
        'movimientos': movimientos.order_by('-fecha_hora'), # Muestra todos
        'titulo': 'Historial General de Movimientos',
        
        # Pasamos los datos para el formulario de filtro
        'farmacias_para_filtro': farmacias_para_filtro,
        
        # Devolvemos los valores seleccionados para que el formulario los "recuerde"
        'filtro_farmacia_id': int(farmacia_id) if farmacia_id else None,
        'filtro_fecha_desde': fecha_desde,
        'filtro_fecha_hasta': fecha_hasta,
    }
    return render(request, 'templatesApp/historial_movimientos.html', context)
# --- === FIN VISTA ACTUALIZADA === ---


@login_required
def agregar_movimiento(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Movimiento registrado exitosamente!')
            return redirect('listar_movimientos')
    else:
        # --- Lógica de Comprobación ---
        ocupados_pks = Movimiento.objects.filter(status='en_ruta').values_list('motorista_id', flat=True).distinct()
        disponibles = Motorista.objects.filter(esta_activo=True).exclude(pk__in=ocupados_pks)
        
        if not disponibles.exists():
            messages.error(request, 'No hay motoristas disponibles para registrar un nuevo movimiento. Todos están "En Ruta".')
            return redirect('listar_movimientos')
        
        form = MovimientoForm()
        # --- Fin Lógica ---

    context = {'form': form, 'titulo': 'Registrar Nuevo Movimiento'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def editar_movimiento(request, pk):
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
    movimiento = get_object_or_404(Movimiento, pk=pk)
    
    estados_no_anulables = ['entregado', 'fallido', 'anulado']
    if movimiento.status in estados_no_anulables:
        messages.error(request, f'No se puede anular un movimiento que ya está "{movimiento.get_status_display()}".')
        return redirect('listar_movimientos')
    
    if request.method == 'POST':
        movimiento.status = 'anulado'
        fecha_hora_actual = timezone.now().strftime("%d/%m/%Y %H:%M")
        nota = f"\n[ANULADO {fecha_hora_actual}]"
        if movimiento.observacion: movimiento.observacion += nota
        else: movimiento.observacion = nota
        movimiento.save()
        messages.warning(request, f'El Movimiento #{movimiento.pk} ha sido anulado.')
        return redirect('listar_movimientos')
    
    context = {'objeto': movimiento, 'tipo': f'Movimiento #{movimiento.pk} (Anular)', 'url_lista': 'listar_movimientos'}
    return render(request, 'templatesApp/confirmar_eliminar.html', context)

@login_required
def reemplazar_motorista(request, pk):
    motorista_original = get_object_or_404(Motorista, pk=pk)
    if request.method == 'POST':
        form = MotoristaForm(request.POST, request.FILES) 
        if form.is_valid():
            nuevo_motorista = form.save(commit=False)
            nuevo_motorista.reemplaza_a = motorista_original 
            nuevo_motorista.esta_activo = True 
            nuevo_motorista.save() 
            motorista_original.esta_activo = False
            motorista_original.save()
            messages.success(request, f'Motorista {nuevo_motorista.nombres} ha reemplazado exitosamente a {motorista_original.nombres}.')
            return redirect('listar_motoristas')
    else:
        form = MotoristaForm()
    context = {'form': form, 'titulo': f'Reemplazar a: {motorista_original.nombres} {motorista_original.apellido_paterno}', 'subtitulo': 'Se creará un nuevo motorista y se desactivará el original.'}
    return render(request, 'templatesApp/agregar.html', context)

@login_required
def reemplazar_movimiento(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk)
    motorista_original = movimiento.motorista

    estados_no_reemplazables = ['entregado', 'fallido', 'anulado']
    if movimiento.status in estados_no_reemplazables:
        messages.error(request, f'No se puede reemplazar el motorista de un movimiento que ya está "{movimiento.get_status_display()}".')
        return redirect('listar_movimientos')

    if request.method == 'POST':
        form = ReemplazoMovimientoForm(request.POST, instance=movimiento)
        
        if form.is_valid():
            nuevo_movimiento = form.save(commit=False) 
            nuevo_movimiento.motorista_original = motorista_original
            fecha_hora_actual = timezone.now().strftime("%d/%m/%Y %H:%M")
            nota = f"\n[REEMPLAZO {fecha_hora_actual}: {motorista_original.nombres} -> {nuevo_movimiento.motorista.nombres}]"
            if nuevo_movimiento.observacion: nuevo_movimiento.observacion += nota
            else: nuevo_movimiento.observacion = nota
            nuevo_movimiento.save()
            messages.success(request, f'Se ha reemplazado a {motorista_original.nombres} por {nuevo_movimiento.motorista.nombres} en el movimiento.')
            return redirect('listar_movimientos')
    
    else: # request.method == 'GET'
        form = ReemplazoMovimientoForm(instance=movimiento)
        
        try:
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
    movimiento = get_object_or_404(Movimiento, pk=pk)
    
    if request.method == 'POST':
        form = CambioEstadoForm(request.POST, instance=movimiento)
        
        if form.is_valid():
            nuevo_estado = form.cleaned_data['status']
            fecha_hora_actual = timezone.now().strftime("%d/%m/%Y %H:%M")
            usuario = request.user.username if request.user.is_authenticated else 'sistema'
            nota = f"\n[ESTADO CAMBIADO A: {nuevo_estado.upper()} por {usuario}]"
            movimiento = form.save(commit=False)
            if movimiento.observacion: movimiento.observacion += nota
            else: movimiento.observacion = nota
            movimiento.save()
            messages.success(request, f'El estado del Movimiento #{movimiento.pk} ha sido actualizado a "{movimiento.get_status_display()}".')
        
        else:
            errores = form.errors.as_text()
            messages.error(request, f'Error al cambiar el estado del Movimiento #{movimiento.pk}: {errores}')

    return redirect('listar_movimientos')
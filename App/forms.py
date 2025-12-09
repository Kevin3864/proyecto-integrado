"""
Archivo de Formularios (App/forms.py)

Define todos los formularios de Django para la aplicación 'App'.
Este archivo es crucial ya que contiene no solo la definición de qué
campos se muestran, sino también la LÓGICA DE NEGOCIO Y VALIDACIÓN clave,
como:
- Filtrado de Querysets (ej. mostrar solo motoristas disponibles).
- Validación personalizada (ej. reglas para 'Traslados').
- Lógica de campos dependientes (ej. Región -> Provincia).
"""

from django import forms
from .models import (
    Motorista, Moto, Farmacia, Comuna, Provincia, Region,
    ContactoEmergencia, DocumentacionMoto, Asignacion, Movimiento, TipoMovimiento, Reporte
)
from django.core.exceptions import ValidationError

# --- Formularios Geográficos (Básicos) ---

class RegionForm(forms.ModelForm):
    """Formulario simple para el mantenedor de Regiones."""
    class Meta:
        model = Region
        fields = '__all__'

class ProvinciaForm(forms.ModelForm):
    """Formulario simple para el mantenedor de Provincias."""
    class Meta:
        model = Provincia
        fields = '__all__'

class ComunaForm(forms.ModelForm):
    """Formulario simple para el mantenedor de Comunas."""
    class Meta:
        model = Comuna
        fields = '__all__'

# --- Formulario de Farmacia (Complejo) ---

class FarmaciaForm(forms.ModelForm):
    """
    Formulario para crear y editar Farmacias.
    
    Mejor Práctica:
    Incluye campos 'extra' ('region', 'provincia') que no están en el modelo Farmacia
    para ayudar al usuario a seleccionar la Comuna. La lógica de filtrado dependiente
    (Región -> Provincia -> Comuna) se maneja en la plantilla con JavaScript.
    """
    
    # 1. Campos 'extra' (no-modelo) para asistir en la selección de Comuna
    region = forms.ModelChoiceField(
        queryset=Region.objects.all().order_by('nombre'), 
        label="Región", 
        required=False # No son obligatorios para el guardado (solo 'comuna' lo es)
    )
    provincia = forms.ModelChoiceField(
        queryset=Provincia.objects.all().order_by('nombre'), 
        label="Provincia", 
        required=False
    )

    class Meta:
        model = Farmacia
        fields = [
            'nombre', 'direccion', 
            'comuna', 'horario_apertura',
            'horario_cierre', 'telefono', 'latitud', 'longitud'
        ]
        widgets = {
            'horario_apertura': forms.TimeInput(attrs={'type': 'time'}),
            'horario_cierre': forms.TimeInput(attrs={'type': 'time'}),
            'latitud': forms.NumberInput(attrs={'step': '0.000001'}),
            'longitud': forms.NumberInput(attrs={'step': '0.000001'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Sobrescribe el __init__ para dos propósitos:
        1. Reordenar los campos visualmente ('region' y 'provincia' primero).
        2. Si es una edición (instance=True), pre-rellenar los campos
           de Región y Provincia basados en la Comuna ya guardada.
        """
        super().__init__(*args, **kwargs)
        
        # 2. Reordenar campos: Mueve region y provincia al principio del formulario
        self.fields = dict(
            [('region', self.fields['region']), ('provincia', self.fields['provincia'])] + 
            list(self.fields.items())
        )

        # 3. Pre-rellenado en modo Edición
        # 'self.instance.pk' es la forma de saber si estamos editando (True) o creando (False)
        if self.instance.pk and self.instance.comuna:
            # Si la farmacia guardada tiene comuna, encontramos su provincia y región
            self.fields['provincia'].initial = self.instance.comuna.provincia
            self.fields['region'].initial = self.instance.comuna.provincia.region


# --- Formularios de Motoristas y Recursos ---

class MotoristaForm(forms.ModelForm):
    """Formulario estándar para el mantenedor de Motoristas."""
    class Meta:
        model = Motorista
        fields = [
            'rut', 'pasaporte', 'nombres', 'apellido_paterno', 'apellido_materno',
            'fecha_nacimiento', 'direccion', 'comuna', 'telefono', 'email',
            'incluye_moto_personal', 'licencia_archivo', 'licencia_ultimo_control'
        ]
        # Mejor Práctica: Widgets para mejorar la experiencia de usuario (HTML5 date picker)
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'licencia_ultimo_control': forms.DateInput(attrs={'type': 'date'}),
        }

class ContactoEmergenciaForm(forms.ModelForm):
    """Formulario simple para los contactos de emergencia de un motorista."""
    class Meta:
        model = ContactoEmergencia
        fields = ['nombre_contacto', 'parentesco', 'telefono']

class MotoForm(forms.ModelForm):
    """Formulario estándar para el mantenedor de Motos."""
    class Meta:
        model = Moto
        fields = [
            'patente', 'marca', 'modelo', 'color', 'anio', 'numero_chasis',
            'motor', 'motorista_asignado', 'es_propiedad_empresa'
        ]
        widgets = {
            'anio': forms.NumberInput(attrs={'min': '1980', 'max': '2025'}),
        }

class DocumentacionMotoForm(forms.ModelForm):
    """Formulario simple para la documentación anual de una moto."""
    class Meta:
        model = DocumentacionMoto
        fields = ['anio', 'permiso_circulacion', 'seguro_obligatorio', 'revision_tecnica']
        widgets = {
            'anio': forms.NumberInput(attrs={'min': '2000', 'max': '2025'}),
        }

class AsignacionForm(forms.ModelForm):
    """Formulario para la tabla 'puente' que asigna un Motorista a una Farmacia."""
    class Meta:
        model = Asignacion
        fields = ['motorista', 'farmacia']

# --- Formularios de Movimientos (Lógica de Negocio Clave) ---

class MovimientoForm(forms.ModelForm):
    """
    Formulario para crear y editar un Movimiento.
    
    Mejor Práctica:
    - __init__: Filtra el queryset de 'motorista' para implementar la
      lógica de negocio de "disponibilidad" (no mostrar motoristas 'en_ruta').
    - clean: Valida la lógica de negocio de "Traslados" (destino obligatorio
      y no igual al origen).
    """

    def __init__(self, *args, **kwargs):
        """
        Filtra la lista de motoristas para mostrar solo los que
        NO están 'en_ruta' en otro movimiento.
        """
        super().__init__(*args, **kwargs)
        
        # 1. Encontrar IDs de motoristas OCUPADOS ('En Ruta')
        #    Mejor Práctica: .distinct() asegura que solo tengamos un ID por motorista.
        ocupados_pks = Movimiento.objects.filter(
            status='en_ruta'
        ).values_list('motorista_id', flat=True).distinct()
        
        # 2. Filtrar el queryset del campo 'motorista'
        #    Solo muestra motoristas activos Y que no estén en la lista de ocupados.
        self.fields['motorista'].queryset = Motorista.objects.filter(esta_activo=True).exclude(
            pk__in=ocupados_pks
        )

    class Meta:
        model = Movimiento
        fields = [
            'farmacia', 'tipo_movimiento', 'farmacia_destino', 
            'motorista', 'observacion'
        ]
        widgets = {
            'observacion': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        """
        Mejor Práctica: Validación de Lógica de Negocio (Patrón de Seguridad 4).
        Aplica las reglas para los movimientos de tipo "Traslado".
        """
        cleaned_data = super().clean()
        tipo_movimiento = cleaned_data.get('tipo_movimiento')
        farmacia_origen = cleaned_data.get('farmacia')
        farmacia_destino = cleaned_data.get('farmacia_destino')

        if tipo_movimiento:
            # Comprobación robusta (cubre "Traslado", "pedido con traslado", etc.)
            if 'traslado' in tipo_movimiento.nombre.lower():
                
                # Regla 1: Si es traslado, 'farmacia_destino' es obligatoria.
                if not farmacia_destino:
                    self.add_error('farmacia_destino', 'Para un traslado, la farmacia de destino es obligatoria.')
                
                # Regla 2: Origen y Destino no pueden ser iguales.
                if farmacia_origen and farmacia_destino and farmacia_origen == farmacia_destino:
                    self.add_error('farmacia_destino', 'La farmacia de destino no puede ser la misma que la de origen.')
            
            else:
                # Regla 3: Si NO es traslado, limpia el campo 'farmacia_destino'.
                cleaned_data['farmacia_destino'] = None
        
        return cleaned_data


class ReemplazoMovimientoForm(forms.ModelForm):
    """
    Formulario específico para Reemplazar el motorista de un movimiento.
    Solo muestra el campo 'motorista'.
    
    Mejor Práctica:
    - __init__: Filtra el queryset de 'motorista' para mostrar solo
      motoristas disponibles, excluyendo también al motorista actual.
    """
    class Meta:
        model = Movimiento
        fields = ['motorista']
        labels = {'motorista': 'Seleccione el Motorista de Reemplazo'}

    def __init__(self, *args, **kwargs):
        """
        Filtra la lista de motoristas para el reemplazo.
        Reglas: Motorista debe estar activo, no debe estar 'en_ruta',
        y no debe ser el mismo motorista que ya tiene el movimiento.
        """
        super().__init__(*args, **kwargs)
        
        movimiento_actual = self.instance
        motorista_actual_pk = movimiento_actual.motorista.pk if movimiento_actual.motorista else None

        # 1. Encontrar motoristas ocupados ('en_ruta')
        #    Se excluye el movimiento actual (un motorista no puede estar
        #    ocupado por el mismo movimiento que está siendo reemplazado).
        ocupados_pks = Movimiento.objects.filter(
            status='en_ruta' 
        ).exclude(pk=movimiento_actual.pk).values_list('motorista_id', flat=True).distinct()
    
        # 2. El queryset base: Activos y no ocupados
        queryset_base = Motorista.objects.filter(esta_activo=True).exclude(
            pk__in=ocupados_pks
        )

        # 3. Excluir al motorista actual de la lista de opciones
        if motorista_actual_pk:
            queryset_base = queryset_base.exclude(pk=motorista_actual_pk)
            
        self.fields['motorista'].queryset = queryset_base


# --- Formulario del Modal de Cambio de Estado ---

# Mejor Práctica: Definir la lista de opciones en un solo lugar.
# Se filtra 'anulado' porque solo se anula desde el botón 'Anular'.
ESTADOS_DISPONIBLES = [estado for estado in Movimiento.ESTADOS if estado[0] != 'anulado']

class CambioEstadoForm(forms.ModelForm):
    """
    Formulario minimalista usado por el pop-up (modal) para cambiar
    el estado de un movimiento (ej. 'En Ruta' -> 'Entregado').
    """
    
    # Sobrescribimos el campo 'status' para usar la lista filtrada
    status = forms.ChoiceField(choices=ESTADOS_DISPONIBLES, label="Nuevo Estado")
    
    class Meta:
        model = Movimiento
        fields = ['status'] # Solo queremos editar este campo

    def __init__(self, *args, **kwargs):
        """Añade la clase 'form-select' de Bootstrap al menú."""
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'form-select'})

# --- Formulario de Reportes (Nuevo Mantenedor) ---

class ReporteForm(forms.Form):
    """
    Formulario para filtrar los reportes por tipo y fecha.
    No está vinculado a un modelo, solo procesa datos.
    """
    TIPOS_REPORTE = (
        ('diario', 'Reporte Diario'),
        ('mensual', 'Reporte Mensual'),
        ('anual', 'Reporte Anual'),
    )

    tipo_reporte = forms.ChoiceField(
        choices=TIPOS_REPORTE, 
        label="Tipo de Reporte",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fecha = forms.DateField(
        label="Fecha de Referencia",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )




# --- FORMULARIO PARA GENERAR REPORTE INDIVIDUAL ---
class ReporteMovimientoForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['observacion']
        widgets = {
            'observacion': forms.Textarea(attrs={
                'rows': 5, 
                'class': 'form-control',
                'placeholder': 'Escriba aquí las observaciones finales, estado de entrega, incidencias, etc...'
            }),
        }
        labels = {
            'observacion': 'Observaciones Finales del Movimiento'
        }
from django import forms
from .models import (
    Motorista, Moto, Farmacia, Comuna, Provincia, Region,
    ContactoEmergencia, DocumentacionMoto, Asignacion, Movimiento, TipoMovimiento
)
from django.core.exceptions import ValidationError

# --- Formularios Básicos ---
class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = '__all__'

class ProvinciaForm(forms.ModelForm):
    class Meta:
        model = Provincia
        fields = '__all__'

class ComunaForm(forms.ModelForm):
    class Meta:
        model = Comuna
        fields = '__all__'

# --- Formulario de Farmacia (MODIFICADO) ---
class FarmaciaForm(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all().order_by('nombre'), 
        label="Región", 
        required=False
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
        super().__init__(*args, **kwargs)
        
        self.fields = dict(
            [('region', self.fields['region']), ('provincia', self.fields['provincia'])] + 
            list(self.fields.items())
        )

        if self.instance.pk and self.instance.comuna:
            self.fields['provincia'].initial = self.instance.comuna.provincia
            self.fields['region'].initial = self.instance.comuna.provincia.region


# --- Resto de Formularios (Sin cambios) ---
class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = [
            'rut', 'pasaporte', 'nombres', 'apellido_paterno', 'apellido_materno',
            'fecha_nacimiento', 'direccion', 'comuna', 'telefono', 'email',
            'incluye_moto_personal', 'licencia_archivo', 'licencia_ultimo_control'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'licencia_ultimo_control': forms.DateInput(attrs={'type': 'date'}),
        }

class ContactoEmergenciaForm(forms.ModelForm):
    class Meta:
        model = ContactoEmergencia
        fields = ['nombre_contacto', 'parentesco', 'telefono']

class MotoForm(forms.ModelForm):
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
    class Meta:
        model = DocumentacionMoto
        fields = ['anio', 'permiso_circulacion', 'seguro_obligatorio', 'revision_tecnica']
        widgets = {
            'anio': forms.NumberInput(attrs={'min': '2000', 'max': '2025'}),
        }

class AsignacionForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        fields = ['motorista', 'farmacia']


# --- === INICIO DE FORMULARIO MODIFICADO === ---
class MovimientoForm(forms.ModelForm):

    # --- ¡NUEVO __INIT__ AÑADIDO! ---
    def __init__(self, *args, **kwargs):
        """
        Filtra la lista de motoristas para mostrar solo los que
        NO están 'en_ruta' en otro movimiento.
        """
        super().__init__(*args, **kwargs)
        
        # 1. Encontrar IDs de motoristas OCUPADOS ('En Ruta')
        ocupados_pks = Movimiento.objects.filter(
            status='en_ruta'
        ).values_list('motorista_id', flat=True).distinct()
        
        # 2. Filtrar el queryset del campo 'motorista'
        self.fields['motorista'].queryset = Motorista.objects.filter(esta_activo=True).exclude(
            pk__in=ocupados_pks
        )
    # --- FIN DE __INIT__ AÑADIDO ---

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
        cleaned_data = super().clean()
        tipo_movimiento = cleaned_data.get('tipo_movimiento')
        farmacia_origen = cleaned_data.get('farmacia')
        farmacia_destino = cleaned_data.get('farmacia_destino')

        if tipo_movimiento:
            if 'traslado' in tipo_movimiento.nombre.lower():
                if not farmacia_destino:
                    self.add_error('farmacia_destino', 'Para un traslado, la farmacia de destino es obligatoria.')
                if farmacia_origen and farmacia_destino and farmacia_origen == farmacia_destino:
                    self.add_error('farmacia_destino', 'La farmacia de destino no puede ser la misma que la de origen.')
            else:
                cleaned_data['farmacia_destino'] = None
        return cleaned_data
# --- === FIN DE FORMULARIO MODIFICADO === ---


# --- === INICIO DE FORMULARIO MODIFICADO === ---
class ReemplazoMovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['motorista']
        labels = {'motorista': 'Seleccione el Motorista de Reemplazo'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        movimiento_actual = self.instance
        motorista_actual_pk = movimiento_actual.motorista.pk if movimiento_actual.motorista else None

        # 1. Encontrar motoristas ocupados. 
        # --- ¡LÓGICA ACTUALIZADA! ---
        # Ahora solo busca 'en_ruta'
        ocupados_pks = Movimiento.objects.filter(
            status='en_ruta' 
        ).exclude(pk=movimiento_actual.pk).values_list('motorista_id', flat=True).distinct()
        # --- FIN DE LÓGICA ACTUALIZADA ---

        # 2. El queryset base son motoristas activos y no ocupados
        queryset_base = Motorista.objects.filter(esta_activo=True).exclude(
            pk__in=ocupados_pks
        )

        # 3. Excluir al motorista actual si existe
        if motorista_actual_pk:
            queryset_base = queryset_base.exclude(pk=motorista_actual_pk)
            
        self.fields['motorista'].queryset = queryset_base
# --- === FIN DE FORMULARIO MODIFICADO === ---


# Formulario para el Pop-up de Cambio de Estado
# Esta lógica ahora es correcta, porque Movimiento.ESTADOS
# ya no contiene 'asignado'.
ESTADOS_DISPONIBLES = [estado for estado in Movimiento.ESTADOS if estado[0] != 'anulado']

class CambioEstadoForm(forms.ModelForm):
    status = forms.ChoiceField(choices=ESTADOS_DISPONIBLES, label="Nuevo Estado")
    class Meta:
        model = Movimiento
        fields = ['status'] 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
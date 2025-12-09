"""
Archivo de Modelos (App/models.py)

Define la estructura de la base de datos (el "Modelo Lógico") del proyecto.
Cada clase representa una tabla en la base de datos y sus atributos
son las columnas.

Mejores Prácticas Aplicadas:
- Uso de 'verbose_name' para nombres amigables en el admin.
- Uso de 'related_name' para consultas inversas claras (ej. motorista.contactos_emergencia).
- Uso de 'on_delete' (PROTECT, CASCADE, SET_NULL) para integridad de datos.
- Definición de 'unique_together' para constraints de base de datos.
- Implementación de lógica de negocio (esta_activo, reemplaza_a, status, etc.)
  directamente en el modelo.
"""

from django.db import models
from django.core.validators import RegexValidator # Para validar RUT

# Mejor Práctica: Definir validadores reutilizables.
rut_validator = RegexValidator(
    regex=r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$',
    message='El RUT debe tener el formato XX.XXX.XXX-X'
)

# --- Modelos Geográficos ---

class Region(models.Model):
    """Modelo Maestro para las Regiones."""
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class Provincia(models.Model):
    """Modelo Maestro para las Provincias, dependiente de Región."""
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    def __str__(self): return f"{self.nombre}, {self.region.nombre}"

class Comuna(models.Model):
    """Modelo Maestro para las Comunas, dependiente de Provincia."""
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)
    def __str__(self): return f"{self.nombre}, {self.provincia.nombre}"

# --- Modelos de Entidades Principales ---

class Farmacia(models.Model):
    """
    Almacena la información de una sucursal de farmacia.
    Se vincula a una Comuna para la geolocalización y filtros.
    """
    nombre = models.CharField(max_length=100, verbose_name="Nombre farmacia")
    direccion = models.CharField(max_length=255)
    
    # Mejor Práctica: on_delete=SET_NULL. Si se borra una comuna,
    # la farmacia no se borra, solo queda sin comuna.
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)
    
    horario_apertura = models.TimeField(blank=True, null=True)
    horario_cierre = models.TimeField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.direccion})"

class Motorista(models.Model):
    """
    Almacena la información de los motoristas.
    Contiene la lógica clave para el reemplazo de personal.
    """
    # Información Personal
    rut = models.CharField(max_length=12, unique=True, validators=[rut_validator], blank=True, null=True)
    pasaporte = models.CharField(max_length=50, blank=True, null=True)
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    
    # Información de Contacto y Ubicación
    direccion = models.CharField(max_length=255, blank=True, null=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True, verbose_name="Correo electrónico") # Para login
    
    # Información de Trabajo
    incluye_moto_personal = models.BooleanField(default=False)
    licencia_archivo = models.FileField(upload_to='licencias/', blank=True, null=True, verbose_name="Adjunto Licencia")
    licencia_ultimo_control = models.DateField(blank=True, null=True, verbose_name="Fecha Último Control Licencia")

    # --- LÓGICA DE REEMPLAZO DE PERSONAL (Punto 3.1.6.15) ---
    
    # Campo para "borrado lógico". Un motorista desactivado no aparece en las listas.
    esta_activo = models.BooleanField(default=True, verbose_name="Está Activo")
    
    # Relación reflexiva (un motorista se enlaza a otro motorista).
    # Si este motorista es un reemplazo, aquí se guarda el ID del motorista al que reemplazó.
    reemplaza_a = models.ForeignKey(
        'self', # Se apunta a sí mismo (al modelo Motorista)
        on_delete=models.SET_NULL, # Si se borra el motorista original, este campo queda nulo
        null=True, blank=True, 
        related_name='reemplazado_por', # Cómo encontrar al reemplazo (motorista.reemplazado_por)
        verbose_name="Reemplaza a"
    )
    # --- FIN DE LÓGICA DE REEMPLAZO ---

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno}"

class ContactoEmergencia(models.Model):
    """
    Almacena los contactos de emergencia de un motorista (Relación 1 a N).
    """
    # Mejor Práctica: on_delete=CASCADE. Si se borra el motorista,
    # sus contactos de emergencia (que no sirven solos) se borran con él.
    motorista = models.ForeignKey(Motorista, related_name='contactos_emergencia', on_delete=models.CASCADE)
    nombre_contacto = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre_contacto} ({self.parentesco}) - {self.motorista}"

class Moto(models.Model):
    """
    Almacena la información de un vehículo (moto).
    """
    patente = models.CharField(max_length=10, unique=True, verbose_name="Patente/Matrícula")
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True, verbose_name="Año")
    numero_chasis = models.CharField(max_length=100, blank=True, null=True)
    motor = models.CharField(max_length=100, blank=True, null=True)
    
    # Relación opcional a un motorista
    motorista_asignado = models.ForeignKey(Motorista, related_name='motos_asignadas', on_delete=models.SET_NULL, null=True, blank=True)
    es_propiedad_empresa = models.BooleanField(default=True, verbose_name="Propietario Moto (Empresa=Sí)")

    def __str__(self):
        return self.patente

class DocumentacionMoto(models.Model):
    """
    Almacena los documentos *anuales* de una moto (Relación 1 a N).
    """
    moto = models.ForeignKey(Moto, related_name='documentaciones', on_delete=models.CASCADE)
    anio = models.IntegerField(verbose_name="Año Documentación")
    permiso_circulacion = models.FileField(upload_to='docs_moto/permisos/', blank=True, null=True)
    seguro_obligatorio = models.FileField(upload_to='docs_moto/seguros/', blank=True, null=True)
    revision_tecnica = models.FileField(upload_to='docs_moto/revisiones/', blank=True, null=True)

    class Meta:
        # Mejor Práctica: Constraint (Restricción) a nivel de BD.
        # Evita que se ingrese la documentación del 2024 dos veces para la misma moto.
        unique_together = ('moto', 'anio')

    def __str__(self):
        return f"Documentación {self.anio} - {self.moto.patente}"
    
    
#----------------------------------------
# --- MODELOS DE LOGÍSTICA (Núcleo del Negocio) ---
#----------------------------------------

class TipoMovimiento(models.Model):
    """
    Modelo Maestro para los tipos de operaciones.
    (ej. "pedido con traslado", "Devolución", "Entrega")
    """
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Asignacion(models.Model):
    """
    Entidad Asociativa (tabla "puente") que crea una relación
    Muchos-a-Muchos (N-N) entre Motorista y Farmacia.
    """
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE, verbose_name="Motorista Asignado")
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, verbose_name="Farmacia Asignada")
    fecha_asignacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Asignación")

    class Meta:
        # Constraint: Un motorista solo puede asignarse una vez a la misma farmacia.
        unique_together = ('motorista', 'farmacia')

    def __str__(self):
        return f"{self.motorista.nombres} asignado a {self.farmacia.nombre}"


class Movimiento(models.Model):
    """
    Modelo "corazón" del sistema. Registra cada operación logística.
    Contiene la lógica de Estados, Traslados y Reemplazos.
    """
    
    # --- LÓGICA DE ESTADOS (Punto 3.1.1.1) ---
    ESTADOS = (
        # 'asignado' fue eliminado por lógica de negocio
        ('en_ruta', 'En Ruta'),
        ('entregado', 'Entregado'),
        ('fallido', 'Fallido'),
        ('anulado', 'Anulado'), # Para borrado lógico
    )
    
    # --- Relaciones (Llaves Foráneas) ---
    
    # Mejor Práctica: on_delete=PROTECT evita que se pueda borrar una farmacia
    # si tiene movimientos asociados (integridad de datos).
    farmacia = models.ForeignKey(
        Farmacia, 
        on_delete=models.PROTECT, 
        verbose_name="Farmacia Origen" # Etiqueta para el Formulario
    )
    motorista = models.ForeignKey(Motorista, on_delete=models.PROTECT, verbose_name="Motorista (Actual)")
    tipo_movimiento = models.ForeignKey(TipoMovimiento, on_delete=models.PROTECT, verbose_name="Tipo de Movimiento")

    # --- Atributos Propios ---
    observacion = models.TextField(blank=True, null=True, verbose_name="Observación")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    
    # --- LÓGICA DE ESTADOS (Aplicada) ---
    status = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='en_ruta', # Lógica de Negocio: El estado base es 'En Ruta'
        verbose_name="Estado"
    )
    
    # --- LÓGICA DE REEMPLAZO DE MOVIMIENTO ---
    # Guarda el ID del motorista que fue reemplazado en ESTE movimiento.
    motorista_original = models.ForeignKey(
        Motorista, 
        on_delete=models.SET_NULL, # Si se borra el motorista original, el campo queda nulo
        null=True, blank=True, 
        related_name='movimientos_reemplazados',
        verbose_name="Motorista Original (si fue reemplazado)"
    )

    # --- LÓGICA DE TRASLADO ---
    # Guarda el ID de la farmacia destino.
    # Es opcional (null=True, blank=True) porque solo se usa
    # si el 'tipo_movimiento' es "Traslado".
    farmacia_destino = models.ForeignKey(
        Farmacia, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        verbose_name="Farmacia Destino (solo traslados)",
        related_name='movimientos_destino' # 'related_name' es obligatorio para evitar conflictos
    )

    def __str__(self):
        # Método para mostrar una representación legible en el Admin de Django
        return f"{self.tipo_movimiento.nombre} - {self.motorista.nombres} ({self.get_status_display()})"
    
    # --- NUEVO MODELO PARA REPORTES INDIVIDUALES ---
class Reporte(models.Model):
    """
    Almacena el reporte final de un movimiento específico.
    Relación 1 a 1: Un movimiento tiene un solo reporte final.
    """
    movimiento = models.OneToOneField(
        Movimiento, 
        on_delete=models.CASCADE, 
        related_name='reporte' # Nos permite acceder como movimiento.reporte
    )
    observacion = models.TextField(
        verbose_name="Observación del Reporte",
        help_text="Conclusiones finales o detalles de la entrega."
    )
    fecha_generacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Generación")

    def __str__(self):
        return f"Reporte #{self.pk} - Movimiento #{self.movimiento.pk}"
    
    
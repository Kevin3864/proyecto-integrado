from django.db import models
from django.core.validators import RegexValidator # Para validar RUT

# Validador simple para RUT chileno (formato XX.XXX.XXX-X o X.XXX.XXX-X)
rut_validator = RegexValidator(
    regex=r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$',
    message='El RUT debe tener el formato XX.XXX.XXX-X'
)

class Region(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    def __str__(self): return f"{self.nombre}, {self.region.nombre}"

class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)
    def __str__(self): return f"{self.nombre}, {self.provincia.nombre}"

class Farmacia(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre farmacia")
    direccion = models.CharField(max_length=255)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)
    horario_apertura = models.TimeField(blank=True, null=True)
    horario_cierre = models.TimeField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        # Esto cambiará "Cruz Verde" por "Cruz Verde (Av. Providencia 123)"
        return f"{self.nombre} ({self.direccion})"

class Motorista(models.Model):
    # Código Motorista se puede usar el ID automático de Django (motorista.id o motorista.pk)
    rut = models.CharField(max_length=12, unique=True, validators=[rut_validator], blank=True, null=True)
    pasaporte = models.CharField(max_length=50, blank=True, null=True)
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    incluye_moto_personal = models.BooleanField(default=False)
    
    
    # Licencia
    licencia_archivo = models.FileField(upload_to='licencias/', blank=True, null=True, verbose_name="Adjunto Licencia")
    licencia_ultimo_control = models.DateField(blank=True, null=True, verbose_name="Fecha Último Control Licencia")

    # --- CAMPOS AÑADIDOS ---
    esta_activo = models.BooleanField(default=True, verbose_name="Está Activo")
    
    reemplaza_a = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='reemplazado_por',
        verbose_name="Reemplaza a"
    )
    # --- FIN DE CAMPOS AÑADIDOS ---

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno}"

# Nuevo Modelo para Contactos de Emergencia (Relación Uno a Muchos con Motorista)
class ContactoEmergencia(models.Model):
    motorista = models.ForeignKey(Motorista, related_name='contactos_emergencia', on_delete=models.CASCADE)
    nombre_contacto = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre_contacto} ({self.parentesco}) - {self.motorista}"

class Moto(models.Model):
    patente = models.CharField(max_length=10, unique=True, verbose_name="Patente/Matrícula")
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True, verbose_name="Año")
    numero_chasis = models.CharField(max_length=100, blank=True, null=True)
    motor = models.CharField(max_length=100, blank=True, null=True)
    motorista_asignado = models.ForeignKey(Motorista, related_name='motos_asignadas', on_delete=models.SET_NULL, null=True, blank=True)
    es_propiedad_empresa = models.BooleanField(default=True, verbose_name="Propietario Moto (Empresa=Sí)")

    def __str__(self):
        return self.patente

# Nuevo Modelo para Documentación de la Moto
class DocumentacionMoto(models.Model):
    moto = models.ForeignKey(Moto, related_name='documentaciones', on_delete=models.CASCADE)
    anio = models.IntegerField(verbose_name="Año Documentación")
    permiso_circulacion = models.FileField(upload_to='docs_moto/permisos/', blank=True, null=True)
    seguro_obligatorio = models.FileField(upload_to='docs_moto/seguros/', blank=True, null=True)
    revision_tecnica = models.FileField(upload_to='docs_moto/revisiones/', blank=True, null=True)

    class Meta:
        unique_together = ('moto', 'anio')

    def __str__(self):
        return f"Documentación {self.anio} - {self.moto.patente}"
    
    



#----------------------------------------nuevos modelos-evaluacion-3

class TipoMovimiento(models.Model):
    """
    Guarda los tipos de movimientos (ej: Retiro, Entrega, Devolución)
    """
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Asignacion(models.Model):
    """
    Registra la asignación de un Motorista a una Farmacia.
    """
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE, verbose_name="Motorista Asignado")
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, verbose_name="Farmacia Asignada")
    fecha_asignacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Asignación")

    class Meta:
        unique_together = ('motorista', 'farmacia')

    def __str__(self):
        return f"{self.motorista.nombres} asignado a {self.farmacia.nombre}"

# (Al final de App/models.py)

class Movimiento(models.Model):
    """
    Registra cada movimiento (retiro, entrega, etc.)
    """
    # --- ¡LISTA DE ESTADOS ACTUALIZADA! ---
    ESTADOS = (
        # ('asignado', 'Asignado'), <-- ELIMINADO
        ('en_ruta', 'En Ruta'),
        ('entregado', 'Entregado'),
        ('fallido', 'Fallido'),
        ('anulado', 'Anulado'),
    )
    
    farmacia = models.ForeignKey(
        Farmacia, 
        on_delete=models.PROTECT, 
        verbose_name="Farmacia Origen"
    )
    
    motorista = models.ForeignKey(Motorista, on_delete=models.PROTECT, verbose_name="Motorista (Actual)")
    tipo_movimiento = models.ForeignKey(TipoMovimiento, on_delete=models.PROTECT, verbose_name="Tipo de Movimiento")
    observacion = models.TextField(blank=True, null=True, verbose_name="Observación")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    
    status = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='en_ruta', # <-- ¡VALOR POR DEFECTO ACTUALIZADO!
        verbose_name="Estado"
    )
    motorista_original = models.ForeignKey(
        Motorista, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='movimientos_reemplazados',
        verbose_name="Motorista Original (si fue reemplazado)"
    )

    farmacia_destino = models.ForeignKey(
        Farmacia, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        verbose_name="Farmacia Destino (solo traslados)",
        related_name='movimientos_destino' 
    )

    def __str__(self):
        return f"{self.tipo_movimiento.nombre} - {self.motorista.nombres} ({self.get_status_display()})"

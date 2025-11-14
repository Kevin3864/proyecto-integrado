from django.contrib import admin

from .models import Motorista, Moto, Farmacia, Region, Provincia, Comuna,TipoMovimiento, Asignacion, Movimiento



# Le decimos a Django que registre cada modelo en el panel de admin
admin.site.register(Motorista)
admin.site.register(Moto)
admin.site.register(Farmacia)


admin.site.register(Region)
admin.site.register(Provincia)
admin.site.register(Comuna)

#----nuevos registros-evaluacion-3
admin.site.register(TipoMovimiento)
admin.site.register(Asignacion)
admin.site.register(Movimiento)
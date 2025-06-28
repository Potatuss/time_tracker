from django.contrib import admin
from .models import Cliente, Proyecto, Etiqueta, EntradaTiempo

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'email')
    list_editable = ('activo',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'email', 'telefono', 'activo')
        }),
        ('Detalles Adicionales', {
            'fields': ('direccion',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cliente', 'estado', 'fecha_inicio', 'fecha_fin_estimada', 'total_horas_trabajadas')
    list_filter = ('estado', 'cliente', 'fecha_inicio')
    search_fields = ('nombre', 'cliente__nombre', 'descripcion')
    list_editable = ('estado',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'total_horas_trabajadas', 'total_facturado')
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'cliente', 'estado')
        }),
        ('Descripción', {
            'fields': ('descripcion',)
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real')
        }),
        ('Financiero', {
            'fields': ('tarifa_por_hora', 'presupuesto_estimado'),
            'classes': ('collapse',)
        }),
        ('Información Calculada', {
            'fields': ('total_horas_trabajadas', 'total_facturado'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'color', 'fecha_creacion')
    search_fields = ('nombre',)
    readonly_fields = ('fecha_creacion',)

class EtiquetaInline(admin.TabularInline):
    model = EntradaTiempo.etiquetas.through
    extra = 1
    verbose_name = "Etiqueta"
    verbose_name_plural = "Etiquetas"

@admin.register(EntradaTiempo)
class EntradaTiempoAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'fecha', 'hora_inicio', 'hora_fin', 'horas', 'usuario', 'facturado')
    list_filter = ('fecha', 'proyecto__cliente', 'proyecto', 'usuario', 'facturado', 'etiquetas')
    search_fields = ('proyecto__nombre', 'descripcion', 'usuario__username')
    list_editable = ('facturado',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('usuario', 'proyecto', 'fecha')
        }),
        ('Tiempo', {
            'fields': ('hora_inicio', 'hora_fin', 'horas')
        }),
        ('Descripción y Etiquetas', {
            'fields': ('descripcion', 'etiquetas')
        }),
        ('Estado', {
            'fields': ('facturado',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('etiquetas',)
    
    def save_model(self, request, obj, form, change):
        if not obj.usuario_id:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

# Personalizar el título del admin
admin.site.site_header = "Time Tracker - Panel de Administración"
admin.site.site_title = "Time Tracker"
admin.site.index_title = "Gestión de Tiempo y Proyectos"
# tracker/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['nombre']
        
    def __str__(self):
        return self.nombre


class Proyecto(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('pausado', 'Pausado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='proyectos')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    activo = models.BooleanField(default=True)
    color = models.CharField(max_length=7, default='#007bff')  # Color hex para el calendario
    tarifa_hora = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    class Meta:
        ordering = ['cliente__nombre', 'nombre']
        unique_together = ['cliente', 'nombre']
        
    def __str__(self):
        return f"{self.cliente.nombre} - {self.nombre}"
    
    @property
    def total_horas(self):
        return self.entradas_tiempo.aggregate(
            total=models.Sum('horas'))['total'] or 0


class EntradaTiempo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entradas_tiempo')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='entradas_tiempo')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    horas = models.DecimalField(max_digits=5, decimal_places=2)  # Calculado automáticamente
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha', '-hora_inicio']
        verbose_name = 'Entrada de Tiempo'
        verbose_name_plural = 'Entradas de Tiempo'
        
    def __str__(self):
        return f"{self.proyecto.nombre} - {self.fecha} ({self.horas}h)"
    
    def save(self, *args, **kwargs):
        # Calcular horas automáticamente si no se proporciona
        if not self.horas:
            from datetime import datetime, timedelta
            inicio = datetime.combine(self.fecha, self.hora_inicio)
            fin = datetime.combine(self.fecha, self.hora_fin)
            
            # Manejar trabajo nocturno
            if fin <= inicio:
                fin += timedelta(days=1)
            
            self.horas = (fin - inicio).total_seconds() / 3600
            
        super().save(*args, **kwargs)


class Categoria(models.Model):
    """Categorías para clasificar las entradas de tiempo"""
    nombre = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#007bff')
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nombre']
        
    def __str__(self):
        return self.nombre


# Opcional: Relación many-to-many entre EntradaTiempo y Categoria
class EntradaCategoria(models.Model):
    entrada = models.ForeignKey(EntradaTiempo, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['entrada', 'categoria']
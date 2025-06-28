# tracker/urls.py
from django.urls import path # type: ignore
from . import views

app_name = 'tracker'

urlpatterns = [
    # Páginas principales
    path('', views.dashboard, name='dashboard'),
    path('reportes/', views.reportes, name='reportes'),
    
    # API para el calendario
    path('api/entradas/', views.api_entradas, name='api_entradas'),
    
    # Gestión de entradas
    path('entradas/nueva/', views.nueva_entrada, name='nueva_entrada'),
    path('entradas/editar/<int:entrada_id>/', views.editar_entrada, name='editar_entrada'),
    path('entradas/eliminar/<int:entrada_id>/', views.eliminar_entrada, name='eliminar_entrada'),
    
    # Gestión de proyectos
    path('proyectos/crear/', views.crear_proyecto, name='crear_proyecto'),
    
    # Clientes
    path('clientes/', views.clientes, name='clientes'),
]
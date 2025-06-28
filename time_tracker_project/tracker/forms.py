from django import forms
from django.contrib.auth.models import User
from .models import EntradaTiempo, Cliente, Proyecto, Etiqueta
from datetime import datetime, date

class EntradaTiempoForm(forms.ModelForm):
    class Meta:
        model = EntradaTiempo
        fields = ['proyecto', 'fecha', 'hora_inicio', 'hora_fin', 'horas', 'descripcion', 'etiquetas']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'horas': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.25',
                'min': '0.25',
                'readonly': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe el trabajo realizado...'
            }),
            'proyecto': forms.Select(attrs={'class': 'form-control'}),
            'etiquetas': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar proyectos activos
        self.fields['proyecto'].queryset = Proyecto.objects.filter(estado='activo')
        
        # Configurar fecha por defecto
        if not self.instance.pk:
            self.fields['fecha'].initial = date.today()
    
    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        horas = cleaned_data.get('horas')
        
        # Validar que hora_fin sea posterior a hora_inicio
        if hora_inicio and hora_fin:
            if hora_fin <= hora_inicio:
                raise forms.ValidationError('La hora de fin debe ser posterior a la hora de inicio.')
            
            # Auto-calcular horas si no están definidas
            if not horas:
                inicio_minutos = hora_inicio.hour * 60 + hora_inicio.minute
                fin_minutos = hora_fin.hour * 60 + hora_fin.minute
                
                if fin_minutos < inicio_minutos:
                    fin_minutos += 24 * 60
                
                diferencia_minutos = fin_minutos - inicio_minutos
                cleaned_data['horas'] = round(diferencia_minutos / 60, 2)
        
        return cleaned_data

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'cliente@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+595 XXX XXX XXX'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección del cliente'
            }),
        }

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'cliente', 'fecha_inicio', 'fecha_fin_estimada', 'tarifa_por_hora', 'presupuesto_estimado']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proyecto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del proyecto'
            }),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fecha_fin_estimada': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'tarifa_por_hora': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'presupuesto_estimado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo clientes activos
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)
        
        # Fecha de inicio por defecto
        if not self.instance.pk:
            self.fields['fecha_inicio'].initial = date.today()

class ReporteForm(forms.Form):
    PERIODO_CHOICES = [
        ('', 'Seleccionar período...'),
        ('hoy', 'Hoy'),
        ('ayer', 'Ayer'),
        ('esta_semana', 'Esta semana'),
        ('semana_pasada', 'Semana pasada'),
        ('este_mes', 'Este mes'),
        ('mes_pasado', 'Mes pasado'),
        ('personalizado', 'Período personalizado'),
    ]
    
    FORMATO_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
    ]
    
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(activo=True),
        required=False,
        empty_label="Todos los clientes",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    proyecto = forms.ModelChoiceField(
        queryset=Proyecto.objects.filter(estado='activo'),
        required=False,
        empty_label="Todos los proyectos",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    formato_exportacion = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        initial='excel',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        periodo = cleaned_data.get('periodo')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if periodo == 'personalizado':
            if not fecha_inicio or not fecha_fin:
                raise forms.ValidationError('Para período personalizado, ambas fechas son requeridas.')
            
            if fecha_inicio > fecha_fin:
                raise forms.ValidationError('La fecha de inicio debe ser anterior a la fecha de fin.')
        
        return cleaned_data
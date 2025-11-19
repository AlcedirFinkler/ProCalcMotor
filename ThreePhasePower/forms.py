from django import forms
from django.core.exceptions import ValidationError

class MotorCalculoForm(forms.Form):
    POLOS_CHOICES = [
        (2, '2 polos'),
        (4, '4 polos'),
        (6, '6 polos'),
        (8, '8 polos'),
        (10, '10 polos'),
        (12, '12 polos'),
    ]
    
    FREQUENCIA_CHOICES = [
        (50, '50 Hz'),
        (60, '60 Hz'),
    ]
    
    diametro = forms.FloatField(
        label='Diâmetro do Rotor (D) em mm',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 110',
            'step': '0.1'
        })
    )
    
    comprimento = forms.FloatField(
        label='Comprimento Axial (L) em mm',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 70',
            'step': '0.1'
        })
    )
    
    polos = forms.ChoiceField(
        label='Número de Polos',
        choices=POLOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    frequencia = forms.ChoiceField(
        label='Frequência da Rede',
        choices=FREQUENCIA_CHOICES,
        initial=60,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class CarcacaSelecaoForm(forms.Form):
    """Formulário para seleção de carcaça e visualização de potências por número de polos"""
    CARCACA_CHOICES = [
        ('63', 'Carcaça 63'),
        ('71', 'Carcaça 71'),
        ('80', 'Carcaça 80'),
        ('90S', 'Carcaça 90S'),
        ('90L', 'Carcaça 90L'),
        ('100L', 'Carcaça 100L'),
        ('112M', 'Carcaça 112M'),
        ('132S', 'Carcaça 132S'),
        ('132M', 'Carcaça 132M'),
        ('160M', 'Carcaça 160M'),
        ('160L', 'Carcaça 160L'),
        ('180M', 'Carcaça 180M'),
        ('180L', 'Carcaça 180L'),
        ('200L', 'Carcaça 200L'),
        ('225S/M', 'Carcaça 225S/M'),
        ('250S/M', 'Carcaça 250S/M'),
        ('280S/M', 'Carcaça 280S/M'),
        ('315S/M', 'Carcaça 315S/M'),
        ('355M/L', 'Carcaça 355M/L'),
        ('355A/B', 'Carcaça 355A/B'),
        ('400', 'Carcaça 400'),
    ]
    
    carcaca = forms.ChoiceField(
        label='Tipo de Carcaça',
        choices=CARCACA_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'carcaca-select'
        })
    )
from django import forms
from .models import *

class MyRecipeInfoForm(forms.ModelForms):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'MyRecipe Title',
        'id': 'titleinput',
    }), label='MyRecipe Title', required=True)
    serves = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Servings',
        'id': 'servesinput',
        'min': '1',
    }), label='Servings', required=True)
    time = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ready in ... minutes',
        'id': 'timeinput',
        'min': '1',
    }), label='Ready in ... minutes', required=True)
    wine_pairing = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Wine Pairing',
        'id': 'wineinput',
    }), label='Wine Pairing', required=False)
    
    class Meta:
        model = MyRecipe
        fields = (
            'title',
            'serves',
            'time',
            'wine_pairing',
        )


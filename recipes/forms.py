from django import forms
from django.forms import modelformset_factory
from .models import *

class MyRecipeInfoForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'MyRecipe Title',
        'id': 'titleinput',
        'oninput': 'checktext(id);'
    }), label='MyRecipe Title', required=True)
    serves = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Servings',
        'id': 'servesinput',
        'min': '1',
        'oninput': 'checknumber(id);'
    }), label='Servings', required=True)
    time = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ready in ... minutes',
        'id': 'timeinput',
        'min': '1',
        'oninput': 'checknumber(id);'
    }), label='Ready in ... minutes', required=True)
    image = forms.ChoiceField(widget=forms.RadioSelect(), choices=MyRecipe.IMAGE_CHOICES, required=True)
    wine_pairing = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'id': 'wineinput',
        'rows': '2',
        'placeholder': 'Enter wine pairings or other drinks (optional)'
    }), required=False)
    
    class Meta:
        model = MyRecipe
        fields = (
            'title',
            'serves',
            'time',
            'wine_pairing',
            'image'
        )

class IngredientsForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingredient name',
        'oninput': 'checktext(id);'
    }), label='Ingredient name', required=True)
    amount = forms.DecimalField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Amount',
        'oninput': 'checktext(id);' 
        }), label='Amount', required=True)
    unit = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Units (optional)',
    }), label='Units', required=False)
    meta = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Other information about ingredient (optional)',
        'rows': '2'
    }), required=False)
    class Meta:
        model = MyRecipeIngredients
        fields = (
        'name',
        'amount',
        'unit',
        'meta'
    )

IngredientsFormset = modelformset_factory(
    MyRecipeIngredients, 
    form=IngredientsForm, 
    extra=1)

class InstructionsForm(forms.ModelForm):
    step = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Step information',
        'rows': '2',
        'oninput': 'checktext(id);'
    }), required=True)
    number = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Number',
        'min': '1',
        'value': '1',
        'oninput': 'checknumber(id);' 
        }), label='Number', required=True)
    class Meta:
        model = MyRecipeInstructions
        fields = (
            'number',
            'step'
        )

InstructionsFormset = modelformset_factory(
    MyRecipeInstructions, 
    form=InstructionsForm, 
    extra=1)
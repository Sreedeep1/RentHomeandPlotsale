from django import forms
from .models import tbl_category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = tbl_category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            })
        }

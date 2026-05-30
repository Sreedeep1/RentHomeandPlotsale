from django import forms
from .models import *

class PropertyForm(forms.ModelForm):
    class Meta:
        model = tbl_property
        exclude = ['owner', 'created_at']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter property description'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property title'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full address'
            }),
           
            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of bedrooms'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of bathrooms'
            }),
            
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class PropertyImageForm(forms.Form):
    image = forms.ImageField(
        widget=MultipleFileInput(attrs={
            'multiple': True
        }),
        required=True,
        label='Add More Images',
        help_text='Select multiple images (max 5MB each)'
    )

    def clean_image(self):
        images = self.files.getlist('image')

        if not images:
            raise forms.ValidationError("Please select at least one image.")

        for image in images:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    f"{image.name} exceeds 5MB limit."
                )

            allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
            if image.content_type not in allowed_types:
                raise forms.ValidationError(
                    f"{image.name} is not a supported image type."
                )

        return images
    

class PlotForm(forms.ModelForm):
    class Meta:
        model = tbl_plot_for_sale
        fields = [
             'title', 'description',
            'address', 'area', 'price',
            'plot_type',
            'water', 'electricity', 'gated_community',
            
        ]


class PlotImageForm(forms.ModelForm):
    class Meta:
        model = tbl_plot_images
        fields = ['image']
from django import forms
from .models import Widget

class WidgetCreationForm(forms.ModelForm):
    class Meta:
        model = Widget
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

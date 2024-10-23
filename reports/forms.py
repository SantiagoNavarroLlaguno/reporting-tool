from django import forms
from .models import Report
from widgets.models import Widget

class ReportForm(forms.ModelForm):
    widgets = forms.ModelMultipleChoiceField(
        queryset=Widget.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Widgets",
        required=False
    )
    
    information = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Report Information",
        required=False
    )

    class Meta:
        model = Report
        fields = ['title', 'widgets', 'csv_file', 'information']

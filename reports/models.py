from django.db import models
from django.conf import settings
from widgets.models import Widget

class Report(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    data = models.JSONField(default=dict)  # For holding widget data
    created_at = models.DateTimeField(auto_now_add=True)
    information = models.TextField(blank=True)  # Optional information field
    csv_file = models.FileField(upload_to='reports/csvs/', blank=True, null=True)
    widgets = models.ManyToManyField(Widget, blank=True)

    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d')}"

class HistoricalData(models.Model):
    date = models.DateField()
    value = models.FloatField()  # e.g., sales value or other numerical data

    def __str__(self):
        return f"{self.date}: {self.value}"

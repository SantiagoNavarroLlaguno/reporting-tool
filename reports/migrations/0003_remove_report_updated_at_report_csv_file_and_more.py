# Generated by Django 5.1.1 on 2024-09-19 04:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0002_historicaldata"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="report",
            name="updated_at",
        ),
        migrations.AddField(
            model_name="report",
            name="csv_file",
            field=models.FileField(blank=True, null=True, upload_to="reports/csvs/"),
        ),
        migrations.AddField(
            model_name="report",
            name="information",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="report",
            name="data",
            field=models.JSONField(default=dict),
        ),
    ]

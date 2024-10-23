from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),  # For listing all reports
    path('create/', views.create_report_view, name='create_report'),
    path('<int:report_id>/', views.report_detail, name='report_detail'),
    path('<int:report_id>/edit/', views.edit_report, name='edit_report'),  # Ensure the argument matches
    path('<int:report_id>/delete/', views.delete_report, name='delete_report'),
    path('<int:report_id>/preview/', views.preview_csv, name='preview_csv'),  # Add the preview URL here
    path('<int:report_id>/download/', views.download_csv_report, name='download_csv'),  # Add the download CSV URL
    path('upload_csv/', views.upload_csv, name='upload_csv'),
]

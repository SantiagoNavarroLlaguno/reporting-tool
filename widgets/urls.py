from django.urls import path
from .views import create_widget, list_widgets, edit_widget, delete_widget

# Regular URL patterns for HTML-based views
urlpatterns = [
    path('', list_widgets, name='widget_list'),
    path('create/', create_widget, name='create_widget'),
    path('edit/<int:widget_id>/', edit_widget, name='edit_widget'),
    path('delete/<int:widget_id>/', delete_widget, name='delete_widget'),
]

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Widget
from .serializers import WidgetSerializer
from .forms import WidgetCreationForm
from nimbus.utils import generate_widget_from_text


PRELOADED_WIDGET_IDS = [1, 7, 16, 17, 18, 19, 20]  # IDs of the preloaded widgets

class WidgetViewSet(viewsets.ModelViewSet):
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

@login_required
def create_widget(request):
    if request.method == 'POST':
        form = WidgetCreationForm(request.POST)

        # Check if the user wants to generate a widget from GPT-Neo
        if request.POST.get('use_gpt', False):  # This will be set if the user opts to use GPT-Neo
            user_input = request.POST.get('description', '')
            generated_code = generate_widget_from_text(user_input)

            # Save the generated widget code
            widget = Widget.objects.create(
                name=request.POST.get('name'),
                description=user_input,
                code=generated_code,  # Assuming your Widget model has a 'code' field for functionality
                created_by=request.user
            )
            return redirect('widget_list')

        # If not using GPT-Neo, continue with the regular manual widget creation
        if form.is_valid():
            widget = form.save(commit=False)
            widget.created_by = request.user
            widget.save()
            return redirect('widget_list')
    else:
        form = WidgetCreationForm()

    return render(request, 'widgets/create_widget.html', {'form': form})


@login_required
def list_widgets(request):
    widgets = Widget.objects.all()  # Show all widgets, including preloaded

    return render(request, 'widgets/list_widgets.html', {
        'widgets': widgets,
        'preloaded_widget_ids': PRELOADED_WIDGET_IDS,
    })

@login_required
def edit_widget(request, widget_id):
    widget = get_object_or_404(Widget, id=widget_id, created_by=request.user)
    if request.method == 'POST':
        widget.name = request.POST.get('name')
        widget.description = request.POST.get('description')
        widget.save()
        return redirect('widget_list')
    return render(request, 'widgets/edit_widget.html', {'widget': widget})

@login_required
def delete_widget(request, widget_id):
    widget = get_object_or_404(Widget, id=widget_id, created_by=request.user)
    if request.method == 'POST':
        widget.delete()
        return redirect('widget_list')
    return render(request, 'widgets/delete_widget.html', {'widget': widget})


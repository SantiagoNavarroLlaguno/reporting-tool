import os
import pandas as pd
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.views.generic.edit import UpdateView, DeleteView
from .models import Report
from .forms import ReportForm
from .utils import generate_report, generate_report_preview
from widgets.models import Widget
from widgets.views import PRELOADED_WIDGET_IDS


def report_list(request):
    reports = Report.objects.filter(user=request.user)
    return render(request, 'reports/report_list.html', {'reports': reports})

def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    # Fetch the widget_ids used in the report
    widget_ids = report.widgets.values_list('id', flat=True)

    # Safely get the last widget ID if there are any widgets applied
    last_widget_id = widget_ids.last() if widget_ids.exists() else None

    # Render the template with report data and pass last_widget_id
    return render(request, 'reports/report_detail.html', {
        'report': report, 
        'information': report.information,
        'data': report.data,  # Pass the report data to the template
        'last_widget_id': last_widget_id  # Pass the last widget ID for CSV download
    })

def create_report_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)

        # Check if form is valid
        if form.is_valid():
            print('Form is valid')

            title = form.cleaned_data['title']
            widgets = form.cleaned_data['widgets']  # Get the selected widgets
            print(f'Selected widgets: {widgets}')
            
            information = form.cleaned_data['information']
            print(f'Report information: {information}')

            # Handle CSV file upload
            csv_file = request.FILES.get('csv_file', None)
            csv_file_path = None
            if csv_file:
                print('CSV file detected, saving...')
                fs = FileSystemStorage()
                csv_file_path = fs.save(csv_file.name, csv_file)
                csv_file_path = fs.path(csv_file_path)
                print(f'CSV file saved at: {csv_file_path}')
            else:
                print('No CSV file uploaded')

            # Create the report object first
            report = Report.objects.create(
                user=request.user,
                title=title,
                information=information,
                csv_file=csv_file_path
            )
            
            # Set the selected widgets for the report
            report.widgets.set(widgets)

            # Generate the report (now treating the returned value as the DataFrame)
            final_df = generate_report(
                user=request.user,
                widget_ids=widgets.values_list('id', flat=True),
                csv_file_path=csv_file_path,
                report=report
            )

            # Save the report object again after generating the data
            report.save()
            print(f'Report saved with widgets: {widgets}')

            return redirect('report_detail', report_id=report.pk)
        else:
            print(f'Form is invalid: {form.errors}')  # Print form errors for easier debugging
    else:
        form = ReportForm()

    return render(request, 'reports/create_report.html', {'form': form})


def preview_csv(request, report_id):
    if request.method == 'POST':
        widget_ids_str = request.POST.get('widgets', '')
        widget_ids = [int(widget_id) for widget_id in widget_ids_str.split(',') if widget_id.isdigit()]

        report = get_object_or_404(Report, id=report_id)
        csv_file_path = report.csv_file

        # Generate a preview of the report data up to the selected widgets
        preview_data = generate_report_preview(widget_ids, csv_file_path)
        
        return JsonResponse({'preview': preview_data})

def edit_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    form = ReportForm(request.POST or None, request.FILES or None, instance=report)

    if request.method == 'POST':
        # Step 1: Fetch widget IDs from POST request and split them properly
        widget_ids_str = request.POST.get('widgets', '')  # Fetch widgets from form (default to empty string if not found)
        widget_ids = [int(widget_id) for widget_id in widget_ids_str.split(',') if widget_id.isdigit()]  # Convert to integers

        print("Widget IDs after splitting:", widget_ids)  # Debug: Check if widget IDs are correctly split and converted

        # Step 2: Create a QuerySet of widgets and preserve the order based on widget IDs
        widgets_qs = Widget.objects.filter(id__in=widget_ids).order_by(
            models.Case(
                *[models.When(id=widget_id, then=pos) for pos, widget_id in enumerate(widget_ids)],
                output_field=models.IntegerField(),
            )
        )
        print("Ordered widgets in queryset:", widgets_qs)  # Debug: Verify the order of widgets

        # Update the request.POST to pass the actual widget objects to the form
        form = ReportForm(instance=report, data=request.POST)
        form.data = form.data.copy()  # Make the form data mutable

        # Provide the correct widget instances to the form's 'widgets' field
        form.data.setlist('widgets', [str(widget.id) for widget in widgets_qs])

        if form.is_valid():
            # Save the report information first
            report = form.save(commit=False)
            report.information = form.cleaned_data['information']

            # Save widgets to the report
            report.widgets.set(widgets_qs)  # Set the widget queryset

            # Step 3: Ensure widget data and order are stored in the `data` field of the report
            widget_data = {}
            for widget_id in widget_ids:  # Iterate over the widget_ids in the correct order
                widget = widgets_qs.get(id=widget_id)  # Ensure we're fetching the widget by the correct order
                widget_data[widget.name] = widget.description

            report.data = widget_data  # Store the widget data in the report's data field
            report.save()  # Ensure the report is saved after updating the `data` field

            print("Widget data being saved to report's data field:", report.data)  # Debug: Ensure the data is being updated

            # Handle CSV upload if any
            csv_file = request.FILES.get('csv_file', None)
            if csv_file:
                fs = FileSystemStorage()
                csv_file_path = fs.save(csv_file.name, csv_file)
                report.csv_file = fs.path(csv_file_path)

            # Re-generate report data based on widgets and csv_file
            generate_report(
                user=request.user,
                widget_ids=widget_ids,  # Pass the split widget IDs
                csv_file_path=report.csv_file,
                report=report
            )

            return redirect('report_detail', report_id=report.id)
        else:
            print("Form errors:", form.errors)  # Add this line to show form errors in the console

    current_csv = report.csv_file if report.csv_file else "No CSV uploaded yet"
    widgets = Widget.objects.all()

    # Sort selected_widgets based on the order they were saved in the report.data field
    selected_widgets = report.widgets.all()

    # Check if report.data is a dictionary before calling .keys()
    if isinstance(report.data, dict):
        widget_order = list(report.data.keys())
        # Handle missing widgets in widget_order gracefully
        selected_widgets = sorted(selected_widgets, key=lambda w: widget_order.index(w.name) if w.name in widget_order else -1)
    else:
        print("Warning: report.data is not a dictionary. It is of type:", type(report.data))
        selected_widgets = list(selected_widgets)  # Just convert to a list without reordering

    return render(request, 'reports/edit_report.html', {
        'form': form,
        'report': report,
        'widgets': widgets,
        'selected_widgets': selected_widgets,  # Corrected order based on saved data
        'current_csv': current_csv,
        'preloaded_widget_ids': PRELOADED_WIDGET_IDS  # Pass the preloaded IDs to the template
    })



# Delete Report View (Confirmation and deletion)
def delete_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        report.delete()
        return redirect('report_list')

    return render(request, 'reports/delete_report.html', {'report': report})

def upload_csv(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        fs = FileSystemStorage()
        file_path = fs.save(csv_file.name, csv_file)
        file_url = fs.url(file_path)

        # Use pandas to read the CSV file
        df = pd.read_csv(fs.path(file_path))
        # Example: Show the first few rows in the template
        data = df.head().to_html()

        return render(request, 'reports/upload_csv.html', {'data': data})

    return render(request, 'reports/upload_csv.html')

def download_csv_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    # Generate the report to get the final modified DataFrame
    final_df = generate_report(
        user=request.user,
        widget_ids=report.widgets.values_list('id', flat=True),
        csv_file_path=report.csv_file,
        report=report
    )

    if final_df is not None:
        # Convert the final DataFrame to a CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report.title}.csv"'

        final_df.to_csv(path_or_buf=response, index=False)  # Save the final DataFrame as CSV to the response
        return response
    else:
        return HttpResponse("No data to export.", status=404)


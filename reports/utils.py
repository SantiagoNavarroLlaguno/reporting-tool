import os
from django.conf import settings
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from widgets.models import Widget
from .models import Report, HistoricalData


def execute_generated_code(generated_code, df):
    # Sandbox setup: Create a local environment for executing the code
    local_env = {'df': df, 'pd': pd, 'np': np}
    
    try:
        print(f"Generated code:\n{generated_code}")  # Debug: Log the generated code
        
        # Execute the generated code, making sure we pass it the correct context
        exec(generated_code, {}, local_env)
        
        # We expect the function to have modified the DataFrame in place.
        if 'df' in local_env:
            return local_env['df']
        else:
            raise ValueError("Generated code did not return or modify the DataFrame as expected.")
    except Exception as e:
        print(f"Error executing generated code: {str(e)}")
        return None



def generate_report(user, widget_ids, csv_file_path=None, report=None):
    print(f'Generating report for user: {user} with widgets: {widget_ids}')
    report_data = {}
    final_df = None  # Store the final DataFrame after all widgets

    # Sort the widgets based on the order they were passed in
    widgets_qs = Widget.objects.filter(id__in=widget_ids)
    ordered_widgets = [widgets_qs.get(id=widget_id) for widget_id in widget_ids]

    # Track whether the Yesterday Trimmer needs to be applied
    apply_yesterday_trimmer = False

    # Fetch and add widget data based on the order of widget execution
    for widget in ordered_widgets:
        report_data[widget.name] = widget.description

        # Check if we need to apply the Yesterday Trimmer logic
        if widget.name == "Yesterday Trimmer":
            apply_yesterday_trimmer = True

    # Process CSV if provided
    if csv_file_path:
        df = pd.read_csv(csv_file_path)
        df.columns = df.columns.str.lower()  # Normalize column names
        print("Normalized column names:\n", df.columns)  # Debugging

        # Apply widgets in order
        for widget in ordered_widgets:
            if widget.name == "Yesterday Trimmer" and 'date' in df.columns:
                print("Applying Yesterday Trimmer...")
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                yesterday_date = (datetime.now() - timedelta(days=1)).date()
                df = df[df['date'].dt.date != yesterday_date]
                print("Trimmed DataFrame:\n", df.head())

            elif widget.name == "Column Dropper":
                columns_to_drop = ["email", "website"]
                print(f"Dropping columns: {columns_to_drop}")
                df = df.drop(columns=columns_to_drop, errors='ignore')
                print("DataFrame after Column Dropper:\n", df.head())

            elif widget.name == "Uppercase Name Converter":
                df['first name'] = df['first name'].str.upper()
                df['last name'] = df['last name'].str.upper()
                print("DataFrame after Uppercase Name Converter:\n", df.head())

            elif widget.name == "Date Filter":
                start_date = "2024-09-01"
                end_date = "2024-10-12"
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
                print("DataFrame after Date Filter:\n", df.head())

            elif widget.name == "Row Deduplicator":
                df = df.drop_duplicates(subset=['customer id'])
                print("DataFrame after Row Deduplicator:\n", df.head())

            # Capture the final DataFrame after all widgets have been applied
            final_df = df

    # Save report data to existing report or create a new one
    if report:
        report.data = report_data
        report.save()
        print('Existing report updated with new data.')
    else:
        report = Report.objects.create(user=user, title="Generated Report", data=report_data)
        print('New report created.')

    # Return the final modified DataFrame for further use (like CSV download)
    return final_df


def generate_report_preview(widget_ids, csv_file_path):
    report_data = {}

    print(f"Widget IDs for preview: {widget_ids}")
    print(f"CSV file path for preview: {csv_file_path}")

    if csv_file_path:
        try:
            df = pd.read_csv(csv_file_path)
            print("CSV loaded successfully.")
            print("Initial DataFrame:\n", df.head())  # Debugging: Check the first few rows of the loaded CSV

            df.columns = df.columns.str.lower()
            print("Normalized column names:\n", df.columns)  # Debugging: Check if columns are normalized correctly
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return {"error": "Error loading CSV"}

        widgets_qs = Widget.objects.filter(id__in=widget_ids)
        ordered_widgets = [widgets_qs.get(id=widget_id) for widget_id in widget_ids]
        print(f"Ordered widgets: {[widget.name for widget in ordered_widgets]}")  # Debugging: Check the widget names in order

        # Apply widgets in order up to the selected point
        for widget in ordered_widgets:
            print(f"Applying widget: {widget.name}")

            if widget.name == "Yesterday Trimmer":
                print("Applying Yesterday Trimmer logic")
                try:
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'], errors='coerce')
                        print(f"Parsed 'date' column:\n", df['date'])

                        yesterday = datetime.now() - timedelta(days=1)
                        yesterday_date = yesterday.date()
                        print("Yesterday's date:", yesterday_date)

                        df_before_trimming = df.copy()
                        df = df[df['date'].dt.date != yesterday_date]
                        print(f"DataFrame after trimming:\n", df.head())

                        if df.equals(df_before_trimming):
                            print("No rows removed. Check if date filtering is working properly.")
                    else:
                        print("No 'date' column found in the DataFrame.")
                except Exception as e:
                    print(f"Error applying Yesterday Trimmer: {e}")
                    return {"error": "Error applying Yesterday Trimmer"}

            elif widget.name == "Column Dropper":
                try:
                    # Hardcode the columns to drop for now
                    columns_to_drop = ["email", "website"]  # Adjust based on your use case
                    print(f"Applying Column Dropper with columns to drop: {columns_to_drop}")

                    # Manually apply the logic in Python here
                    df = df.drop(columns=columns_to_drop, axis=1, errors='ignore')  # Drop the specified columns
                    print(f"DataFrame after applying {widget.name}:\n", df.head())  # Debugging: Check the DataFrame after applying the widget
                except Exception as e:
                    print(f"Error applying {widget.name}: {e}")
                    return {"error": f"Error applying {widget.name}"}

            elif widget.name == "Uppercase Name Converter":
                try:
                    print("Converting names to uppercase")
                    before_conversion = df[['first name', 'last name']].copy()  # Keep track of names before change
                    df['first name'] = df['first name'].str.upper()
                    df['last name'] = df['last name'].str.upper()
                    print(f"Names before conversion:\n{before_conversion.head()}")
                    print(f"Names after conversion:\n{df[['first name', 'last name']].head()}")
                except Exception as e:
                    print(f"Error applying Uppercase Name Converter: {e}")
                    return {"error": f"Error applying {widget.name}"}

            elif widget.name == "Date Filter":
                try:
                    start_date = "2024-09-01"  # Define start date (hardcoded for now, can be passed dynamically)
                    end_date = "2024-10-12"  # Define end date (hardcoded for now, can be passed dynamically)
                    print(f"Filtering rows between {start_date} and {end_date}")
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    before_filtering = df.copy()  # Keep track of DataFrame before filtering
                    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
                    print(f"DataFrame before filtering:\n{before_filtering.head()}")
                    print(f"DataFrame after filtering:\n{df.head()}")
                except Exception as e:
                    print(f"Error applying Date Filter: {e}")
                    return {"error": f"Error applying {widget.name}"}

            elif widget.name == "Row Deduplicator":
                try:
                    print("Removing duplicate rows based on 'customer id'")
                    before_deduplication = df.copy()  # Keep track of DataFrame before deduplication
                    
                    # Drop duplicates based only on the 'customer id' column
                    df = df.drop_duplicates(subset=['customer id'])
                    
                    print(f"DataFrame before deduplication:\n{before_deduplication.head()}")
                    print(f"DataFrame after deduplication:\n{df.head()}")
                    
                    # Debugging for ensuring rows were dropped
                    if df.equals(before_deduplication):
                        print("No duplicate rows were removed based on 'customer id'.")
                    else:
                        print("Duplicates removed successfully based on 'customer id'.")
                except Exception as e:
                    print(f"Error applying Row Deduplicator: {e}")
                    return {"error": f"Error applying {widget.name}"}

            elif widget.code:
                try:
                    print(f"Widget code for {widget.name}:\n{widget.code}")
                    df = execute_generated_code(widget.code, df)
                    print(f"DataFrame after applying {widget.name}:\n", df.head())

                    if df is None:
                        print(f"Error: DataFrame is None after applying {widget.name}")
                        return {"error": f"Widget {widget.name} failed to modify the CSV correctly."}

                except Exception as e:
                    print(f"Error applying widget {widget.name}: {e}")
                    return {"error": f"Error applying widget {widget.name}"}

        # Ensure all timestamp columns are converted to strings before returning preview data
        if df is not None:
            for col in df.columns:
                print(f"Checking column {col} for datetime type")
                if isinstance(df[col].dtype, pd.core.dtypes.dtypes.DatetimeTZDtype) or np.issubdtype(df[col].dtype, np.datetime64):
                    print(f"Converting datetime column {col} to string")
                    df[col] = df[col].dt.strftime('%Y-%m-%d')

        print("Final modified DataFrame for preview:\n", df.head())  # Debugging: Show the final state of the DataFrame

        # Convert DataFrame to JSON-serializable format
        report_data = df.to_dict(orient='records')

    return report_data










def predict_future_sales(df):
    # Ensure the date column is properly formatted
    df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Coerce errors will turn bad dates into NaT (Not a Time)
    
    # Remove rows where date parsing failed
    df = df.dropna(subset=['date'])
    
    if df.empty:
        return {"error": "No valid dates found in the CSV."}

    df = df.sort_values('date')  # Ensure data is sorted by date

    # Prepare data for the regression model
    df['date_ordinal'] = df['date'].map(pd.Timestamp.toordinal)  # Convert date to ordinal for regression
    X = df['date_ordinal'].values.reshape(-1, 1)
    y = df['value'].values

    # Train a simple linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict the next 30 days
    future_dates = pd.date_range(df['date'].max() + pd.Timedelta(days=1), periods=30).to_pydatetime()
    future_dates_ordinal = [pd.Timestamp(date).toordinal() for date in future_dates]
    future_predictions = model.predict([[d] for d in future_dates_ordinal])

    # Combine future dates and predictions into a dictionary
    future_sales = {str(date.date()): round(prediction, 2) for date, prediction in zip(future_dates, future_predictions)}

    return future_sales




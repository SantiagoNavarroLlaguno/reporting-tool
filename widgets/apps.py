from django.apps import AppConfig
from django.db.models.signals import post_migrate


class WidgetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "widgets"

    def ready(self):
        # Connect post_migrate signal
        post_migrate.connect(create_default_widgets, sender=self)


def create_default_widgets(sender, **kwargs):
    from django.apps import apps
    Widget = apps.get_model('widgets', 'Widget')  # Dynamically fetch the Widget model

    # List of widgets to be created if they don't already exist
    widgets = [
        {
            "name": "Yesterday Trimmer",
            "description": "This widget trims rows from the CSV that correspond to yesterday's date.",
            "code": """
def yesterday_trimmer(df):
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=False)
    yesterday = datetime.now().date() - timedelta(days=1)
    trimmed_df = df[df['Date'].dt.date != yesterday]
    return trimmed_df
"""
        },
        {
            "name": "Column Dropper",
            "description": "Drops specified columns from the CSV.",
            "code": """
def column_dropper(df, columns):
    return df.drop(columns, axis=1)
"""
        },
        {
            "name": "Date Filter",
            "description": "Filters rows based on a date range.",
            "code": """
def date_filter(df, start_date, end_date):
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
"""
        },
        {
            "name": "Uppercase Name Converter",
            "description": "Converts first and last names to uppercase.",
            "code": """
def uppercase_name_converter(df):
    df['first name'] = df['first name'].str.upper()
    df['last name'] = df['last name'].str.upper()
    return df
"""
        },
        {
            "name": "Null Value Filler",
            "description": "Fills null values with a default value.",
            "code": """
def null_value_filler(df, fill_value):
    return df.fillna(fill_value)
"""
        },
        {
            "name": "Row Deduplicator",
            "description": "Removes duplicate rows.",
            "code": """
def row_deduplicator(df):
    return df.drop_duplicates()
"""
        }
    ]

    # Create each widget if it doesn't already exist
    for widget_data in widgets:
        Widget.objects.get_or_create(
            name=widget_data["name"],
            defaults={
                "description": widget_data["description"],
                "code": widget_data["code"]
            }
        )

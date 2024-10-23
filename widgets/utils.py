import pandas as pd
from datetime import datetime, timedelta

def yesterday_trimmer(df):
    # Print the original DataFrame to verify the data
    print("Original DataFrame:\n", df)

    # Convert the 'Date' column to datetime, and ensure errors don't crash the function
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=False)

    # Print the parsed date column to see if the conversion was successful
    print("Parsed 'Date' column:\n", df['Date'])

    # Get yesterday's date
    yesterday = datetime.now().date() - timedelta(days=1)
    print("Yesterday's date:", yesterday)

    # Compare each date with yesterday and trim rows
    trimmed_df = df[df['Date'].dt.date != yesterday]

    # Print the DataFrame after trimming
    print("Trimmed DataFrame:\n", trimmed_df)

    # If trimming results in empty DataFrame, print warning
    if trimmed_df.empty:
        print("Warning: All rows were trimmed based on yesterday's date.")

    return trimmed_df

# Column Dropper Widget
def column_dropper(df, columns_to_drop):
    print("Original DataFrame columns:\n", df.columns)
    # Drop specified columns
    df = df.drop(columns=columns_to_drop, errors='ignore')
    print(f"Columns after dropping {columns_to_drop}:\n", df.columns)
    return df

# Date Filter Widget
def date_filter(df, start_date, end_date):
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    print(f"Filtered DataFrame from {start_date} to {end_date}:\n", filtered_df)
    return filtered_df

# Uppercase Name Converter Widget
def uppercase_names(df):
    print("Original 'first name' and 'last name':\n", df[['first name', 'last name']])
    df['first name'] = df['first name'].str.upper()
    df['last name'] = df['last name'].str.upper()
    print("Uppercased names:\n", df[['first name', 'last name']])
    return df

# Null Value Filler Widget
def fill_null_values(df, column_name, default_value):
    print(f"Null values in '{column_name}' before filling:\n", df[column_name].isna().sum())
    df[column_name] = df[column_name].fillna(default_value)
    print(f"Null values in '{column_name}' after filling:\n", df[column_name].isna().sum())
    return df

# Row Deduplicator Widget
def remove_duplicates(df, subset_columns):
    print(f"Duplicates before:\n", df.duplicated(subset=subset_columns).sum())
    df = df.drop_duplicates(subset=subset_columns, keep='first')
    print(f"Duplicates after:\n", df.duplicated(subset=subset_columns).sum())
    return df


# Example usage:
# Assuming you load your CSV into a DataFrame 'df'
df = pd.read_csv('path_to_your_csv.csv')  # Use your actual CSV path

# Test the trimming function
trimmed_df = yesterday_trimmer(df)

# Test column dropper
df = column_dropper(df, ['phone 2', 'website'])

# Test date filter
df = date_filter(df, '2024-10-01', '2024-10-31')

# Test uppercase name conversion
df = uppercase_names(df)

# Test null value filler
df = fill_null_values(df, 'email', 'no-email@example.com')

# Test row deduplication
df = remove_duplicates(df, ['customer id'])
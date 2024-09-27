import pandas as pd
import re

def rename_columns(df : pd.DataFrame):
    # Rename first column to time
    df = df.dropna(axis=1)
    df = df.drop([col for col in df.columns if "'" in col], axis=1)
    df = df.drop([col for col in df.columns if "#" in col], axis=1)
    df = df.rename(columns={'X(I)': 'Time'})


    # Regular expression to match "Integral(float1, float2)"
    pattern = r'Integral\((\d+\.\d+),(\d+\.\d+)\)'

    # Iterate over each column
    for col in df.columns:
        first_row_value = str(df[col].iloc[0])
        
        # Use regex to find the two float numbers in the string
        match = re.match(pattern, first_row_value)
        if match:
            float1 = float(match.group(1))
            float2 = float(match.group(2))
            # Calculate the median of the two floats
            median_value = round((float1 + float2) / 2, 1)
            # Rename the column
            df = df.rename(columns={col: f'{median_value}_ppm'})
    if any(index == 0 for index in df.index):
        df = df.drop(index=0, axis=0)
    df = df.astype(float)
    
    # Remove solvent (CDCl3) peak
    if '79.3_ppm' in df.columns:
        df = df.drop('79.3_ppm', axis=1)
    
    return df
import pandas as pd
import os
from pathlib import Path

# Define resampling timeframes and their output suffixes
timeframes = {
    '1min': 'M1',
    '5min': 'M5',
    '15min': 'M15',
    '1h': 'H1',
    '4h': 'H4',
    '1D': 'D1'
}

# OHLC aggregation dictionary
ohlc_dict = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}

# Base directory containing all symbol folders
base_dir = Path('/home/chris/market_data')

# Process each subdirectory (symbol folder)
for symbol_dir in base_dir.iterdir():
    if not symbol_dir.is_dir():
        continue
    
    # Path to M1_seed.csv file
    m1_seed_file = symbol_dir / 'M1_seed.csv'
    
    # Skip if M1_seed.csv doesn't exist
    if not m1_seed_file.exists():
        print(f"Skipping {symbol_dir.name}: M1_seed.csv not found")
        continue
    
    print(f"Processing {symbol_dir.name}...")
    
    try:
        # Load 1-minute data (tab-separated with Windows line endings)
        df = pd.read_csv(m1_seed_file, sep='\t', lineterminator='\r')
        
        # Strip angle brackets and whitespace from column names
        df.columns = df.columns.str.replace('<', '').str.replace('>', '').str.strip()
        
        # Combine DATE and TIME columns to create datetime index
        df['Datetime'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'])
        df.set_index('Datetime', inplace=True)
        
        # Rename columns to match OHLC format
        df.rename(columns={
            'OPEN': 'Open',
            'HIGH': 'High',
            'LOW': 'Low',
            'CLOSE': 'Close',
            'TICKVOL': 'Volume'
        }, inplace=True)
        
        # Select only required columns
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Resample to each timeframe
        for timeframe, suffix in timeframes.items():
            df_resampled = df.resample(timeframe).agg(ohlc_dict).dropna()
            output_file = symbol_dir / f'{symbol_dir.name}_{suffix}.csv'
            df_resampled.to_csv(output_file)
            print(f"  Created {output_file.name}")
        
        print(f"  Completed {symbol_dir.name}\n")
        
    except Exception as e:
        print(f"  Error processing {symbol_dir.name}: {e}\n")

print("Resampling complete!")
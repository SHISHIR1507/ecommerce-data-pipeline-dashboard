import pytest
import pandas as pd
from datetime import datetime

# Import functions from clean_data.py
# Since it's a script not structured as a package, we can import it directly
# but we need to make sure the script code runs cleanly without side effects if imported
# Fortunately we put the main execution logic under if __name__ == "__main__":
from clean_data import clean_customers, clean_orders

def test_clean_customers():
    # Setup test data
    raw_data = pd.DataFrame({
        'customer_id': ['C1', 'C1', 'C2', 'C3'],
        'name': [' Alice ', 'Alice', 'Bob', 'Charlie'],
        'email': ['ALICE@example.com', 'alice@test.com', 'bad-email', pd.NA],
        'region': ['North', ' North ', pd.NA, 'South'],
        'signup_date': ['2023-01-01', '2023-02-01', '2023-15-01', 'not-a-date']  # C1 has duplicate, C2 bad date
    })
    
    # Run function
    cleaned_df, report = clean_customers(raw_data)
    
    # Assertions
    # 1. Deduplication (C1 should exist once, keeping the latest signup date)
    assert len(cleaned_df) == 3
    alice_row = cleaned_df[cleaned_df['customer_id'] == 'C1'].iloc[0]
    assert alice_row['signup_date'] == pd.to_datetime('2023-02-01')
    
    # 2. String cleaning and email validation
    assert alice_row['name'] == 'Alice'
    assert alice_row['region'] == 'North'
    assert alice_row['email'] == 'alice@test.com' # Took the latest row's email
    assert alice_row['is_valid_email'] == True
    
    bob_row = cleaned_df[cleaned_df['customer_id'] == 'C2'].iloc[0]
    assert bob_row['is_valid_email'] == False
    assert bob_row['region'] == 'Unknown' # Missing filled with Unknown
    
    # 3. Invalid dates forced output to NaT
    assert pd.isna(bob_row['signup_date'])
    assert pd.isna(cleaned_df[cleaned_df['customer_id'] == 'C3'].iloc[0]['signup_date'])


def test_clean_orders():
    # Setup test data
    raw_data = pd.DataFrame({
        'order_id': ['O1', 'O2', 'O3', pd.NA],
        'customer_id': ['C1', 'C2', pd.NA, pd.NA], # O3 missing customer, row 4 missing both
        'product': ['Widget', 'Widget', 'Gadget', 'Gadget'],
        'amount': [100.0, pd.NA, 50.0, pd.NA], # O2 amount missing (should impute to Widget median=100)
        'order_date': ['2023-01-15', '15/01/2023', '01-15-2023', '2023-01-15'], # Different formats
        'status': ['Completed', '  PENDING ', 'canceled', 'refunded']
    })
    
    cleaned_df, report = clean_orders(raw_data)
    
    # Assertions
    # 1. Drop rows missing both order_id and customer_id
    assert len(cleaned_df) == 3
    
    # 2. Amount imputation (O2 amount should be median of Widgets = 100.0)
    o2_row = cleaned_df[cleaned_df['order_id'] == 'O2'].iloc[0]
    assert o2_row['amount'] == 100.0
    
    # 3. Status normalization
    assert o2_row['status'] == 'pending'
    assert cleaned_df[cleaned_df['order_id'] == 'O3'].iloc[0]['status'] == 'cancelled'
    
    # 4. Date parsing & year_month generation (all dates are actually Jan 15 2023)
    assert (cleaned_df['order_date'] == pd.to_datetime('2023-01-15')).all()
    assert (cleaned_df['order_year_month'] == '2023-01').all()

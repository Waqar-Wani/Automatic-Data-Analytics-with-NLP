import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# test_imports.py
from backend.data_preprocessing.data_cleaning import handle_missing_values

print("Import successful!")

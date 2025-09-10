import pandas as pd
import numpy as np
import json
import os
from typing import Callable, Optional, Union

class DataProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data: Optional[pd.DataFrame] = None

    def load_csv(self) -> pd.DataFrame:
        """Loads CSV data into a DataFrame"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"{self.file_path} does not exist.")
        self.data = pd.read_csv(self.file_path)
        return self.data

    def normalize_columns(self) -> pd.DataFrame:
        """Normalize numeric columns to 0-1 range"""
        if self.data is None:
            raise ValueError("Data not loaded.")
        numeric_columns = self.data.select_dtypes(include=[np.number]).columns
        if not numeric_columns.any():
            raise ValueError("No numeric columns to normalize.")
        for col in numeric_columns:
            min_val = self.data[col].min()
            max_val = self.data[col].max()
            if max_val == min_val:
                raise ValueError(f"Cannot normalize column {col} as max equals min.")
            self.data[col] = (self.data[col] - min_val) / (max_val - min_val)
        return self.data

    def summarize_data(self) -> pd.DataFrame:
        """Generate summary statistics for numeric columns"""
        if self.data is None:
            raise ValueError("Data not loaded.")
        summary = self.data.describe()
        return summary

    def save_json(self, output_file: str) -> None:
        """Save DataFrame to JSON"""
        if self.data is None:
            raise ValueError("Data not loaded.")
        self.data.to_json(output_file, orient="records")

    def filter_rows(self, condition_func: Callable[[pd.DataFrame], pd.Series]) -> pd.DataFrame:
        """Filter rows based on a condition function"""
        if self.data is None:
            raise ValueError("Data not loaded.")
        if not callable(condition_func):
            raise ValueError("condition_func must be a callable function.")
        self.data = self.data[condition_func(self.data)]
        return self.data

# Sample usage
if __name__ == "__main__":
    processor = DataProcessor("data.csv")
    processor.load_csv()
    processor.normalize_columns()
    summary = processor.summarize_data()
    print(summary)
    processor.save_json("output.json")
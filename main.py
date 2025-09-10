import pandas as pd
import numpy as np
import json
import os

class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def load_csv(self):
        """Loads CSV data into a DataFrame"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"{self.file_path} does not exist.")
        self.data = pd.read_csv(self.file_path)
        return self.data

    def normalize_columns(self):
        """Normalize numeric columns to 0-1 range"""
        if self.data is None:
            raise ValueError("Data not loaded.")
        for col in self.data.select_dtypes(include=[np.number]).columns:
            min_val = self.data[col].min()
            max_val = self.data[col].max()
            self.data[col] = (self.data[col] - min_val) / (max_val - min_val)
        return self.data

    def summarize_data(self):
        """Generate summary statistics for numeric columns"""
        if self.data is None:
            raise ValueError("Data not loaded.")
        summary = self.data.describe()
        return summary

    def save_json(self, output_file):
        """Save DataFrame to JSON"""
        if self.data is None:
            raise ValueError("Data not loaded.")
        self.data.to_json(output_file, orient="records")

    def filter_rows(self, condition_func):
        """Filter rows based on a condition function"""
        if self.data is None:
            raise ValueError("Data not loaded.")
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

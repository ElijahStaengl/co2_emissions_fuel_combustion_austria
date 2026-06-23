
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_CSV = PROJECT_ROOT / "data" / "output_data"
INPUT_CSV = PROJECT_ROOT / "data" / "input_data" / "latest_updated_data"

def save_output_df_to_csv(df, name):
    df.to_csv(OUTPUT_CSV/f"{name}.csv", sep=";")

def save_input_df_to_csv(df, name):
    df.to_csv(INPUT_CSV/f"{name}.csv", sep=";")
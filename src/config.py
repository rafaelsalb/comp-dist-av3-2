from pathlib import Path



class Config:
    BASE_DIR = Path(__file__).resolve().parent
    EXAMPLES_DIR = BASE_DIR / "graph" / "examples"

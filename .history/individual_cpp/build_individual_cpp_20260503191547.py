from pathlib import Path
from individual_cpp_accelerated import build_cpp_backend

if __name__ == "__main__":
    out = build_cpp_backend(Path(__file__).resolve().parent)
    print(f"Backend construit: {out}")

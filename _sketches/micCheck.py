import subprocess
import sys

required_packages = [
    'dawdreamer', 'numpy', 'scipy', 'mido'
]

for package in required_packages:
    try:
        __import__(package)
        print(f"{package} is installed")
    except ImportError:
        print(f"{package} is not installed")
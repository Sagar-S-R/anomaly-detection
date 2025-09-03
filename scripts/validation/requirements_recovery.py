#!/usr/bin/env python3
"""
Requirements Recovery and Validation System
Handles missing packages that were removed during cleanup
"""

import subprocess
import sys
import os
from pathlib import Path

# Packages that might have been in requirements-missing.txt or requirements-dev.txt
DEVELOPMENT_PACKAGES = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0", 
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "jupyter>=1.0.0",
    "ipython>=8.0.0"
]

OPTIONAL_PACKAGES = [
    "tensorboard>=2.13.0",
    "wandb>=0.15.0", 
    "streamlit>=1.25.0",
    "gradio>=3.35.0",
    "plotly>=5.15.0",
    "seaborn>=0.12.0",
    "matplotlib>=3.7.0"
]

MISSING_PACKAGES_LIKELY = [
    "python-dateutil>=2.8.0",
    "six>=1.16.0",
    "wheel>=0.40.0",
    "packaging>=23.0"
]

def check_package_availability(package_name):
    """Check if a package is available on PyPI"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "index", "versions", package_name.split(">=")[0]
        ], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def install_missing_packages(packages, category_name):
    """Install missing packages from a category"""
    print(f"\n🔧 Checking {category_name} packages...")
    
    missing = []
    for package in packages:
        package_name = package.split(">=")[0]
        try:
            __import__(package_name.replace("-", "_"))
            print(f"   ✅ {package_name} (already available)")
        except ImportError:
            if check_package_availability(package_name):
                missing.append(package)
                print(f"   ⚠️  {package_name} (missing, available on PyPI)")
            else:
                print(f"   ❌ {package_name} (not available)")
    
    if missing:
        print(f"\n📦 Installing {len(missing)} missing {category_name} packages...")
        for package in missing:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True, text=True)
                print(f"   ✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to install {package}: {e}")
    else:
        print(f"   ✅ All {category_name} packages are satisfied")

def create_supplementary_requirements():
    """Create supplementary requirements files"""
    
    # Development requirements
    dev_req_path = Path("backend/requirements-dev.txt")
    with open(dev_req_path, "w") as f:
        f.write("# Development Dependencies\n")
        f.write("# Install with: pip install -r requirements-dev.txt\n\n")
        for package in DEVELOPMENT_PACKAGES:
            f.write(f"{package}\n")
    print(f"📄 Created {dev_req_path}")
    
    # Optional requirements  
    opt_req_path = Path("backend/requirements-optional.txt")
    with open(opt_req_path, "w") as f:
        f.write("# Optional Dependencies\n")
        f.write("# Install with: pip install -r requirements-optional.txt\n\n")
        for package in OPTIONAL_PACKAGES:
            f.write(f"{package}\n")
    print(f"📄 Created {opt_req_path}")
    
    # Missing packages (likely needed)
    missing_req_path = Path("backend/requirements-missing.txt")
    with open(missing_req_path, "w") as f:
        f.write("# Likely Missing Dependencies\n")
        f.write("# These packages are commonly needed but might be missing\n\n")
        for package in MISSING_PACKAGES_LIKELY:
            f.write(f"{package}\n")
    print(f"📄 Created {missing_req_path}")

def validate_current_requirements():
    """Validate that current requirements.txt is sufficient"""
    print("🔍 Validating current requirements.txt...")
    
    req_file = Path("backend/requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    with open(req_file) as f:
        content = f.read()
    
    # Count packages
    packages = [line for line in content.split('\n') 
               if line.strip() and not line.startswith('#') and '>=' in line]
    
    print(f"📦 Found {len(packages)} packages in requirements.txt")
    
    # Check for critical packages
    critical_packages = ['fastapi', 'torch', 'transformers', 'opencv-python', 'mediapipe']
    missing_critical = []
    
    for package in critical_packages:
        if package not in content.lower():
            missing_critical.append(package)
    
    if missing_critical:
        print(f"❌ Missing critical packages: {missing_critical}")
        return False
    else:
        print("✅ All critical packages present")
        return True

def main():
    print("🔧 Requirements Recovery and Validation System")
    print("=" * 50)
    
    # Validate current setup
    if not validate_current_requirements():
        print("\n❌ Current requirements.txt is insufficient!")
        return 1
    
    # Create supplementary files
    print("\n📄 Creating supplementary requirements files...")
    create_supplementary_requirements()
    
    # Check for missing packages
    install_missing_packages(MISSING_PACKAGES_LIKELY, "likely missing")
    install_missing_packages(DEVELOPMENT_PACKAGES, "development")
    
    print("\n✅ Requirements recovery complete!")
    print("\n📋 Available requirements files:")
    for req_file in Path("backend").glob("requirements*.txt"):
        size = req_file.stat().st_size
        print(f"   📄 {req_file.name} ({size} bytes)")
    
    print("\n🚀 Usage:")
    print("   pip install -r backend/requirements.txt           # Main dependencies")
    print("   pip install -r backend/requirements-dev.txt       # Development tools") 
    print("   pip install -r backend/requirements-optional.txt  # Optional features")
    print("   pip install -r backend/requirements-missing.txt   # Likely missing packages")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Requirements Validator and Missing Package Handler
Validates requirements.txt and handles missing dependencies during Docker build
"""

import subprocess
import sys
import os
import json
from pathlib import Path
import importlib.util

class RequirementsValidator:
    def __init__(self):
        self.missing_packages = []
        self.failed_imports = []
        self.alternative_packages = {
            'cv2': ['opencv-python', 'opencv-contrib-python', 'opencv-python-headless'],
            'sklearn': ['scikit-learn'],
            'PIL': ['Pillow', 'PIL'],
            'speech_recognition': ['SpeechRecognition'],
            'dotenv': ['python-dotenv'],
            'yaml': ['PyYAML', 'ruamel.yaml'],
            'whisper': ['openai-whisper'],
            'groq': ['groq'],
        }
        
    def check_package_installed(self, package_name):
        """Check if a package is installed"""
        try:
            result = subprocess.run([
                sys.executable, '-c', f'import {package_name}'
            ], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def install_package(self, package_name):
        """Install a package using pip"""
        try:
            print(f"📦 Installing {package_name}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully installed {package_name}")
                return True
            else:
                print(f"❌ Failed to install {package_name}: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error installing {package_name}: {e}")
            return False
    
    def try_alternatives(self, import_name):
        """Try alternative package names for an import"""
        if import_name in self.alternative_packages:
            for alt_package in self.alternative_packages[import_name]:
                print(f"🔄 Trying alternative: {alt_package}")
                if self.install_package(alt_package):
                    if self.check_package_installed(import_name):
                        return True
        return False
    
    def validate_critical_imports(self):
        """Validate critical imports for the anomaly detection system"""
        critical_imports = {
            'fastapi': 'FastAPI web framework',
            'uvicorn': 'ASGI server',
            'cv2': 'OpenCV for computer vision',
            'mediapipe': 'MediaPipe for pose detection',
            'transformers': 'Hugging Face Transformers',
            'torch': 'PyTorch',
            'whisper': 'OpenAI Whisper for speech recognition',
            'groq': 'Groq API client',
            'PIL': 'Python Imaging Library',
            'numpy': 'NumPy for numerical computing',
            'pymongo': 'MongoDB driver',
        }
        
        print("🔍 Validating critical imports...")
        
        all_good = True
        for import_name, description in critical_imports.items():
            print(f"Checking {import_name} ({description})...")
            
            if self.check_package_installed(import_name):
                print(f"✅ {import_name} is available")
            else:
                print(f"❌ {import_name} is missing")
                
                # Try to install alternatives
                if self.try_alternatives(import_name):
                    print(f"✅ {import_name} resolved with alternative")
                else:
                    self.missing_packages.append(import_name)
                    all_good = False
        
        return all_good
    
    def create_fallback_requirements(self):
        """Create a comprehensive fallback requirements.txt"""
        fallback_requirements = [
            "# Comprehensive requirements.txt - Auto-generated fallback",
            "# Web Framework",
            "fastapi>=0.110.0",
            "uvicorn[standard]>=0.30.0",
            "python-multipart>=0.0.6",
            "websockets>=11.0",
            "",
            "# AI and ML Core",
            "torch>=2.0.0",
            "transformers>=4.40.0",
            "numpy>=1.24.0",
            "",
            "# Computer Vision",
            "opencv-python>=4.8.0",
            "mediapipe>=0.10.0",
            "Pillow>=10.0.0",
            "",
            "# Audio Processing", 
            "openai-whisper>=20231117",
            "moviepy>=1.0.3",
            "pydub>=0.25.1",
            "pyaudio>=0.2.11",
            "",
            "# AI APIs",
            "groq>=0.30.0",
            "",
            "# Database",
            "motor>=3.3.0",
            "pymongo>=4.6.0",
            "",
            "# Utilities",
            "python-dotenv>=1.0.0",
            "requests>=2.31.0",
            "",
            "# Development (optional)",
            "pytest>=7.0.0",
            "black>=23.0.0",
        ]
        
        req_path = Path("requirements.txt")
        with open(req_path, 'w') as f:
            f.write('\n'.join(fallback_requirements))
        
        print(f"📝 Created fallback requirements.txt with {len([r for r in fallback_requirements if r and not r.startswith('#')])} packages")
    
    def install_from_requirements(self, requirements_file="requirements.txt"):
        """Install packages from requirements file with error handling"""
        if not Path(requirements_file).exists():
            print(f"⚠️  {requirements_file} not found, creating fallback...")
            self.create_fallback_requirements()
        
        print(f"📦 Installing packages from {requirements_file}...")
        
        # Read requirements
        with open(requirements_file, 'r') as f:
            requirements = f.readlines()
        
        failed_packages = []
        successful_packages = []
        
        for req in requirements:
            req = req.strip()
            if not req or req.startswith('#'):
                continue
            
            # Extract package name (handle version specifiers)
            package_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0]
            
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', req
                ], capture_output=True, text=True, timeout=300)  # 5 minute timeout per package
                
                if result.returncode == 0:
                    successful_packages.append(req)
                    print(f"✅ {req}")
                else:
                    failed_packages.append(req)
                    print(f"❌ {req}: {result.stderr.strip()}")
                    
            except subprocess.TimeoutExpired:
                failed_packages.append(req)
                print(f"⏱️  {req}: Installation timeout")
            except Exception as e:
                failed_packages.append(req)
                print(f"❌ {req}: {e}")
        
        print(f"\n📊 Installation Summary:")
        print(f"   ✅ Successful: {len(successful_packages)}")
        print(f"   ❌ Failed: {len(failed_packages)}")
        
        if failed_packages:
            print(f"\n❌ Failed packages:")
            for pkg in failed_packages:
                print(f"   - {pkg}")
            
            # Try alternatives for failed packages
            print(f"\n🔄 Trying alternatives for failed packages...")
            for pkg in failed_packages[:]:  # Copy list
                base_name = pkg.split('==')[0].split('>=')[0]
                if base_name in self.alternative_packages:
                    for alt in self.alternative_packages[base_name]:
                        if self.install_package(alt):
                            failed_packages.remove(pkg)
                            successful_packages.append(alt)
                            break
        
        return len(failed_packages) == 0

def main():
    """Main validation function"""
    print("🔍 Requirements Validator and Missing Package Handler")
    print("=" * 55)
    
    validator = RequirementsValidator()
    
    # Step 1: Install from requirements.txt
    success = validator.install_from_requirements()
    
    # Step 2: Validate critical imports
    imports_ok = validator.validate_critical_imports()
    
    # Step 3: Final report
    if success and imports_ok:
        print("\n🎉 All requirements validated successfully!")
        print("✅ System ready for model pre-loading")
        return True
    else:
        print("\n⚠️  Some packages are missing or failed to install")
        if validator.missing_packages:
            print("❌ Missing critical packages:")
            for pkg in validator.missing_packages:
                print(f"   - {pkg}")
        
        print("\n💡 Suggestions:")
        print("   1. Check your internet connection")
        print("   2. Update pip: pip install --upgrade pip")
        print("   3. Try installing packages individually")
        print("   4. Check system dependencies (gcc, python-dev, etc.)")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

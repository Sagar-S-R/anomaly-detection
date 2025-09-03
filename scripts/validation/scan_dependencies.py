#!/usr/bin/env python3
"""
Comprehensive Dependency Scanner and Requirements Generator
Automatically scans the codebase and generates complete requirements.txt
"""

import os
import sys
import ast
import subprocess
import pkg_resources
from pathlib import Path
import importlib
import json
from collections import defaultdict

class DependencyScanner:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.imports = set()
        self.stdlib_modules = self._get_stdlib_modules()
        self.package_mapping = {
            'cv2': 'opencv-python',
            'sklearn': 'scikit-learn',
            'PIL': 'Pillow',
            'yaml': 'PyYAML',
            'dotenv': 'python-dotenv',
            'speech_recognition': 'SpeechRecognition',
            'pyaudio': 'PyAudio',
            'whisper': 'openai-whisper',
        }
        
    def _get_stdlib_modules(self):
        """Get list of standard library modules"""
        try:
            import sys
            stdlib = set()
            for name in sys.stdlib_module_names:
                stdlib.add(name)
            # Add some common stdlib modules that might be missing
            stdlib.update([
                'os', 'sys', 'json', 'time', 'datetime', 'pathlib',
                'collections', 'threading', 'multiprocessing', 'asyncio',
                'urllib', 'http', 'email', 'xml', 'html', 'logging',
                'unittest', 'typing', 'functools', 'itertools', 'math',
                'random', 're', 'string', 'io', 'tempfile', 'shutil',
                'subprocess', 'traceback', 'warnings'
            ])
            return stdlib
        except AttributeError:
            # Fallback for older Python versions
            return {
                'os', 'sys', 'json', 'time', 'datetime', 'pathlib',
                'collections', 'threading', 'multiprocessing', 'asyncio',
                'urllib', 'http', 'email', 'xml', 'html', 'logging',
                'unittest', 'typing', 'functools', 'itertools', 'math',
                'random', 're', 'string', 'io', 'tempfile', 'shutil',
                'subprocess', 'traceback', 'warnings'
            }

    def scan_file(self, file_path):
        """Scan a Python file for imports"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports.add(node.module.split('.')[0])

    def scan_directory(self):
        """Scan all Python files in the project"""
        print(f"🔍 Scanning {self.project_root} for imports...")
        
        python_files = list(self.project_root.rglob('*.py'))
        print(f"📁 Found {len(python_files)} Python files")
        
        for file_path in python_files:
            # Skip virtual environment and cache directories
            if any(part in file_path.parts for part in ['venv', '__pycache__', '.git', 'node_modules']):
                continue
            self.scan_file(file_path)
        
        print(f"📦 Found {len(self.imports)} unique imports")

    def filter_third_party_imports(self):
        """Filter out standard library modules"""
        third_party = set()
        
        for imp in self.imports:
            if imp not in self.stdlib_modules:
                # Map known package names
                package_name = self.package_mapping.get(imp, imp)
                third_party.add(package_name)
        
        return third_party

    def get_installed_packages(self):
        """Get currently installed packages with versions"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], 
                                  capture_output=True, text=True)
            installed = {}
            for line in result.stdout.strip().split('\n'):
                if '==' in line:
                    name, version = line.split('==', 1)
                    installed[name.lower()] = version
            return installed
        except Exception as e:
            print(f"⚠️  Error getting installed packages: {e}")
            return {}

    def validate_package(self, package_name):
        """Validate if a package exists on PyPI"""
        try:
            # Try to import the package
            importlib.import_module(package_name)
            return True, "installed"
        except ImportError:
            try:
                # Check if it's available on PyPI
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'search', package_name],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return True, "available"
                else:
                    return False, "not_found"
            except:
                return False, "unknown"

    def generate_requirements(self):
        """Generate comprehensive requirements.txt"""
        print("\n🔧 Analyzing dependencies...")
        
        third_party_imports = self.filter_third_party_imports()
        installed_packages = self.get_installed_packages()
        
        requirements = []
        missing_packages = []
        suggested_packages = []
        
        # Check each third-party import
        for package in sorted(third_party_imports):
            package_lower = package.lower()
            
            if package_lower in installed_packages:
                version = installed_packages[package_lower]
                requirements.append(f"{package}=={version}")
                print(f"✅ {package}=={version}")
            else:
                is_valid, status = self.validate_package(package)
                if is_valid:
                    if status == "available":
                        suggested_packages.append(package)
                        print(f"📦 {package} (available, not installed)")
                    else:
                        requirements.append(package)
                        print(f"✅ {package} (installed, no version)")
                else:
                    missing_packages.append(package)
                    print(f"❌ {package} (not found)")
        
        return requirements, missing_packages, suggested_packages

    def create_requirements_files(self, requirements, missing_packages, suggested_packages):
        """Create comprehensive requirements files"""
        
        # Main requirements.txt
        req_file = self.project_root / 'backend' / 'requirements.txt'
        req_file.parent.mkdir(exist_ok=True)
        
        with open(req_file, 'w') as f:
            f.write("# Auto-generated requirements.txt\n")
            f.write("# Core dependencies for Anomaly Detection System\n\n")
            f.write("# FastAPI and Web Framework\n")
            f.write("fastapi==0.112.0\n")
            f.write("uvicorn==0.30.3\n")
            f.write("python-multipart==0.0.6\n")
            f.write("websockets\n\n")
            
            f.write("# AI and ML Libraries\n")
            f.write("torch==2.4.0\n")
            f.write("transformers==4.44.0\n")
            f.write("openai-whisper==20231117\n")
            f.write("groq==0.31.0\n")
            f.write("mediapipe==0.10.14\n\n")
            
            f.write("# Computer Vision\n")
            f.write("opencv-python==4.10.0.84\n")
            f.write("Pillow==10.4.0\n\n")
            
            f.write("# Audio Processing\n")
            f.write("moviepy==1.0.3\n")
            f.write("pydub==0.25.1\n")
            f.write("pyaudio==0.2.14\n\n")
            
            f.write("# Database and Storage\n")
            f.write("motor==3.3.2\n")
            f.write("pymongo==4.6.1\n\n")
            
            f.write("# Utilities\n")
            f.write("numpy==2.0.1\n")
            f.write("python-dotenv==1.0.1\n\n")
            
            f.write("# Detected dependencies\n")
            for req in sorted(requirements):
                f.write(f"{req}\n")
        
        # Missing packages file
        if missing_packages:
            missing_file = self.project_root / 'backend' / 'requirements-missing.txt'
            with open(missing_file, 'w') as f:
                f.write("# Missing packages that couldn't be resolved\n")
                f.write("# Please review and add manually if needed\n\n")
                for pkg in sorted(missing_packages):
                    f.write(f"# {pkg}  # Could not resolve - check package name\n")
        
        # Development requirements
        dev_req_file = self.project_root / 'backend' / 'requirements-dev.txt'
        with open(dev_req_file, 'w') as f:
            f.write("# Development dependencies\n")
            f.write("-r requirements.txt\n\n")
            f.write("# Testing\n")
            f.write("pytest\n")
            f.write("pytest-asyncio\n")
            f.write("pytest-cov\n\n")
            f.write("# Development tools\n")
            f.write("black\n")
            f.write("flake8\n")
            f.write("mypy\n")
            f.write("jupyter\n")

def main():
    """Main function"""
    project_root = Path(__file__).parent
    
    print("🔍 Comprehensive Dependency Scanner")
    print("=" * 40)
    
    scanner = DependencyScanner(project_root)
    scanner.scan_directory()
    
    requirements, missing_packages, suggested_packages = scanner.generate_requirements()
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Resolved packages: {len(requirements)}")
    print(f"   ❌ Missing packages: {len(missing_packages)}")
    print(f"   📦 Suggested packages: {len(suggested_packages)}")
    
    scanner.create_requirements_files(requirements, missing_packages, suggested_packages)
    
    print(f"\n📝 Files generated:")
    print(f"   📄 backend/requirements.txt (main dependencies)")
    print(f"   🔧 backend/requirements-dev.txt (development)")
    
    if missing_packages:
        print(f"   ⚠️  backend/requirements-missing.txt (needs review)")
        print(f"\n⚠️  Please review missing packages:")
        for pkg in missing_packages:
            print(f"      - {pkg}")
    
    if suggested_packages:
        print(f"\n💡 Consider installing these packages:")
        for pkg in suggested_packages:
            print(f"      - {pkg}")

if __name__ == "__main__":
    main()

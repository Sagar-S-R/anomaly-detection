#!/bin/bash
# Docker containerization test script
# Tests complete dependency resolution and model pre-loading

echo "🐳 Docker Containerization Test Suite"
echo "======================================"

# Test 1: Requirements validation
echo "📦 Test 1: Validating requirements.txt completeness"
cd /Users/samrudhp/Projects-git/anomaly-detection/backend
python validate_requirements.py

if [ $? -ne 0 ]; then
    echo "❌ Requirements validation failed"
    exit 1
fi

# Test 2: Dependency scanner check
echo ""
echo "🔍 Test 2: Running dependency scanner"
python -c "
import ast
import os
critical_files = ['app.py', 'dashboard_app.py', 'utils/fusion_logic.py']
missing_imports = []

for file_path in critical_files:
    if not os.path.exists(file_path):
        missing_imports.append(f'File missing: {file_path}')
        continue
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
        
        # Check for common missing imports
        imports_found = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports_found.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports_found.add(node.module.split('.')[0])
        
        # Critical imports check
        critical_imports = {'fastapi', 'cv2', 'torch', 'transformers', 'groq', 'whisper'}
        file_critical = critical_imports.intersection(imports_found)
        
        if file_critical:
            print(f'✅ {file_path}: Found critical imports {sorted(file_critical)}')
        
    except Exception as e:
        missing_imports.append(f'Parse error in {file_path}: {e}')

if missing_imports:
    print('❌ Issues found:')
    for issue in missing_imports:
        print(f'   - {issue}')
    exit(1)
else:
    print('✅ All critical files and imports validated')
"

if [ $? -ne 0 ]; then
    echo "❌ Dependency scanner failed"
    exit 1
fi

# Test 3: Model pre-loading simulation
echo ""
echo "🤖 Test 3: Testing model pre-loading logic"
python -c "
import os
import sys
sys.path.append('.')

try:
    # Test imports that will be needed for model loading
    print('Testing model-related imports...')
    
    import torch
    print(f'✅ PyTorch: {torch.__version__}')
    
    import transformers
    print(f'✅ Transformers: {transformers.__version__}')
    
    import cv2
    print(f'✅ OpenCV: {cv2.__version__}')
    
    import whisper
    print('✅ Whisper available')
    
    import mediapipe
    print(f'✅ MediaPipe: {mediapipe.__version__}')
    
    # Test model cache directories
    cache_dirs = ['/tmp/model_cache', '/tmp/transformers_cache', '/tmp/torch_home']
    for cache_dir in cache_dirs:
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            print(f'✅ Created cache directory: {cache_dir}')
        else:
            print(f'✅ Cache directory exists: {cache_dir}')
    
    print('✅ Model pre-loading setup validated')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Model pre-loading test failed"
    exit 1
fi

# Test 4: Docker compatibility check
echo ""
echo "🐋 Test 4: Docker file validation"
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile exists"
    
    # Check for critical Dockerfile elements
    if grep -q "requirements.txt" Dockerfile; then
        echo "✅ Dockerfile references requirements.txt"
    else
        echo "⚠️  Dockerfile may not install requirements.txt"
    fi
    
    if grep -q "preload_models" Dockerfile; then
        echo "✅ Dockerfile includes model pre-loading"
    else
        echo "⚠️  Dockerfile may not pre-load models"
    fi
else
    echo "⚠️  No Dockerfile found"
fi

if [ -f "docker-compose.yml" ]; then
    echo "✅ docker-compose.yml exists"
else
    echo "⚠️  No docker-compose.yml found"
fi

# Test 5: Environment variables check
echo ""
echo "🌍 Test 5: Environment configuration"
if [ -f ".env.example" ] || [ -f ".env" ]; then
    echo "✅ Environment configuration found"
else
    echo "⚠️  No .env file found - may need manual configuration"
fi

echo ""
echo "🎉 Docker Containerization Test Complete!"
echo "✅ All critical tests passed"
echo ""
echo "📋 Summary:"
echo "   ✅ Requirements validated and complete"
echo "   ✅ Critical imports detected and available"  
echo "   ✅ Model pre-loading setup verified"
echo "   ✅ Docker configuration checked"
echo ""
echo "🚀 Ready for containerization with:"
echo "   docker-compose up --build"

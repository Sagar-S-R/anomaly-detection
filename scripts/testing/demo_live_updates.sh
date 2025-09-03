#!/bin/bash
# Live Code Update Demo Script
# Demonstrates how code changes work in containerized development

echo "🔄 Live Code Update Demonstration"
echo "================================"

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "📦 Starting containers first..."
    docker-compose up -d
    echo "⏳ Waiting for services to be ready..."
    sleep 30
fi

echo ""
echo "🧪 Test 1: Check current container status"
docker-compose ps

echo ""
echo "🧪 Test 2: Test current API response"
echo "Testing backend health endpoint..."
curl -s http://localhost:8000/health || echo "Backend not ready yet"

echo ""
echo "🧪 Test 3: Demonstrate live code update"
echo "Creating a test endpoint to show live updates..."

# Create a temporary test endpoint
cat >> app.py << 'EOF'

# TEMPORARY TEST ENDPOINT - WILL BE REMOVED
@app.get("/test-live-update")
async def test_live_update():
    """Test endpoint to demonstrate live code updates"""
    return {
        "message": "🔥 LIVE UPDATE WORKS!",
        "timestamp": datetime.now().isoformat(),
        "update_count": 1
    }
EOF

echo "✅ Added test endpoint to app.py"
echo "⏳ Waiting 3 seconds for auto-reload..."
sleep 3

echo ""
echo "🧪 Test 4: Check if new endpoint is available (should work without rebuild!)"
response=$(curl -s http://localhost:8000/test-live-update 2>/dev/null)
if [[ $response == *"LIVE UPDATE WORKS"* ]]; then
    echo "🎉 SUCCESS: Live code update works!"
    echo "📝 Response: $response"
else
    echo "⚠️  Endpoint not ready yet, checking container logs..."
    docker-compose logs --tail=10 backend
fi

echo ""
echo "🧪 Test 5: Update the endpoint again (modify existing code)"
# Update the test endpoint
sed -i.bak 's/update_count": 1/update_count": 2/' app.py
sed -i.bak 's/LIVE UPDATE WORKS!/LIVE UPDATE WORKS - UPDATED!/' app.py

echo "✅ Updated test endpoint"
echo "⏳ Waiting 3 seconds for auto-reload..."
sleep 3

# Test updated endpoint
echo ""
echo "🧪 Test 6: Check updated endpoint"
updated_response=$(curl -s http://localhost:8000/test-live-update 2>/dev/null)
if [[ $updated_response == *"UPDATED"* ]] && [[ $updated_response == *"update_count\": 2"* ]]; then
    echo "🎉 SUCCESS: Live code updates work perfectly!"
    echo "📝 Updated Response: $updated_response"
else
    echo "⚠️  Update not reflected yet"
    echo "📝 Current Response: $updated_response"
fi

echo ""
echo "🧪 Test 7: Show container logs (should show reload messages)"
echo "Recent backend logs:"
docker-compose logs --tail=15 backend

echo ""
echo "🧪 Test 8: Clean up test endpoint"
# Remove the test endpoint
head -n -7 app.py > app.py.tmp && mv app.py.tmp app.py
rm -f app.py.bak
echo "✅ Removed test endpoint"

echo ""
echo "📊 SUMMARY: How Updates Work"
echo "=========================="
echo "✅ Python code changes: INSTANT (auto-reload)"
echo "✅ No rebuild needed for .py files"
echo "✅ Volume mapping syncs local files to container" 
echo "⚠️  New packages: Requires rebuild"
echo "⚠️  Docker config: Requires rebuild"
echo ""
echo "🚀 Development Workflow:"
echo "1. docker-compose up -d  # Start once"
echo "2. Edit code normally    # Changes auto-apply"  
echo "3. Test at http://localhost:8000"
echo "4. Only rebuild for new packages"

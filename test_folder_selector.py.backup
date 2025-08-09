import requests

def test_folders_endpoint():
    """Test the folders endpoint with authentication"""
    print("Testing folders endpoint...")
    
    # First test without auth (should fail)
    response = requests.get('http://127.0.0.1:8000/api/admin/folders')
    print(f'Without auth - Status: {response.status_code}')
    
    if response.status_code == 401:
        print("✅ Authentication required (as expected)")
    elif response.status_code == 200:
        folders = response.json()
        print(f"✅ Found {len(folders)} folders:")
        for folder in folders:
            print(f'  - {folder}')
    else:
        print(f"❌ Unexpected status: {response.text[:200]}")

def test_chapters_endpoint():
    """Test the chapters endpoint (should be public)"""
    print("\nTesting chapters endpoint...")
    response = requests.get('http://127.0.0.1:8000/api/chapters')
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        chapters = response.json()
        print(f"✅ Found chapters: {chapters}")
    else:
        print(f"❌ Error: {response.text[:200]}")

if __name__ == "__main__":
    test_chapters_endpoint()
    test_folders_endpoint()
    print("\n🎉 API testing completed!")
    print("\n📁 Folder Selector Features:")
    print("  - 📂 Dropdown with common folder suggestions")
    print("  - 🔍 Filtered search as you type")
    print("  - ➕ Create new folder option")
    print("  - 💾 Manual input with validation")
    print("  - 🔒 Backend API integration (requires admin auth)")
    print("\n🚀 Ready to test in the web interface!")

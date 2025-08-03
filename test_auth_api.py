from database import SessionLocal
from models import User
import requests

# Create a test user
db = SessionLocal()
try:
    # Check if we have any admin users
    admin_user = db.query(User).filter(User.role == 'admin').first()
    if not admin_user:
        # Create a test admin user
        admin_user = User(
            email='admin@test.com',
            name='Test Admin',
            google_id='test123',
            role='admin'
        )
        db.add(admin_user)
        db.commit()
        print('Created test admin user')
    
    print(f'Using test user: {admin_user.email} (Role: {admin_user.role})')
    
finally:
    db.close()

# Test API endpoints
print('\nTesting chapters endpoint:')
response = requests.get('http://127.0.0.1:8000/api/chapters')
print(f'Chapters API Status: {response.status_code}')
if response.status_code == 200:
    chapters = response.json()
    print(f'Available chapters: {chapters}')

# Test question endpoint without auth - this might require auth
print('\nTesting question endpoint without auth:')
url = 'http://127.0.0.1:8000/api/ask?chapter=chapter1'
data = {'question': 'What is machine learning?'}
response = requests.post(url, json=data)
print(f'Question API Status: {response.status_code}')
if response.status_code == 200:
    answer = response.json()
    print(f'Answer: {answer["answer"][:300]}...')
else:
    print(f'Error: {response.text[:200]}...')

import requests
import json

# Test the chapter-based API
url = 'http://127.0.0.1:8000/api/chapters'
try:
    response = requests.get(url)
    if response.status_code == 200:
        chapters = response.json()
        print('Available chapters:')
        for chapter in chapters:
            print(f'  - {chapter}')
        
        # Test asking a question about machine learning
        if 'chapter1' in chapters:
            print('\nTesting question about chapter1 (Machine Learning):')
            question_url = 'http://127.0.0.1:8000/api/ask?chapter=chapter1'
            question_data = {'question': 'What is machine learning?'}
            response = requests.post(question_url, json=question_data)
            if response.status_code == 200:
                answer = response.json()
                print(f'Question: {question_data["question"]}')
                print(f'Answer: {answer["answer"][:200]}...')
            else:
                print(f'Error asking question: {response.status_code}')
    else:
        print(f'Error getting chapters: {response.status_code}')
except Exception as e:
    print(f'Error: {e}')

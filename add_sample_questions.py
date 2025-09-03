#!/usr/bin/env python3
"""
Script to add sample questions to the survey database
"""

import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'survey_app'
}

def add_sample_questions():
    """Add sample questions to the database"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Sample questions data
        questions = [
            {
                'title': 'How did you hear about our service?',
                'question_type': 'multiple_choice',
                'is_required': True,
                'order_index': 1,
                'options': ['Social Media', 'Friend/Family', 'Advertisement', 'Search Engine', 'Other']
            },
            {
                'title': 'How satisfied are you with our service?',
                'question_type': 'rating',
                'is_required': True,
                'order_index': 2,
                'options': []
            },
            {
                'title': 'Would you recommend us to others?',
                'question_type': 'yes_no',
                'is_required': True,
                'order_index': 3,
                'options': []
            },
            {
                'title': 'What suggestions do you have for improvement?',
                'question_type': 'essay',
                'is_required': False,
                'order_index': 4,
                'options': []
            },
            {
                'title': 'Which age group do you belong to?',
                'question_type': 'dropdown',
                'is_required': True,
                'order_index': 5,
                'options': ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
            }
        ]
        
        for question_data in questions:
            # Insert question
            cursor.execute("""
            INSERT INTO questions (title, question_type, is_required, order_index)
            VALUES (%s, %s, %s, %s)
            """, (question_data['title'], question_data['question_type'], 
                  question_data['is_required'], question_data['order_index']))
            
            question_id = cursor.lastrowid
            
            # Insert options for multiple choice and dropdown questions
            if question_data['question_type'] in ['multiple_choice', 'dropdown']:
                for i, option_text in enumerate(question_data['options']):
                    cursor.execute("""
                    INSERT INTO options (question_id, text, order_index)
                    VALUES (%s, %s, %s)
                    """, (question_id, option_text, i))
        
        conn.commit()
        print("✅ Sample questions added successfully!")
        print(f"Added {len(questions)} questions to the database.")
        
    except mysql.connector.Error as err:
        print(f"❌ Error adding sample questions: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_sample_questions()

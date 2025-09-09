from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import mysql.connector
from datetime import datetime
import uuid
import json
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database configuration
DB_CONFIG = {
    'host': 'mysql.railway.internal',
    'user': 'root',
    'password': 'jWkKqGzliifXGJuYsskPgrtJLldzcKXD',
    'database': 'railway',
    'port': 3306
}

# Mail configuration for SendGrid

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv("GMAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("GMAIL_APP_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("GMAIL_USERNAME")





mail = Mail(app)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Create questions table with enhanced structure
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            question_type ENUM('multiple_choice', 'essay', 'rating', 'yes_no', 'dropdown') NOT NULL,
            is_required BOOLEAN DEFAULT TRUE,
            order_index INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        
        # Create options table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS options (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question_id INT,
            text VARCHAR(500) NOT NULL,
            order_index INT DEFAULT 0,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        )
        """)
        
        # Create answers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question_id INT,
            option_id INT NULL,
            text_answer TEXT NULL,
            respondent_id VARCHAR(36),
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
            FOREIGN KEY (option_id) REFERENCES options(id) ON DELETE CASCADE
        )
        """)
        
        # Create question branching table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_branching (
            id INT AUTO_INCREMENT PRIMARY KEY,
            from_question_id INT,
            from_option_id INT,
            to_question_id INT,
            FOREIGN KEY (from_question_id) REFERENCES questions(id) ON DELETE CASCADE,
            FOREIGN KEY (from_option_id) REFERENCES options(id) ON DELETE CASCADE,
            FOREIGN KEY (to_question_id) REFERENCES questions(id) ON DELETE CASCADE
        )
        """)
        
        conn.commit()
        return True
        
    except mysql.connector.Error as err:
        print(f"Database initialization error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# Initialize database on startup
init_database()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    return render_template('admin/dashboard.html')

@app.route('/admin/questions')
def questions_management():
    """Questions management page"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('admin/questions.html', questions=[])
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all questions
        cursor.execute("""
        SELECT * FROM questions 
        ORDER BY order_index, id
        """)
        questions = cursor.fetchall()
        
        # Get counts for each question
        for question in questions:
            # Count options
            cursor.execute("SELECT COUNT(*) as count FROM options WHERE question_id = %s", (question['id'],))
            question['options_count'] = cursor.fetchone()['count']
            
            # Count responses
            cursor.execute("SELECT COUNT(*) as count FROM answers WHERE question_id = %s", (question['id'],))
            question['responses_count'] = cursor.fetchone()['count']
        
        return render_template('admin/questions.html', questions=questions)
        
    except mysql.connector.Error as err:
        flash(f'Database error: {err}', 'error')
        return render_template('admin/questions.html', questions=[])
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/questions/new', methods=['GET', 'POST'])
def new_question():
    """Create new question"""
    if request.method == 'POST':
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = conn.cursor()
        
        try:
            # Insert question
            cursor.execute("""
            INSERT INTO questions (title, question_type, is_required, order_index)
            VALUES (%s, %s, %s, %s)
            """, (data['title'], data['question_type'], data.get('is_required', True), data.get('order_index', 0)))
            
            question_id = cursor.lastrowid
            
            # Insert options if it's a multiple choice question
            if data['question_type'] in ['multiple_choice', 'dropdown'] and 'options' in data:
                for i, option_text in enumerate(data['options']):
                    if option_text.strip():
                        cursor.execute("""
                        INSERT INTO options (question_id, text, order_index)
                        VALUES (%s, %s, %s)
                        """, (question_id, option_text.strip(), i))
            
            conn.commit()
            return jsonify({'success': True, 'question_id': question_id})
            
        except mysql.connector.Error as err:
            conn.rollback()
            return jsonify({'success': False, 'message': f'Database error: {err}'})
        finally:
            cursor.close()
            conn.close()
    
    return render_template('admin/new_question.html')

@app.route('/admin/questions/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    """Edit question"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('questions_management'))
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        data = request.get_json()
        
        try:
            # Update question
            cursor.execute("""
            UPDATE questions 
            SET title = %s, question_type = %s, is_required = %s, order_index = %s
            WHERE id = %s
            """, (data['title'], data['question_type'], data.get('is_required', True), 
                  data.get('order_index', 0), question_id))
            
            # Update options for multiple choice questions
            if data['question_type'] in ['multiple_choice', 'dropdown']:
                # Delete existing options
                cursor.execute("DELETE FROM options WHERE question_id = %s", (question_id,))
                
                # Insert new options
                if 'options' in data:
                    for i, option_text in enumerate(data['options']):
                        if option_text.strip():
                            cursor.execute("""
                            INSERT INTO options (question_id, text, order_index)
                            VALUES (%s, %s, %s)
                            """, (question_id, option_text.strip(), i))
            
            conn.commit()
            return jsonify({'success': True})
            
        except mysql.connector.Error as err:
            conn.rollback()
            return jsonify({'success': False, 'message': f'Database error: {err}'})
        finally:
            cursor.close()
            conn.close()
    
    try:
        # Get question details
        cursor.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
        question = cursor.fetchone()
        
        if not question:
            flash('Question not found', 'error')
            return redirect(url_for('questions_management'))
        
        # Get options
        cursor.execute("SELECT * FROM options WHERE question_id = %s ORDER BY order_index", (question_id,))
        options = cursor.fetchall()
        
        return render_template('admin/edit_question.html', question=question, options=options)
        
    except mysql.connector.Error as err:
        flash(f'Database error: {err}', 'error')
        return redirect(url_for('questions_management'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/questions/<int:question_id>/update', methods=['POST'])
def update_question(question_id):
    """Update question"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('questions_management'))
    
    cursor = conn.cursor()
    
    try:
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description', '')
        question_type = request.form.get('question_type')
        is_required = 'required' in request.form
        order_index = int(request.form.get('order_index', 1))
        
        # Update question
        cursor.execute("""
        UPDATE questions 
        SET title = %s, question_type = %s, is_required = %s, order_index = %s, updated_at = NOW()
        WHERE id = %s
        """, (title, question_type, is_required, order_index, question_id))
        
        # Handle options for multiple choice and dropdown questions
        if question_type in ['multiple_choice', 'dropdown']:
            option_texts = request.form.getlist('option_text[]')
            option_ids = request.form.getlist('option_id[]')
            option_orders = request.form.getlist('option_order[]')
            
            # Update existing options and add new ones
            for i, (option_text, option_id, option_order) in enumerate(zip(option_texts, option_ids, option_orders)):
                if option_text.strip():  # Only process non-empty options
                    if option_id.startswith('new_'):
                        # Add new option
                        cursor.execute("""
                        INSERT INTO options (question_id, text, order_index, updated_at)
                        VALUES (%s, %s, %s, NOW())
                        """, (question_id, option_text.strip(), int(option_order) if option_order else i + 1))
                    else:
                        # Update existing option
                        cursor.execute("""
                        UPDATE options 
                        SET text = %s, order_index = %s, updated_at = NOW()
                        WHERE id = %s AND question_id = %s
                        """, (option_text.strip(), int(option_order) if option_order else i + 1, option_id, question_id))
            
            # Remove options that are no longer in the form
            existing_option_ids = [oid for oid in option_ids if not oid.startswith('new_')]
            if existing_option_ids:
                placeholders = ','.join(['%s'] * len(existing_option_ids))
                cursor.execute(f"""
                DELETE FROM options 
                WHERE question_id = %s AND id NOT IN ({placeholders})
                """, [question_id] + existing_option_ids)
            else:
                # If no existing options, delete all options for this question
                cursor.execute("DELETE FROM options WHERE question_id = %s", (question_id,))
        
        conn.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('questions_management'))
        
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'Database error: {err}', 'error')
        return redirect(url_for('edit_question', question_id=question_id))
    except Exception as e:
        conn.rollback()
        flash(f'Error updating question: {str(e)}', 'error')
        return redirect(url_for('edit_question', question_id=question_id))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/questions/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    """Delete question"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'})
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))
        conn.commit()
        return jsonify({'success': True})
        
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/questions/<int:question_id>/duplicate', methods=['POST'])
def duplicate_question(question_id):
    """Duplicate question"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'})
    
    cursor = conn.cursor()
    
    try:
        # Get original question
        cursor.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
        question = cursor.fetchone()
        
        if not question:
            return jsonify({'success': False, 'message': 'Question not found'})
        
        # Insert duplicated question
        cursor.execute("""
        INSERT INTO questions (title, question_type, is_required, order_index)
        VALUES (%s, %s, %s, %s)
        """, (f"{question[1]} (Copy)", question[2], question[3], question[4]))
        
        new_question_id = cursor.lastrowid
        
        # Duplicate options
        cursor.execute("SELECT * FROM options WHERE question_id = %s ORDER BY order_index", (question_id,))
        options = cursor.fetchall()
        
        for option in options:
            cursor.execute("""
            INSERT INTO options (question_id, text, order_index)
            VALUES (%s, %s, %s)
            """, (new_question_id, option[2], option[3]))
        
        conn.commit()
        return jsonify({'success': True, 'question_id': new_question_id})
        
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        cursor.close()
        conn.close()

@app.route('/survey')
def take_survey():
    """Survey taking interface"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('survey.html', questions=[])
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all questions
        cursor.execute("""
        SELECT * FROM questions 
        ORDER BY order_index, id
        """)
        questions = cursor.fetchall()
        
        # Get options for each question
        for question in questions:
            cursor.execute("""
            SELECT * FROM options 
            WHERE question_id = %s 
            ORDER BY order_index
            """, (question['id'],))
            question['options'] = cursor.fetchall()
        
        return render_template('survey.html', questions=questions)
        
    except mysql.connector.Error as err:
        flash(f'Database error: {err}', 'error')
        return render_template('survey.html', questions=[])
    finally:
        cursor.close()
        conn.close()

@app.route('/survey/submit', methods=['POST'])
def submit_survey():
    """Submit survey responses"""
    data = request.get_json()
    responses = data.get('responses', [])
    respondent_email = data.get('email')  # You need to collect this in your form!

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'})
    
    cursor = conn.cursor()
    respondent_id = str(uuid.uuid4())
    
    try:
        # Save responses in DB
        for response in responses:
            question_id = response['question_id']
            option_id = response.get('option_id')
            text_answer = response.get('text_answer')
            
            cursor.execute("""
            INSERT INTO answers (question_id, option_id, text_answer, respondent_id)
            VALUES (%s, %s, %s, %s)
            """, (question_id, option_id, text_answer, respondent_id))
        
        conn.commit()

        # Compose answers for email
        answers_text = ""
        for resp in responses:
            q_id = resp.get('question_id')
            option_id = resp.get('option_id')
            text_answer = resp.get('text_answer')
            answers_text += f"Question ID: {q_id}\n"
            if option_id:
                answers_text += f"Selected Option ID: {option_id}\n"
            if text_answer:
                answers_text += f"Answer: {text_answer}\n"
            answers_text += "\n"

        # Send confirmation email using Gmail SMTP via Flask-Mail
        if respondent_email:
            try:
                msg = Message(
                    subject="Survey Received - Thank You!",
                    recipients=[respondent_email],
                    body = (
                            "Thank you for completing the survey!\n\n"
                            "Your responses have been recorded successfully.\n\n"
                            "This will help us improve and provide better services in the future.\n\n"
                            "Best regards,\nThe Survey Team" )
                            
                )
                mail.send(msg)
            except Exception as e:
                print(f"Gmail email sending failed: {e}")

        return jsonify({'success': True, 'respondent_id': respondent_id})
        
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        cursor.close()
        conn.close()

@app.route('/send-test-email')
def send_test_email():
    try:
        msg = Message(
            subject="Test Email from Flask + Gmail",
            recipients=["angelo.ruiz44444@gmail.com"],  # test with your inbox
            body="This is a test email from Flask-Mail using Gmail SMTP."
        )
        mail.send(msg)
        return "Test email sent successfully!"
    except Exception as e:
        return f"Email failed: {e}"

@app.route('/admin/analytics')
def analytics():
    """Analytics dashboard"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('admin/analytics.html', questions=[])
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get questions with response statistics
        cursor.execute("""
        SELECT q.*, 
               COUNT(DISTINCT a.respondent_id) as total_responses,
               COUNT(a.id) as total_answers
        FROM questions q
        LEFT JOIN answers a ON q.id = a.question_id
        GROUP BY q.id
        ORDER BY q.order_index, q.id
        """)
        questions = cursor.fetchall()
        
        # Get detailed response data for each question
        for question in questions:
            if question['question_type'] in ['multiple_choice', 'dropdown']:
                cursor.execute("""
                SELECT o.text as option_text, COUNT(a.id) as count
                FROM options o
                LEFT JOIN answers a ON o.id = a.option_id
                WHERE o.question_id = %s
                GROUP BY o.id, o.text
                ORDER BY o.order_index
                """, (question['id'],))
                question['option_stats'] = cursor.fetchall()
                
            elif question['question_type'] == 'yes_no':
                # Get Yes/No statistics
                cursor.execute("""
                SELECT 
                    SUM(CASE WHEN a.text_answer = 'Yes' THEN 1 ELSE 0 END) as yes_count,
                    SUM(CASE WHEN a.text_answer = 'No' THEN 1 ELSE 0 END) as no_count
                FROM answers a
                WHERE a.question_id = %s
                """, (question['id'],))
                yes_no_stats = cursor.fetchone()
                question['yes_count'] = yes_no_stats['yes_count'] or 0
                question['no_count'] = yes_no_stats['no_count'] or 0
                
            elif question['question_type'] == 'rating':
                # Get rating statistics
                cursor.execute("""
                SELECT 
                    AVG(CAST(a.text_answer AS UNSIGNED)) as avg_rating,
                    COUNT(*) as total_ratings,
                    SUM(CASE WHEN a.text_answer = '1' THEN 1 ELSE 0 END) as rating_1,
                    SUM(CASE WHEN a.text_answer = '2' THEN 1 ELSE 0 END) as rating_2,
                    SUM(CASE WHEN a.text_answer = '3' THEN 1 ELSE 0 END) as rating_3,
                    SUM(CASE WHEN a.text_answer = '4' THEN 1 ELSE 0 END) as rating_4,
                    SUM(CASE WHEN a.text_answer = '5' THEN 1 ELSE 0 END) as rating_5
                FROM answers a
                WHERE a.question_id = %s AND a.text_answer IS NOT NULL
                """, (question['id'],))
                rating_stats = cursor.fetchone()
                question['avg_rating'] = float(rating_stats['avg_rating']) if rating_stats['avg_rating'] else 0.0
                question['rating_distribution'] = [
                    rating_stats['rating_1'] or 0,
                    rating_stats['rating_2'] or 0,
                    rating_stats['rating_3'] or 0,
                    rating_stats['rating_4'] or 0,
                    rating_stats['rating_5'] or 0
                ]
                
            else:
                # For essay and other text-based questions
                cursor.execute("""
                SELECT text_answer, COUNT(*) as count
                FROM answers
                WHERE question_id = %s AND text_answer IS NOT NULL
                GROUP BY text_answer
                ORDER BY count DESC
                LIMIT 10
                """, (question['id'],))
                question['text_stats'] = cursor.fetchall()
        
        return render_template('admin/analytics.html', questions=questions)
        
    except mysql.connector.Error as err:
        flash(f'Database error: {err}', 'error')
        return render_template('admin/analytics.html', questions=[])
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

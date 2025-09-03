# Professional Survey Application

A modern, web-based survey application built with Flask and Bootstrap that provides a professional interface for creating, managing, and analyzing surveys.

## Features

### 🎯 **Core Features**
- **Question Management**: Create, edit, delete, and duplicate questions
- **Multiple Question Types**: Multiple choice, essay, rating, yes/no, dropdown
- **Professional Admin Interface**: Clean, modern design matching professional standards
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Real-time Analytics**: Advanced charts and statistics
- **Question Branching**: Conditional logic (coming soon)

### 📊 **Question Types**
- **Multiple Choice**: Single selection from options
- **Essay**: Open-ended text responses
- **Rating**: Numeric rating scales (1-5, customizable)
- **Yes/No**: Binary choice questions
- **Dropdown**: Compact option selection

### 🎨 **Professional Interface**
- Clean, modern design
- Intuitive navigation
- Progress tracking
- Mobile-responsive
- Professional color scheme
- Smooth animations

## Installation

### Prerequisites
- Python 3.7 or higher
- MySQL 5.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd survey-app
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database**
   - Create a new database called `survey_app`
   - Update database credentials in `app.py` if needed:
     ```python
     DB_CONFIG = {
         'host': 'localhost',
         'user': 'root',           # Your MySQL username
         'password': '',           # Your MySQL password
         'database': 'survey_app'
     }
     ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - The application will automatically create the necessary database tables

## Usage

### Admin Dashboard
1. Click "Admin Panel" to access the management interface
2. Use the sidebar to navigate between different sections
3. Create questions using the "New Question" button
4. Manage existing questions with edit, duplicate, and delete options

### Creating Questions
1. Go to Admin → Questions
2. Click "New Question"
3. Select question type
4. Enter question text
5. Configure options (for multiple choice/dropdown)
6. Set question order and requirements
7. Save the question

### Taking Surveys
1. Click "Take Survey" from the main page
2. Answer questions one by one
3. Use Previous/Next buttons to navigate
4. Submit when all questions are answered

### Viewing Analytics
1. Go to Admin → Analytics
2. View response statistics
3. See charts and detailed breakdowns
4. Export data if needed

## File Structure

```
survey-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── survey.html       # Survey taking interface
│   └── admin/            # Admin templates
│       ├── dashboard.html
│       ├── questions.html
│       └── new_question.html
└── static/               # Static files
    ├── css/
    │   └── style.css     # Custom styles
    ├── js/
    │   └── main.js       # JavaScript functions
    └── images/           # Image assets
```

## Database Schema

### Tables
- **questions**: Stores survey questions
- **options**: Stores answer options for multiple choice questions
- **answers**: Stores user responses
- **question_branching**: Stores conditional logic (future feature)

### Key Fields
- Questions: id, title, question_type, is_required, order_index
- Options: id, question_id, text, order_index
- Answers: id, question_id, option_id, text_answer, respondent_id

## Customization

### Styling
- Modify `static/css/style.css` for custom styling
- Update Bootstrap theme in `templates/base.html`
- Add custom fonts or colors as needed

### Functionality
- Extend question types in `app.py`
- Add new admin features
- Implement question branching logic
- Add user authentication if needed

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set up a production web server (nginx + gunicorn)
2. Configure environment variables
3. Set up SSL certificates
4. Configure database for production
5. Set up monitoring and logging

## Browser Support

- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions:
- Check the documentation
- Review the code comments
- Create an issue in the repository

## Future Enhancements

- [ ] User authentication and roles
- [ ] Question branching and conditional logic
- [ ] Advanced analytics and reporting
- [ ] Email notifications
- [ ] Survey templates
- [ ] Multi-language support
- [ ] API endpoints
- [ ] Data export features
- [ ] Survey scheduling
- [ ] Response validation rules

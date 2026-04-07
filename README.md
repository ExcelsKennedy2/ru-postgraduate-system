# 📘 RU Postgraduate System

A role-based postgraduate management system designed to streamline supervision, submissions, approvals, analytics, and reporting within academic departments. The system supports multiple user roles including Students, Supervisors, Department Chairs, and Administrators.

It includes workflow automation for submissions, departmental analytics, AI-assisted features, and deployment-ready configuration for cloud hosting (Render).

---

## 🚀 Key Features

- 🔐 Role-based authentication (Student, Supervisor, Chair, Admin)
- 📄 Submission and thesis tracking system
- ✅ Approval workflow (Chair review: Approve / Defer)
- 👨‍🏫 Supervisor management and performance tracking
- 📊 Department analytics dashboard
- 📅 Meeting scheduling and milestone tracking
- 📈 Automated reporting system
- 🤖 OpenAI-powered assistant features (via `ai_module/services.py`)
- 🌐 REST API support using Django REST Framework
- 🔑 JWT authentication for secure API access

---

## 🧰 Tech Stack

- **Backend:** Django 6.0.2  
- **API Layer:** Django REST Framework  
- **Authentication:** JWT (djangorestframework-simplejwt)  
- **Database:** PostgreSQL (production), SQLite (development)  
- **Server:** Gunicorn  
- **Static Files:** Whitenoise  
- **Frontend:** Django Templates (HTML/CSS/JS)  
- **AI Integration:** OpenAI API  
- **Deployment:** Render.com  

---

## 📦 Project Structure
RU-Postgraduate-System/
│
├── ai_module/ # OpenAI services and AI utilities
├── assessments/ # Submissions, approvals, academic workflows
├── accounts/ # User authentication and roles
├── dashboard/ # Role-based dashboards (Chair, Dean, etc.)
├── templates/ # HTML templates
├── static/ # CSS, JS, images
├── manage.py
├── requirements.txt
└── README.md


---

## ⚙️ Installation & Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd RU-Postgraduate-System

## ⚙️ Installation & Setup

### 2. Create Virtual Environment
```bash
python -m venv venv

Activate:

Windows
venv\Scripts\activate
Mac/Linux
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Apply Migrations
python manage.py makemigrations
python manage.py migrate
5. Create Superuser
python manage.py createsuperuser
6. Run Development Server
python manage.py runserver
🔐 Environment Variables

Create a .env file in the root directory:

Variable	Description
SECRET_KEY	Django secret key
DEBUG	True/False
DATABASE_URL	PostgreSQL connection string
OPENAI_API_KEY	API key for OpenAI integration
ALLOWED_HOSTS	Allowed domain names
🔑 Authentication (JWT API)
Obtain Token
POST /api/token/

Request:

{
  "username": "your_username",
  "password": "your_password"
}

Response:

{
  "access": "access_token_here",
  "refresh": "refresh_token_here"
}
Refresh Token
POST /api/token/refresh/
🌐 API Endpoints Overview
/api/token/ – Obtain JWT token
/api/token/refresh/ – Refresh JWT token
/api/submissions/ – Submission management
/api/users/ – User management
/api/reports/ – Reporting system
🚀 Deployment (Render.com)
Build Command
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
Start Command
gunicorn RU_Postgraduate_System.wsgi:application
Environment Setup on Render

Set the following variables:

SECRET_KEY
DEBUG=False
DATABASE_URL (PostgreSQL from Render)
OPENAI_API_KEY
ALLOWED_HOSTS
📊 System Modules
👨‍🎓 Student Module
Submit proposals and chapters
Track progress
Receive feedback
👨‍🏫 Supervisor Module
Review submissions
Provide feedback
Track assigned students
🧑‍⚖️ Chair Module
Approve / Defer submissions
Monitor departmental progress
Generate reports
View escalations
📈 Analytics Module
Student progress tracking
Supervisor workload analysis
Department performance insights
🤖 AI Features

The system integrates OpenAI via ai_module/services.py to:

Assist in academic feedback generation
Summarize submissions
Provide writing suggestions
🧪 Common Issues & Fixes
1. Migration Errors
python manage.py makemigrations
python manage.py migrate
2. Static Files Not Loading (Production)
python manage.py collectstatic
3. Database Issues on Render
Ensure DATABASE_URL is correctly set
Run migrations after deployment
👨‍💻 Development Notes
Follow Django app modular structure
Keep business logic inside app services
Use serializers for all API responses
Keep templates lightweight (logic in views/services)
📄 License

This project is developed for academic use.

👤 Author

Kennedy Ndung'u Mbugua
Informatics – Kenya

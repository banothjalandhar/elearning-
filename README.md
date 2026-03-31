# 🚀 eLearning Platform (LMS)

A full-stack **Learning Management System (LMS)** built using Django, designed to provide a structured and scalable online learning experience similar to platforms like Udemy and Scaler.

---

## 📌 Overview

This platform enables students to:

* Learn through structured content (Subject → Topic → SubTopic)
* Attend live and recorded classes
* Practice coding
* Take assessments (MCQ & coding)
* Track their learning progress

---

## 🏗️ Tech Stack

* **Backend:** Django (Python)
* **Frontend:** HTML, CSS, JavaScript
* **Database:** SQLite / PostgreSQL
* **Authentication:** Custom User Model
* **Payments:** Stripe

---

## ✨ Features

### 🔐 Authentication & Security

* Custom user authentication system
* OTP-based login
* Single device session control
* Password reset functionality
* CSRF protection

---

### 📚 Structured Learning System

Content is organized as:

Subject → Topic → SubTopic

Each SubTopic includes:

* Theory explanation
* Examples
* Code snippets
* Detailed explanations

---

### 🎓 Course System

* Course enrollment system
* Access control for paid users
* Organized learning modules

---

### 🎥 Live & Recorded Classes

* Live class scheduling
* Real-time session access
* Recorded sessions for revision

---

### 📝 Notes System

* Topic-based notes
* Easy access for revision

---

### 🧪 Exam System

#### MCQ Tests

* Automated evaluation
* Instant results

#### Coding Tests

* Problem-solving based evaluation

---

### 📊 Progress Tracking

* Track completed topics
* Monitor test performance
* Dashboard with progress percentage

---

### 👥 Batch System

* Students grouped into batches
* Batch-specific learning and exams

---

### ⏰ Scheduled Exams

* Time-based exams
* Access restricted to batch users
* Start & end time control

---

### 💳 Payment Integration

* Secure payments using Stripe
* Access granted after successful purchase

---

### 💻 Coding Practice

* Integrated code editor
* Supports multiple languages
* Save user submissions

---

## 🔐 Access Control

| Feature         | Access         |
| --------------- | -------------- |
| Course Content  | Public         |
| Live Classes    | Enrolled Users |
| Recordings      | Enrolled Users |
| Notes           | Enrolled Users |
| Scheduled Exams | Batch Users    |

---

## 🛠️ Admin Features

* Manage subjects, topics, and subtopics
* Upload course content
* Create and manage tests
* Assign users to batches
* Schedule exams

---

## 📁 Project Structure

```bash
elearning/
│
├── learning/          # LMS core logic
├── users/             # Authentication system
├── courses/           # Course management
├── exams/             # Test system
├── templates/         # HTML templates
├── static/            # CSS, JS, assets
├── manage.py
```

---

## ⚙️ Installation

```bash
# Clone repository
git clone https://github.com/your-username/elearning.git

# Navigate into project
cd elearning

# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

---

## 🌐 Usage

* Open browser and go to:
  http://127.0.0.1:8000/

* Register / Login

* Enroll in a course

* Start learning 🚀

---

## 🔮 Future Enhancements

* Advanced analytics dashboard
* Leaderboard system
* Certificate generation
* Mobile app integration

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch
3. Commit changes
4. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Banoth Jalandhar**
Full Stack Developer | Trainer

---

⭐ If you like this project, give it a star!

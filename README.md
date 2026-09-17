# Secure Question Paper System

## 1. Project Title

**Secure Question Paper System**

## 2. Brief Description

The **Secure Question Paper System** is a web-based application developed to securely manage competitive examination question papers.

The system allows authorized users to **upload, encrypt, review, approve, release, and access** question papers. It uses role-based access control and OTP authentication to improve security and prevent unauthorized access.

The main roles are:

* Admin
* Question Setter
* Reviewer
* Exam Centre

## 3. Technologies / Tools Used

* **Python** – Programming language
* **Flask** – Web framework
* **HTML5** – Web page structure
* **CSS3** – User interface design
* **Jinja2** – Flask templates
* **AES-GCM** – Question paper encryption
* **Supabase Storage** – Secure cloud storage
* **Gmail SMTP** – OTP email service
* **Git & GitHub** – Version control
* **Google Cloud Run** – Cloud deployment

## 4. Installation and Running Steps

### Step 1: Clone the project

```bash
git clone https://github.com/Madhumitha1012/secure-exam-question-paper-system.git
cd secure-exam-question-paper-system
```

### Step 2: Create virtual environment

```bash
python -m venv venv
```

### Step 3: Activate virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure environment variables

Create a `.env` file in the project folder and add the required configuration:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ENCRYPTION_KEY=your_encryption_key
OTP_EMAIL=your_email
OTP_PASSWORD=your_gmail_app_password
```

### Step 6: Run the application

```bash
python app.py
```

Open the application in a browser:

```text
http://127.0.0.1:5000
```

## 5. Project Structure / Modules

```text
secure-exam-question-paper-system/
│
├── app.py
├── users.py
├── encryption.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── otp.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── review.html
│   ├── status.html
│   ├── release.html
│   ├── logs.html
│   └── centre_papers.html
│
├── static/
│   └── style.css
│
└── uploads/
```

### Module Purpose

* **`app.py`** – Main Flask application. Handles login, OTP, uploads, review, approval, release, access, and audit logs.
* **`users.py`** – Stores authorized users and their roles.
* **`encryption.py`** – Provides AES-GCM encryption and decryption for question papers.
* **`requirements.txt`** – Contains required Python packages.
* **`templates/`** – Contains HTML pages for different system functions.
* **`static/style.css`** – Contains the styling and design of the application.
* **`uploads/`** – Local upload folder retained for project compatibility.

## 6. Sample Input and Output

### Sample Input

```text
Exam Name: NEET
Exam Date: 15-05-2027
Release Date: 15-05-2027
Release Time: 07:30 AM
Number of Question Papers: 3
```

Uploaded files:

```text
neet_paper_1.pdf
neet_paper_2.pdf
neet_paper_3.pdf
```

Reviewer decision:

```text
Paper 1 → Approved
Paper 2 → Rejected
Paper 3 → Approved
```

Admin selects:

```text
Selected Paper: Paper 1
```

### Sample Output

```text
Login successful.
OTP sent successfully.
OTP verified successfully.

Question papers uploaded successfully.
Question Paper 1 → Approved
Question Paper 2 → Rejected
Question Paper 3 → Approved

Paper 1 → Released

Exam Centre:
Exam: NEET
Paper: Paper 1
Status: Released
Action: Open Paper
```

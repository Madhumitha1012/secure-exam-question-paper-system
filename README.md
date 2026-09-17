# Secure Exam Question Paper System

## 1. Project Title

**Secure Question Paper System**

## 2. Brief Description

The **Secure Exam Question Paper System** is a web-based application developed to securely manage competitive examination question papers.

The system allows authorized users to upload, encrypt, review, approve, release, and access question papers. It uses role-based access control and OTP authentication to improve security and prevent unauthorized access.

The main roles are:

* Admin
* Question Setter
* Reviewer
* Exam Centre

## 3. Technologies / Tools Used

* Python – Programming language
* Flask – Web framework
* HTML5 – Web page structure
* CSS3 – User interface design
* Jinja2 – Flask templates
* AES-GCM – Question paper encryption
* Supabase Storage – Secure cloud storage
* Gmail SMTP – OTP email service
* Git & GitHub – Version control
* Google Cloud Run – Cloud deployment

## 4. Installation and Running Steps

### Step 1: Clone the project

git clone https://github.com/Madhumitha1012/secure-exam-question-paper-system.git
cd secure-exam-question-paper-system

### Step 2: Create virtual environment

python -m venv venv

### Step 3: Activate virtual environment

venv\Scripts\activate

### Step 4: Install dependencies


pip install -r requirements.txt

### Step 5: Configure Environment Variables

Create a .env file in the project folder.

Add the following variables:

SUPABASE_URL – Supabase project URL
SUPABASE_KEY – Supabase project key
ENCRYPTION_KEY – Encryption key used for securing question papers
OTP_EMAIL – Email account used for sending OTP
OTP_PASSWORD – Gmail app password used for OTP email
### Step 6: Run the Application

After installing the dependencies and configuring the environment variables, run the Flask application using python app.py.

The application can be opened in a browser at http://127.0.0.1:5000.

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



Module Purpose
* app.py – Main Flask application that handles login, OTP verification, question paper upload, review, approval, release, access, and audit logs.
* users.py – Stores authorized users and their roles.
* encryption.py – Provides AES-GCM encryption and decryption for question papers.
* requirements.txt – Contains the Python packages required for the project.
* templates/ – Contains the HTML pages used for different system functions.
* static/style.css – Contains the styling and design of the application.
* uploads/ – Folder used for upload-related files.


## 6. Sample Input and Output
<img width="1887" height="877" alt="image" src="https://github.com/user-attachments/assets/01f46576-4a53-472b-b861-5a9272dece1f" />
<img width="1892" height="881" alt="image" src="https://github.com/user-attachments/assets/061eae46-8ef7-4faa-b2a9-4dff779dd096" />
<img width="1797" height="795" alt="image" src="https://github.com/user-attachments/assets/b7cfa6a8-384b-4c51-80ff-826cba9d7680" />

### Setter

<img width="1841" height="872" alt="image" src="https://github.com/user-attachments/assets/c5369354-1146-4664-bad5-a9e2f2dd5130" />
<img width="1807" height="881" alt="image" src="https://github.com/user-attachments/assets/0264ffed-e674-49d5-88c5-522dd59c433d" />

### Reviewer

<img width="1800" height="902" alt="image" src="https://github.com/user-attachments/assets/78b85196-a5bf-4acd-9d4d-147dbaeb79a6" />

### Admin

<img width="1812" height="886" alt="image" src="https://github.com/user-attachments/assets/a906cafa-72f3-411a-9dfc-c206d34b9920" />
<img width="1796" height="746" alt="image" src="https://github.com/user-attachments/assets/ece9c718-6f78-4cee-9c99-afe8bf61afe7" />
<img width="1840" height="827" alt="image" src="https://github.com/user-attachments/assets/ac37605f-43e4-4e8c-8da7-428086181e07" />
<img width="1827" height="865" alt="image" src="https://github.com/user-attachments/assets/aa02757a-1328-4e83-b723-2c5f1e8463f2" />

### Exam centre
<img width="1867" height="847" alt="image" src="https://github.com/user-attachments/assets/ca8c26c7-beaf-4d49-875d-360d0be558b5" />








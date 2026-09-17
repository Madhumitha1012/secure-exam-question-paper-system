from werkzeug.security import generate_password_hash


users = {

    "madhumitha200610@gmail.com": {
        "password": generate_password_hash("admin123"),
        "role": "Admin"
    },

    "madhumithag1012@gmail.com": {
        "password": generate_password_hash("setter123"),
        "role": "Question Setter"
    },

    "2403717610422102@cit.edu.in": {
        "password": generate_password_hash("reviewer123"),
        "role": "Reviewer"
    },

    "examcentre01@gmail.com": {
        "password": generate_password_hash("centre123"),
        "role": "Exam Centre"
    },
    "examcentre02@gmail.com": {
        "password": generate_password_hash("centre456"),
        "role": "Exam Centre"
    }


}
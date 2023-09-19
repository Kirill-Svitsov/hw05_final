[![GitHub](https://img.shields.io/badge/GitHub-Kirill--Svitsov-blue)](https://github.com/Kirill-Svitsov)
# Yatube

Yatube is a web application for sharing blog posts. Here you can create posts, comment on them, subscribe to interesting authors, and much more. Join our community and share your thoughts!

## Installation and Launch

To run Yatube locally, follow these steps:

1. Clone the repository to your local computer:

```
git clone https://github.com/Kirill-Svitsov/hw05_final.git
```
Navigate to the project directory:

```
cd hw05_final
```

Create and activate a virtual environment:

```
python -m venv venv
```
```
source venv/bin/activate  # For Linux/Mac
```
```
venv\Scripts\activate    # For Windows
```
Install dependencies:
```
pip install -r requirements.txt
```
Create and apply migrations:
```
python manage.py makemigrations
python manage.py migrate
```
Start the development server:

```
python manage.py runserver
```
Open your browser and go to http://127.0.0.1:8000/ to access Yatube.

Usage
After starting the server, you can register or log in to your account. Create posts, comment on them, subscribe to interesting authors, and enjoy exchanging thoughts with the community.

## Technologies
- Django
- Django REST framework
- PostgreSQL
- JavaScript
- HTML/CSS
- Docker


Author
Kirill Svitsov - GitHub

License
This project is distributed under the MIT license. See the LICENSE file for additional information.

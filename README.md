# saas-task-mgr
Dev quickstart:
1. copy .env.example -> .env and set variables
2. docker compose up -d   # start postgres
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py createsuperuser
6. python manage.py runserver

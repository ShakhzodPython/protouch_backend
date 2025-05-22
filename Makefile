run:
	# Starts the django development server
	command python3 manage.py runserver
migrate:
	# Creates and applies migrations
	command python3 manage.py makemigrations && python3 manage.py migrate
superuser:
	# Create superuser
	command python3 manage.py createsuperuser
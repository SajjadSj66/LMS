Write-Host "Waiting for PostgreSQL to start..."
Start-Sleep -Seconds 5  # صبر برای آماده شدن دیتابیس

Write-Host "Running Django migrations..."
python manage.py migrate
python manage.py collectstatic --noinput

Write-Host "Starting Django server..."
python manage.py runserver 0.0.0.0:8000

# AI Lead Dashboard

## Setup

# AI Lead Dashboard

## Setup

1. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in secrets:
   - `DJANGO_SECRET_KEY`: Your Django secret key (required for production)
   - `DJANGO_DEBUG`: Set to 0 for production, 1 for development
   - `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts
   - `DJANGO_CSRF_TRUSTED_ORIGINS`: Comma-separated trusted origins
   - `DATABASE_URL`: Database connection string (e.g., for Postgres)
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)
4. Run migrations:
   ```powershell
   python manage.py migrate
   ```
5. Start the server:
   ```powershell
   python manage.py runserver
   ```

## Deployment

### Heroku

1. Install the Heroku CLI and log in.
2. Create a new Heroku app:
   ```sh
   heroku create your-app-name
   ```
3. Set environment variables:
   ```sh
   heroku config:set DJANGO_SECRET_KEY=your-secret-key
   heroku config:set DJANGO_DEBUG=0
   heroku config:set DJANGO_ALLOWED_HOSTS=your-app-name.herokuapp.com
   heroku config:set DJANGO_CSRF_TRUSTED_ORIGINS=https://your-app-name.herokuapp.com
   # Add DATABASE_URL and OPENAI_API_KEY as needed
   ```
4. Push your code:
   ```sh
   git push heroku main
   ```
5. Heroku will run migrations and start Gunicorn automatically via `Procfile`.
## Static & Media Files

For production, make sure to run:
```sh
python manage.py collectstatic
```
and serve the `staticfiles/` directory using your web server or platform (e.g., Heroku, Gunicorn, or WhiteNoise).


## Desarrollo

Activar entorno:
.\.venv\Scripts\Activate.ps1
Salir del entorno: 
deactivate

Levantar API:
uvicorn main:app --reload

Swagger:
http://127.0.0.1:8000/docs

Migraciones:
alembic revision --autogenerate -m "descripcion"
alembic upgrade head

Entrar a psql: psql -U odontobot_app -d odontobot -h localhost
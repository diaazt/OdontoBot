from fastapi import FastAPI
from routers import appointments, auth, availability, patients, professionals, services, users

app = FastAPI(
    title="OdontoBot API",
    version="0.1.0"
)

app.include_router(patients.router)
app.include_router(professionals.router)
app.include_router(services.router)
app.include_router(appointments.router)
app.include_router(availability.router)
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")   # devuelve informacion basica de la API
def root():
    return {
        "message": "OdontoBot API running",
        "version": "0.1.0"
    }


@app.get("/health")   # health endpoint para verificar si la API esta funcionando (si el backend esta funcionando)                
def health():
    return {
        "status": "ok"
    }
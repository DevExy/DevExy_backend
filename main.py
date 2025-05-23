from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as auth_router
from test_gen.router import router as test_gen_router
from diagram_gen.router import router as diagram_gen_router
from requirements_manage.router import router as requirements_router
from db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(auth_router)
app.include_router(test_gen_router)
app.include_router(diagram_gen_router)
app.include_router(requirements_router)

@app.get("/")
async def root():
    return {"message": "Welcome to DevExy Backend API"}

if __name__ == "__main__":
    import uvicorn
    # When using reload=True, run Uvicorn with the module path
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
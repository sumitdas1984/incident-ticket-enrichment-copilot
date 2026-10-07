# main.py — FastAPI application
# This is the entry point.

from fastapi import FastAPI

app = FastAPI(title="Alarm Management API Simulator")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Alarm Management API Simulator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # This will start the FastAPI server when the script is run directly.
    # You can access the API at http://localhost:8000/ after running this script.
    # Press Ctrl+C to stop the server.
    # Note: In a production environment, you would typically use a process manager to run the server.
    # For development purposes, you can also use the --reload flag with uvicorn to enable hot-reloading.
    # Example: uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    # End of script.
    
import asyncio
from fastapi import FastAPI, APIRouter

# Define your endpoint functions outside the class
async def root():
    return {"message": "Hello World from the function"}

async def run_subprocess():
    # Example: Running 'echo' command. Replace with your actual command
    process = await asyncio.create_subprocess_shell(
        'echo "Hello from subprocess"',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()

    if stderr:
        return {"error": stderr.decode()}
    
    return {"message": stdout.decode().strip()}

class APIEndpoints:
    def __init__(self, endpoint_functions):
        self.router = APIRouter()
        self.endpoint_functions = endpoint_functions
        self._register_routes()

    def _register_routes(self):
        # Iterate through the list of functions passed to the constructor
        for path, func in self.endpoint_functions.items():
            self.router.add_api_route(path, self._wrap_async(func), methods=["GET"])

    def _wrap_async(self, func):
        # This wrapper converts the standalone async function to a method that can be called on the class instance.
        async def wrapped():
            return await func()
        return wrapped

# Initialize FastAPI app
app = FastAPI()

# Create an instance of your APIEndpoints class, passing a dictionary of endpoint functions
api_endpoints = APIEndpoints({
    "/": root,
    "/run-subprocess": run_subprocess
})

# Include the routes from the APIEndpoints instance into your FastAPI app
app.include_router(api_endpoints.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
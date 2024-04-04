from process_builder import ProcessBuilder
from process_runner import DockerRunner
from llm import GPTWrapper
from houdini_api import APIEndpoints
from pprint import pp
from async_function_generator import AsyncFunctionGenerator
from fastapi import FastAPI, APIRouter 

fns = [
    "generate a random number from 0 to 100",
    "get time in italy",
    "generate the first 16 numbers of pi",
    "print the hex for the color blue",
    "generate the first 16 numbers of pi",
]


processes = [ProcessBuilder(llm=GPTWrapper(), task=fn, epochs=3).build_process() for fn in fns]

pp(processes)

images = [process["image"].id for process in processes]
names = [process["endpoint_name"].strip("\"").strip("`").strip("\\").strip("/").strip("\(\)") for process in processes]

generator = AsyncFunctionGenerator(names, images)

api_endpoints = APIEndpoints({ "/"+fn.__name__:fn  for fn in generator.functions})
# api_endpoints.endpoint_functions

app = FastAPI()

app.include_router(api_endpoints.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
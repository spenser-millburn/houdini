from typing import List, Callable, Coroutine
import asyncio

class AsyncFunctionGenerator:
    def __init__(self, function_names: List[str], image_list: List[str]):
        self.functions: List[Callable[..., Coroutine]] = []
        self._generate_functions(function_names, image_list=image_list)

    def _generate_function(self, name: str, image: str) -> Callable[..., Coroutine]:
        # Prepare the function body with the image variable correctly interpolated
        async_template = f"""
async def {name}():
    print("hello from '{image}'")
    import subprocess;
    return subprocess.run(["docker", "run", "{image}"], capture_output=True, text=True)
 
"""
        local_namespace = {}
        # Pass the globals and local_namespace as the environment for the exec
        exec(async_template, globals(), local_namespace)
        # The created function is now stored in the local_namespace with the key as its name
        return local_namespace[name]

    def _generate_functions(self, function_names: List[str], image_list: List[str]):
        for name, image in zip(function_names, image_list):
            # Generate a function for each name, passing along the corresponding image string
            self.functions.append(self._generate_function(name, image))

import shutil
import uuid
import os
from docker import DockerClient, errors

class DockerRunner:
    def __init__(self):
        self.docker_client = DockerClient(base_url='unix://var/run/docker.sock')

    def run_from_image_id(self, image_id, run_duration=5):
        container = self.docker_client.containers.run(image_id, detach=True)
        container.stop()
        # Capture runtime logs
        logs = container.logs(timestamps=True).decode('utf-8')
        # Wait for the specified run duration
        container.wait(timeout=run_duration)
        container.remove()
        response = {}
        response["image"] = image
        response["run_logs"] = logs
        return response

    def run_dockerfile(self, dockerfile_path, run_duration=5):
        # Generate a random directory to store the Dockerfile
        dir_path = f"temp/{str(uuid.uuid4())}"
        os.makedirs(dir_path, exist_ok=True)
        temp_dockerfile_path = os.path.join(dir_path, "Dockerfile")
        
        # Prepare the response dictionary
        response = {"dockerfile": dockerfile_path}
        with open(dockerfile_path, 'r') as file: data = file.read() 
        response["dockerfile_content"] = data
        
        try:
            # Copy Dockerfile to the temporary directory
            shutil.copy(dockerfile_path, temp_dockerfile_path)
            
            # Build the Docker image
            # image, build_logs = self.docker_client.images.build(path=dir_path, rm=True, forcerm=True)
            image, build_logs = self.docker_client.images.build(path=dir_path)
            
            # Run the container
            container = self.docker_client.containers.run(image.id, detach=True)
            
            # Wait for the specified run duration
            container.wait(timeout=run_duration)
            
            # Capture runtime logs
            logs = container.logs(timestamps=True).decode('utf-8')

            response["build_logs"] = [log.get('stream', '') for log in build_logs if 'stream' in log]
            response["image"] = image
            response["run_logs"] = logs
            
            # Stop and remove the container
            container.stop()
            container.remove()
            
        except (errors.DockerException, errors.APIError) as e:
            print(f"Error: {e}")
            response["error"] = str(e)
        
        finally:
            # Cleanup: remove the directory after building
            shutil.rmtree(dir_path)
        
        return response

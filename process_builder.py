import io
from pprint import pp
from process_runner import DockerRunner

class ProcessBuilder:
    def __init__(self, llm, task : str, epochs=1 ):
        self.llm = llm
        self.task = task
        self.epochs = epochs
        self.dockerfile_path = './Dockerfile'
        self.build_initial()

    def build_initial(self):
        dockerfile_lines = [self.llm.generate_dockerfile(self.task)]
        with open(self.dockerfile_path, 'w') as file:
            file.writelines(dockerfile_lines)

    def run_dockerfile(self):
        docker_runner = DockerRunner()
        result = docker_runner.run_dockerfile(self.dockerfile_path)
        return result

    def iterate(self, new_result, user_feedback):
        refined_dockerfile_lines = self.llm.refine_dockerfile(
            user_feedback, 
            dockerfile_string=new_result.get('dockerfile_content'),
            build_logs=new_result.get('build_logs not available', None),
            run_logs=new_result.get('run_logs', "run logs not available"),
            errors=new_result.get("error", "no errors"),
            topic=self.task
        )
        with open(self.dockerfile_path, 'w') as file:
            file.write(refined_dockerfile_lines)
        return self.run_dockerfile()

    def documented(self, result):
        result['documentation'] = self.llm.generate_text(f"I am writing an api endpoint for the given task {self.task}, write a 10 word description for the enpoint including the request type, description and any inputs. Respond with only the 10 words")
        result['endpoint_name'] = self.llm.generate_text(f"respond with only one word: an appropriate function name for {self.task}")
        result['task'] = self.task
        result['epochs'] = self.epochs
        result.pop("build_logs")
        result.pop("run_logs")
        # result['run_logs'] = io.StringIO(result["run_logs"])
        # result['build_logs'] = io.StringIO(result["build_logs"])
        return result

    def build_process(self) -> dict: 
        result = {'dockerfile_content': None}  # Initialize result dictionary
        for _ in range(self.epochs):
            feedback = self.llm.generate_text(f"in 20 words describe what went wrong")
            result = self.iterate(new_result=result, user_feedback=feedback)
            if 'error' not in result or not result['error']:  # Assuming 'error' key presence indicates issues
                break  # Exit loop if no errors in the latest iteration
        return self.documented(result)
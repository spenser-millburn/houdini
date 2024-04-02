
FROM python:latest

RUN python -c 'import random; print(random.randint(100, 10000))' 

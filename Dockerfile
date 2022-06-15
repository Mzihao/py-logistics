FROM python:3.9.7-slim-buster
WORKDIR /fastapi_template
COPY . .
RUN pip install -i https://pypi.doubanio.com/simple/ -r requirements.txt
EXPOSE 9000
CMD ["python","app_run.py"]
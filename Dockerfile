FROM python:3.10

WORKDIR /code

COPY . .

RUN pip install .

EXPOSE 5111

# CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "5111"]
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5111", "src.api.app:app"]

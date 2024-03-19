FROM python:3.11.7

ENV POETRY_HOME=/opt/poetry
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

WORKDIR /app
COPY ./install-poetry.py /app/
RUN python install-poetry.py --version 1.5.1

COPY ./poetry.lock ./pyproject.toml /app/
RUN $POETRY_HOME/bin/poetry export -f requirements.txt --output ./requirements.txt
RUN pip install -r ./requirements.txt

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]

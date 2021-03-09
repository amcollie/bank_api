FROM python:3.8-alpine3.12
WORKDIR /usr/src/app
RUN apk add --update musl-dev gcc libffi-dev
RUN pip install --upgrade pip
RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv install --system --deploy --ignore-pipfile
COPY . .
CMD ["pipenv", "run", "flask", "run"]
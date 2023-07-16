FROM python:3.11

ADD . /app/
WORKDIR /app/
RUN pip install -r requirements.txt


# #
# # Build image
# #

# FROM python:3.11 AS builder

# WORKDIR /app
# COPY . .

# RUN apt update -y && apt upgrade -y && apt install curl -y
# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
# RUN $HOME/.poetry/bin/poetry config virtualenvs.create false 
# RUN $HOME/.poetry/bin/poetry install --no-dev 
# RUN $HOME/.poetry/bin/poetry export -f requirements.txt >> requirements.txt

# #
# # Prod image
# #

# FROM python:3.11 AS runtime

# WORKDIR /app
# COPY --from=builder /app/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
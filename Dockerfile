FROM python:3.10.12-slim-bullseye
RUN addgroup app && useradd -m -g app app
RUN apt update
RUN apt install python3-pip python3-setuptools  -y
USER app
WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv env 
RUN . env/bin/activate
RUN pip install -r requirements.txt
COPY . .
CMD [ "python3", "bot.py" ]

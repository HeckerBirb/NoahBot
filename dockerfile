FROM python:3.9

RUN apt-get update -y
RUN apt-get install mariadb-client python3 python3-pip libmariadb-dev -y

COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade -r /tmp/requirements.txt
RUN pip3 install -U git+https://github.com/Pycord-Development/pycord

COPY . /noahbot
WORKDIR /noahbot

ENV PYTHONPATH "${PYTHONPATH}:/noahbot/src"

ENTRYPOINT ["python3", "-u", "src/noahbot.py"]

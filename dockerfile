FROM python:3.9

RUN apt-get update -y
RUN apt-get install mariadb-client python3 python3-pip libmariadb-dev -y

COPY ./requirements.txt /tmp/requirements.txt

# Cache bust argument - modify to pip update, otherwise it uses cached fs layers
ARG LAST_UPDATED=2021-12-28-21-12-CET

RUN pip3 install --upgrade -r /tmp/requirements.txt
RUN pip3 install -U git+https://github.com/Pycord-Development/pycord@1c17e64c2d78ba6740f3a1234c95f230be13ea83 aiohttp

COPY . /noahbot
WORKDIR /noahbot

ENV PYTHONPATH "${PYTHONPATH}:/noahbot/src"

ENTRYPOINT ["python3", "-u", "src/noahbot.py"]

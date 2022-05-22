FROM alpine:latest
EXPOSE 5000

RUN apk add --no-cache gcc musl-dev python3 python3-dev py3-pip mariadb-connector-c-dev
RUN pip install flask==2.1.2 mariadb==1.0.11
COPY . /app
WORKDIR /app
ENTRYPOINT ["python3", "app.py"]

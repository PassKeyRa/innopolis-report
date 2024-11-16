FROM docker.io/clojure:tools-deps-bullseye

RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app
COPY math math
RUN cd math && clojure -M:run --help && cd ..

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY src src

WORKDIR /app/src

EXPOSE 8080

CMD ["python3", "main.py", "server", "--port", "8080", "--host", "0.0.0.0"]
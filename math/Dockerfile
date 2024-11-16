FROM docker.io/clojure:tools-deps-bullseye

RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app
COPY . .

# Install clojure and fetch dependencies
RUN clojure -A:dev -P

CMD ["./bin/run"]

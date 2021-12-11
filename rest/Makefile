VERSION=v4
DOCKERUSER=387527458246

build:
	docker build -f Dockerfile-rest -t song-rest .

push:
	docker tag song-rest $(DOCKERUSER)/song-rest:$(VERSION)
	docker push $(DOCKERUSER)/song-rest:$(VERSION)
	docker tag song-rest $(DOCKERUSER)/song-rest:latest
	docker push $(DOCKERUSER)/song-rest:latest

VERSION=v4
DOCKERUSER=387527458246

build:
	docker build -f Dockerfile-generator -t generator .

push:
	docker tag generator $(DOCKERUSER)/generator:$(VERSION)
	docker push $(DOCKERUSER)/generator:$(VERSION)
	docker tag generator $(DOCKERUSER)/generator:latest
	docker push $(DOCKERUSER)/generator:latest

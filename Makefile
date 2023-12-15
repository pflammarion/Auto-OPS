IMAGE_NAME = autoops
CONTAINER_NAME = autoops_container

build:
	mkdir -p "./tmp"
	docker rmi -f $(IMAGE_NAME)
	docker build -t $(IMAGE_NAME) .

start-linux:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker run --name $(CONTAINER_NAME) -d -v "$(PWD):/app" -it $(IMAGE_NAME)
	docker exec -it $(CONTAINER_NAME) bash

start-windows:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker run --name $(CONTAINER_NAME) -d -v "%cd%:/app" -it $(IMAGE_NAME)
	docker exec -it $(CONTAINER_NAME) bash

stop:
	docker stop $(CONTAINER_NAME)

clear:
	docker rm $(CONTAINER_NAME)

.PHONY: build start stop clear

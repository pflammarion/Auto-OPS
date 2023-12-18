IMAGE_NAME = autoops
CONTAINER_NAME = autoops_container

# To access to the GUI you need to enable X11 forwarding. For MacOs you can use https://www.xquartz.org/ and brew install socat.
# Then listen to socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\"

build:
	mkdir -p "./tmp"
	docker rmi -f $(IMAGE_NAME)
	docker build -t $(IMAGE_NAME) .

start:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker run -e DISPLAY=host.docker.internal:0 --name $(CONTAINER_NAME) -d -v "$(PWD):/app" --rm -it $(IMAGE_NAME)
	docker exec -it $(CONTAINER_NAME) bash

start-windows:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker run -e DISPLAY=host.docker.internal:0 --name $(CONTAINER_NAME) -d -v "%cd%:/app" --rm -it $(IMAGE_NAME)
	docker exec -it $(CONTAINER_NAME) bash

stop:
	docker stop $(CONTAINER_NAME)

clear:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker rmi -f $(IMAGE_NAME) || true

.PHONY: build start stop clear

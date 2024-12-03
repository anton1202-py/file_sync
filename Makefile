IMAGE_NAME = working-with-files
DOCKERFILE = Dockerfile
CONTEXT = .

tag = $(shell cat $(CONTEXT)/version.txt)

IMAGE = $(IMAGE_NAME):$(tag)

all: build

build:
	@docker build -f $(DOCKERFILE) -t $(IMAGE) $(CONTEXT)

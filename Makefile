PROJECT_DIR := $(realpath $(CURDIR))
#================================================================
# Usage: based on setup.mk file
#================================================================
# make glue-image				# connect to glue container with the purpose of debugging
# make jupyter					# jupyter notebook
# make tf-planfile				# planfile to docker
# make tf-applyfile				# apply changes to AWS

#=======================================================================
# Variables
#=======================================================================
.EXPORT_ALL_VARIABLES:
include .docker/make/variables.mk # load variables from a separate makefile file
include .docker/make/setup.mk # load variables from a separate makefile file

#=======================================================================
# make commands for debuging and executing docker-compose
#=======================================================================
.PHONY: glue-image
glue-image: copy-files
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm glue

jupyter: build-glue-note
	@docker run -it \
		-v ~/.aws:/home/glue_user/.aws  \
		-e AWS_PROFILE=localstack \
		-e DISABLE_SSL=true --rm \
		-p 4040:4040 -p 18080:18080 -p 8998:8998 -p 8888:8888 \
	$(REPOSITORY)-notebook-test

#=======================================================================
# tests commands
#=======================================================================
unittests: copy-files build-glue
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm unittests

unittests-watch: copy-files build-glue
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm unittests-watch || true

testing-environment: create-network copy-files check-container run-aws-mock
.PHONY: systemtests
systemtests: testing-environment
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm systemtests

.PHONY: systemtests-watch
systemtests-watch: testing-environment
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm systemtests-watch || true

.PHONY: tests
tests: systemtests unittests

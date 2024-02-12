include .docker/make/variables.mk # load variables from a separate file

###########################################################################
# docker commands
###########################################################################
build-%:
	docker-compose $(COMPOSE_TEST_FLAGS) build $*

run-%: check-container
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm $*

create-network:
	@printf "\033[32m#%.0s\033[0m" {1..100}
	@echo "\n${CRITICAL}=>  Creating network 'data_bridge'${COLOUR_OFF}\n"
	@printf "\033[32m#%.0s\033[0m" {1..100}
	@docker network create -d bridge data_bridge 2>/dev/null || true

stop-all-containers:
	docker ps -q | xargs -I@ docker stop @

clear-all-containers: stop-all-containers
	docker ps -aq | xargs -I@ docker rm @

clear-volumes: clear-all-containers
	docker volume ls -q | xargs -I@ docker volume rm @

clear-images: clear-volumes
	docker images -q | uniq | xargs -I@ docker rmi -f @

stop-db:
	docker ps -aqf ancestor=handler-postgres| xargs -I@ sh -c 'docker stop @ && docker rm @' || true

clear-db: stop-db
	docker image ls -aqf=reference='handler-postgres' | xargs -I@ docker rmi -f @ || true

clear-systemtests: clear-db
	docker image ls -aqf=reference='handler-systemtests-watch' | xargs -I@ docker rmi -f @ || true

start-glue:
	docker exec -it $(docker ps -aqf ancestor=handler-systemtests-watch) bash

glue-%: copy-files
	@docker-compose $(COMPOSE_TEST_FLAGS) run --rm glue-$*

#=======================================================================
# move file to mulitple locations
#=======================================================================
BUILD_DIR := $(PROJECT_DIR)
PY_SOURCES = $(patsubst %,$(BUILD_DIR)/%, pyproject.toml)
POETRY_SOURCES = $(patsubst %,$(BUILD_DIR)/%, poetry.lock)
PY_PROJECT = $(foreach dir, $(DESTINATION_DIRS), $(patsubst %, $(BUILD_DIR)/$(dir)/%, pyproject.toml))
POETRY_PROJECT = $(foreach dir, $(DESTINATION_DIRS), $(patsubst %, $(BUILD_DIR)/$(dir)/%, poetry.lock))
DESTINATION_DIRS := ./tests/system ./tests/unit ./.docker/glue_integrater ./.docker/notebook

.SECONDEXPANSION:
$(PY_PROJECT) $(POETRY_PROJECT): $(BUILD_DIR)/$$(notdir $$@)
	@echo "${INFO}=> Moving $< to $@ ${COLOUR_OFF}"
	@cp $< $@

copy-files: $(PY_PROJECT) $(POETRY_PROJECT)

check-container:
ifdef LOCAL_STACK_PORT
	@echo "=> remove localstack container"
	@docker stop $(LOCAL_STACK_PORT)
	@docker rm $(LOCAL_STACK_PORT)
else
	@echo "=> nothing to for containers be done"
endif

ifndef BKF_TERRAFORM_ENV_FILE
ifdef JENKINS_URL
BKF_TERRAFORM_ENV_FILE=.enviroment/cicd.env
else
BKF_TERRAFORM_ENV_FILE=.enviroment/local.env
endif
export BKF_TERRAFORM_ENV_FILE
endif

#=======================================================================
# terraform commands
#=======================================================================
terraform-%:
	@echo "=>  Check validate|fmt command"
	@docker-compose -f docker-compose.yaml run terraform $* -upgrade

tf-plan:
	@echo "=>  Main make plan into environment: [${ENVIRONMENT}]"
	@docker-compose -f docker-compose.yaml run terraform validate
	@docker-compose -f docker-compose.yaml run terraform plan \
		-lock=false -no-color \
		-var-file ./$(ENVIRONMENT)/terraform.tfvars

tf-planfile:
	@printf "\033[32m#%.0s\033[0m" {1..100}
	@echo "\n${CRITICAL}=>  Main make environment: [${ENVIRONMENT}]${COLOUR_OFF}\n"
	@docker-compose -f docker-compose.yaml run terraform init \
		-upgrade -backend-config=./${ENVIRONMENT}/backend
	@echo "${CRITICAL}=>  Plan into file [${ENVIRONMENT}] ${COLOUR_OFF}\n"
	@printf "\033[32m#%.0s\033[0m" {1..100}
	@docker-compose -f docker-compose.yaml run terraform plan \
		-lock=false -no-color \
		-var-file ./$(ENVIRONMENT)/terraform.tfvars \
		-out=./$(ENVIRONMENT)/planfile

tf-applyfile:
	@printf "\033[32m#%.0s\033[0m" {1..100}
	@echo "\n${CRITICAL}=> Apply planfile for environment: [${ENVIRONMENT}]${COLOUR_OFF}"
	@printf "\033[32m#%.0s\033[0m" {1..100}
	@docker-compose -f docker-compose.yaml run terraform apply \
		-lock=false "./$(ENVIRONMENT)/planfile"

tf-destroy:
	@echo "=>  Destroy environment: [${ENVIRONMENT}]"
	@docker-compose -f docker-compose.yaml run terraform init -upgrade\
		-reconfigure -backend-config=./${ENVIRONMENT}/backend
	@docker-compose -f docker-compose.yaml run terraform destroy \
		-var-file ./${ENVIRONMENT}/terraform.tfvars

refresh:
	terraform -chdir=$(TERRAFORM) refresh -var-file ./${ENVIRONMENT}/terraform.tfvars

state-file-%:
	@echo "=>  deply global changes to: [${ENVIRONMENT}]"
	@docker-compose -f docker-compose.yaml \
		run terraform -chdir=/infrastructure/global/${ENVIRONMENT} $* \
			-var aws_account=${AWS_PROFILE}

tf-%:
	@printf "\033[32m#%.0s\033[0m" {1..100}
	@printf "\033[32m#%.0s\033[0m" {1..100}
	@docker-compose -f docker-compose.yaml run terraform $* \
		-reconfigure -backend-config=./$(AWS_REGION)/$(ENVIRONMENT)/backend

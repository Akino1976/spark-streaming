#!/bin/bash
set +x
GREEN="\033[32m"
NO_COLOUR="\033[0m"
RED="\033[31m"

until curl http://localstack:4566 &>/dev/null; do
   echo "endpoint localstack is unavailable, wait"
   sleep 2
done

AWSCMD="aws --region eu-west-1 --endpoint-url=http://localstack:4566"
function logs(){
   local message=$1
   local parameter=$2

   printf "${RED}=%.0s${NO_COLOUR}" {1..100}
   printf "\n${GREEN}# %s (%s) \n${NO_COLOUR}" "$message" "$parameter"
   printf "${RED}=%.0s${NO_COLOUR}" {1..100}
   printf "\n"
}
echo "Start provisioning"

function create_or_update_stack(){
   local stackname=$1
   type_formation="update"
   if ! ${AWSCMD} cloudformation describe-stacks --stack-name $stackname
   then
      type_formation="create"
   fi
   logs "cloudformation process is " "${type_formation}"
   ${AWSCMD} cloudformation ${type_formation}-stack \
      --stack-name ${stackname} \
      --template-body file://infrastructure/cfn-streaming-service.yaml \
      --parameters \
         ParameterKey=Environment,ParameterValue=${ENVIRONMENT} \
         ParameterKey=ServiceName,ParameterValue=${SERVICENAME}
      ${AWSCMD} cloudformation wait stack-${type_formation}-complete \
         --stack-name ${stackname}
}

logs "Validation of template for " "[${SERVICENAME}-${ENVIRONMENT}]"
${AWSCMD} cloudformation validate-template --template-body file://infrastructure/cfn-streaming-service.yaml
logs "Validation done for " "[${SERVICENAME}-${ENVIRONMENT}]"
create_or_update_stack ${SERVICENAME}-${ENVIRONMENT}


STACK=$(${AWSCMD} cloudformation describe-stacks --stack-name ${SERVICENAME}-${ENVIRONMENT})
printf "\n"
printf "${RED}*%.0s${NO_COLOUR}" {1..100}
printf "\n"
printf "##${GREEN} %s ${NO_COLOUR} ##\n"  "${STACK}"
printf "${RED}*%.0s${NO_COLOUR}" {1..100}
printf "\n"

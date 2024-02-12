#!/bin/bash
GREEN="\033[32m"
NO_COLOUR="\033[0m"
RED="\033[31m"
PACKAGE_NAME=${1:-glue_library.zip}
FOLDER_NAME="glue_library"

printf "${RED}=%.0s${NO_COLOUR}" {1..100}
printf "\n${GREEN}> Zipping contents of %s into %s \n${NO_COLOUR}" "${PWD}/${FOLDER_NAME}, ${PACKAGE_NAME}"
printf "${RED}=%.0s${NO_COLOUR}" {1..100}
printf "\n"

pip install \
    --requirement ${PWD}/requirements.txt \
    --target ${PWD}/${FOLDER_NAME} \
    --no-index --find-links /usr/tmp/wheelhouse
mkdir -p ${FOLDER_NAME}
cp -R ./common ${FOLDER_NAME}
cd ${FOLDER_NAME}
zip -r ../${PACKAGE_NAME} . -x '*.*dist-info/*'
cd ../
printf "${RED}=%.0s${NO_COLOUR}" {1..100}
printf "\n${GREEN} > Finished packaging glue into %s\n" "${PWD}/${FOLDER_NAME}"
printf "${RED}=%.0s${NO_COLOUR}" {1..100}
printf "\n"

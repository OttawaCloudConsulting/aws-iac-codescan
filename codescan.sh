#!/bin/bash

## Execute this file as ./code-scan.sh
## All Variables are optional
## Example:  code-scan.sh --project "my_project" --fmt "false" --terrascan "true"
##
## --project "" | Defaults to pwd name
## --planfile "" | Terraform Plan filename
## --planjson "" | Terraform Plan JSON version filename
## --scanoutput "" | Scan Output folder.  Defaults to ./codescan_report/
## --terrascanoutput "" | Terrascan Output Filename
## --severity "" | Minimum Severity (tfsec and terrascan support only)
## --fmt "true" | Perform terraform format
## --validate "true" | Validate Terraform
## --tflint "true" | Lint Terraform files
## --checkov "true" | Perform Checkov scan
## --terrascan "true" | Perform terrascan scan
## --tfsec "true" | Perform tfsec scan
## --cleanup "true" | Delete files


project=${project:-$(basename "${PWD}")}
planfile=${planfile:-'tf.plan'}
planjson=${planjson:-'tf_plan.json'}
scanoutput=${scanoutput:-'codescan_report'}    
terrascanoutput=${terrascanoutput:-'terrascan.txt'}
tfscanoutput=${tfscanoutput:-'tfsec.txt'}
severity=${severity:-'LOW'}

fmt=${fmt:-'true'}
validate=${validate:-'true'}
tflint=${tflint:-'true'}
checkov=${checkov:-'true'}
terrascan=${terrascan:-'false'}
tfsec=${tfsec:-'false'}
cleanup=${cleanup:-'false'}


while [ $# -gt 0 ]; do
    if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare $param="$2"
        # echo $1 $2 // Optional to see the parameter:value result
    fi
  shift
done

# Get latest URLs for download
VAR_TERRASCAN_URL=$(curl -sL https://api.github.com/repos/accurics/terrascan/releases/latest | grep browser_download_url | grep "Linux_x86" | cut -d '"' -f 4)
VAR_TFSECGEN_URL=$(curl -sL https://api.github.com/repos/aquasecurity/tfsec/releases | grep browser_download_url | grep tfsec-checkgen-linux-amd64 | awk 'NR==1' | cut -d '"' -f 4)
VAR_TFSEC_URL=$(curl -sL https://api.github.com/repos/aquasecurity/tfsec/releases | grep browser_download_url | grep tfsec-linux-amd64 | awk 'NR==1' | cut -d '"' -f 4)

### Functions

function install-tflint () {
  curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash
}

function terraform-lint () {
  tflint --version
  tflint
  arr=(*/)
  for d in "${arr[@]}"; do
    subdir=$(echo $d | sed "s,/$,,")
    ( cd $subdir && tflint )
  done
}

function terraform-plan () {
  rm -f $planfile
  terraform plan \
    -refresh=false \
    -out $planfile > /dev/null
}

function terraform-plan-to-json () {
  terraform show \
    -json $planfile \
    > $planjson
}

function clean-up-files () {
  rm -f \
    $planfile \
    $planjson
}

function checkov-simple () {
  checkov \
    --soft-fail \
    --file $planjson
}

# set IaC Framework language, soft fail ALWAYS returns exit 0, output file path creates report, path MUST exist, file provides input plan
function checkovoutput-file () {
  mkdir -p $scanoutput
  terraform-plan-to-json
  echo "checkov verion" $(checkov --version)
  checkov \
  --framework cloudformation terraform terraform_plan \
  --soft-fail \
  --output-file-path $scanoutput \
  --file $planjson
}

function install-terrascan () {
  curl -L $VAR_TERRASCAN_URL \
  -o terrascan.tar.gz
  tar -xf terrascan.tar.gz terrascan && rm -f terrascan.tar.gz
  install terrascan /usr/bin && rm -f terrascan
}

function terrascan-scan () {
  mkdir -p $scanoutput
  echo "terrascan" $(terrascan version)
  terrascan scan \
    --iac-type terraform \
    --severity $severity \
    --policy-type aws \
    --show-passed \
    --output human \
    > "$scanoutput/$terrascanoutput"
}

function install-tfsec () {
  curl -L $VAR_TFSECGEN_URL -o tfsec-checkgen
  install tfsec-checkgen /usr/bin
  rm -f tfsec-checkgen
  curl -L $VAR_TFSEC_URL -o tfsec
  install tfsec /usr/bin
  rm -f tfsec
}

function tfsec-scan () {
  mkdir -p $scanoutput
  echo "checkov verion" $(tfsec --version)
  tfsec \
    --concise-output \
    --include-passed \
    --include-passed \
    --minimum-severity $severity \
    --out "$scanoutput/$tfscanoutput"
}

if [ $fmt = "true" ]
  then
    echo "Performing Terraform Format..."
    terraform fmt -recursive
  fi
if [ $validate = "true" ]
  then
    echo "Performing Terraform Validate..."
    terraform validate
  fi
if [ $tflint = "true" ]
  then
    echo "Performing Terraform Lint..."
    terraform-lint
  fi
if [ $checkov = "true" ]
  then
    echo "Performing Checkov Scan..."
    terraform-plan
    checkovoutput-file
  fi
if [ $terrascan = "true" ]
  then
    echo "Performing TerraScan Scan..."
    terrascan-scan
  fi
if [ $tfsec = "true" ]
  then
    echo "Performing TFSec Scan..."
    tfsec-scan
  fi
if [ $cleanup = "true" ]
  then
      echo "Remove Scan Result Files - Not available yet"
  fi

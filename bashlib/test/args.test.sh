export OCRD_TOOL_JSON=./test/ocrd-tool.json
export OCRD_TOOL_NAME="ocrd-test-bashlib"
declare -A argv
source `ocrd bashlib`

ocrd__parse_argv "$@"

for k in "${!argv[@]}";do
    echo "$k == ${argv[$k]}"
done

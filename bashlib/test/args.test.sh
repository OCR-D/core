export OCRD_TOOL_JSON=./test/ocrd-tool.json
export OCRD_TOOL_NAME="ocrd-test-bashlib"
declare -A ocrd__argv=()
source `ocrd bashlib filename`

ocrd__parse_argv "$@"

for k in "${!ocrd__argv[@]}";do
    echo "$k == ${ocrd__argv[$k]}"
done

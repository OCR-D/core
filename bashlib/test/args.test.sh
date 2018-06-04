export OCRD_TOOL_JSON=foo
declare -A argv
source ./lib.bash

ocrd__parse_argv "$@"

for k in "${!argv[@]}";do
    echo "$k == ${argv[$k]}"
done

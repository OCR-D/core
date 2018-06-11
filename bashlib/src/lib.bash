# HERE-INCLUDE ./src/raise.bash
# HERE-INCLUDE ./src/dumpjson.bash
# HERE-INCLUDE ./src/usage.bash
# HERE-INCLUDE ./src/parse_argv.bash

if ! which "ocrd" >/dev/null 2>/dev/null;then
    ocrd__raise "ocrd not in \$PATH"
fi

if ! declare -p "OCRD_TOOL_JSON" >/dev/null 2>/dev/null;then
    ocrd__raise "Must set \$OCRD_TOOL_JSON"
elif [[ ! -r "$OCRD_TOOL_JSON" ]];then
    ocrd__raise "Cannot read \$OCRD_TOOL_JSON: '$OCRD_TOOL_JSON'"
fi

if [[ -z "$OCRD_TOOL_NAME" ]];then
    ocrd__raise "Must set \$OCRD_TOOL_NAME"
elif ! ocrd ocrd-tool "$OCRD_TOOL_JSON" list-tools|grep -q "$OCRD_TOOL_NAME";then
    ocrd__raise "No such command \$OCRD_TOOL_NAME: $OCRD_TOOL_NAME"
fi


ocrd__wrap () {

    declare -gx OCRD_TOOL_JSON="$1"
    declare -gx OCRD_TOOL_NAME="$2"
    shift
    shift
    declare -Agx params
    params=()
    declare -Agx ocrd__argv
    ocrd__argv=()

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

    ocrd__parse_argv "$@"

    i=0
    declare -ag ocrd__files
    while read line; do
        eval declare -Ag "ocrd__file$i=( $line )"
        eval "ocrd__files[$i]=ocrd__file$i"
        let ++i
    done < <(ocrd bashlib input-files \
                  -m "${ocrd__argv[mets_file]}" \
                  -I "${ocrd__argv[input_file_grp]}" \
                  -O "${ocrd__argv[output_file_grp]}" \
                  ${ocrd__argv[page_id]:+-g} ${ocrd__argv[page_id]:-})
}

# usage: pageId=$(ocrd__input_file 3 pageId)
ocrd__input_file() {
    eval echo "\${${ocrd__files[$1]}[$2]}"
}

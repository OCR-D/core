# BEGIN-INCLUDE ./src/raise.bash 
## ### `ocrd__raise`
## 
## Raise an error and exit.
ocrd__raise () {
    echo >&2 "ERROR: $1"; exit 127
}

# END-INCLUDE 
# BEGIN-INCLUDE ./src/dumpjson.bash 
## ### `ocrd__dumpjson`
## 
## Output ocrd-tool.json.
## 
## Requires `$OCRD_TOOL_JSON` and `$OCRD_TOOL_NAME` to be set:
## 
## ```sh
## export OCRD_TOOL_JSON=/path/to/ocrd-tool.json
## export OCRD_TOOL_NAME=ocrd-foo-bar
## ```
## 
ocrd__dumpjson () {
    ocrd ocrd-tool "$OCRD_TOOL_JSON" tool "$OCRD_TOOL_NAME" dump
}

# END-INCLUDE 
# BEGIN-INCLUDE ./src/usage.bash 
## ### `ocrd__usage`
## 
## Print usage
## 
ocrd__usage () {
    echo "
Usage: $OCRD_TOOL_NAME [OPTIONS]

`ocrd ocrd-tool "$OCRD_TOOL_JSON" tool "$OCRD_TOOL_NAME" description`

Options:
-l, --log-level [OFF|ERROR|WARN|INFO|DEBUG|TRACE]
                                Log level
-J, --dump-json                 Dump tool description as JSON and exit
-p, --parameter PATH
-g, --page-id TEXT              ID(s) of the physical page
-O, --output-file-grp TEXT      File group(s) used as output.
-I, --input-file-grp TEXT       File group(s) used as input.
-w, --working-dir TEXT          Working Directory
-m, --mets TEXT                 METS URL to validate  [required]
--help                          Show this message and exit.
-V, --version                   Show version.
    "
}

# END-INCLUDE 
# BEGIN-INCLUDE ./src/parse_argv.bash 
## ### `ocrd__parse_argv`
## 
## Expects an associative array ("hash"/"dict") `ocrd__argv` to be defined:
## 
## ```sh
## declare -A ocrd__argv=()
## ```
ocrd__parse_argv () {

    # if [[ -n "$ZSH_VERSION" ]];then
    #     print -r -- ${+ocrd__argv} ${(t)ocrd__argv}
    # fi
    if ! declare -p "ocrd__argv" >/dev/null 2>/dev/null ;then
        ocrd__raise "Must set \$ocrd__argv (declare -A ocrd__argv)"
    fi

    if ! declare -p "params" >/dev/null 2>/dev/null ;then
        ocrd__raise "Must set \$params (declare -A params)"
    fi

    while [[ "${1:-}" = -* ]];do
        case "$1" in
            -l|--log-level) ocrd__argv[log_level]=$2 ; shift ;;
            -h|--help|--usage) ocrd__usage; exit ;;
            -J|--dump-json) ocrd__dumpjson; exit ;;
            -p|--parameter) ocrd__argv[parameter]=$2 ; shift ;;
            -g|--page-id) ocrd__argv[page_id]=$2 ; shift ;;
            -O|--output-file-grp) ocrd__argv[output_file_grp]=$2 ; shift ;;
            -I|--input-file-grp) ocrd__argv[input_file_grp]=$2 ; shift ;;
            -w|--working-dir) ocrd__argv[working_dir]=$2 ; shift ;;
            -m|--mets-file) ocrd__argv[mets_file]=$2 ; shift ;;
            -V|--version) ocrd ocrd-tool "$OCRD_TOOL_JSON" version; exit ;;
            *) ocrd__raise "Unknown option '$1'" ;;
        esac
        shift
    done

    if [[ "${ocrd__argv[mets_file]:-}" = "" ]];then
        ocrd__raise "Option -m/--mets-file required"
    fi

    if [[ "${ocrd__argv[working_dir]:-}" = "" ]];then
        ocrd__argv[working_dir]=$(dirname "${ocrd__argv[mets_file]}")
    fi

    if [[ "${ocrd__argv[log_level]:-}" = "" ]];then
        ocrd__argv[log_level]="INFO"
    fi

    if [[ "${ocrd__argv[input_file_grp]:-}" = "" ]];then
        ocrd__argv[input_file_grp]="OCR-D-IMG"
    fi

    if [[ "${ocrd__argv[output_file_grp]:-}" = "" ]];then
        ocrd__argv[output_file_grp]="OCR-D-TEXT"
    fi

    local params_parsed retval
    params_parsed="$(ocrd ocrd-tool "$OCRD_TOOL_JSON" tool $OCRD_TOOL_NAME parse-params -p "${ocrd__argv[parameter]}")"
    retval=$?
    if [[ $retval != 0 ]];then
        echo "Error: Failed to parse parameters (retval $retval):"
        echo "$params_parsed"
        exit 42 # $retval
    fi
    eval "$params_parsed"

}

# END-INCLUDE 
# BEGIN-INCLUDE ./src/wrap.bash 
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

}

# END-INCLUDE 

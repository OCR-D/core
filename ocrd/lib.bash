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
-g, --group-id TEXT             mets:file GROUPID
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
## Expects an associative array ("hash"/"dict") `argv` to be defined:
## 
## ```sh
## declare -A argv
## ```
ocrd__parse_argv () {

    if ! declare -p "argv" >/dev/null 2>/dev/null ;then
        ocrd__raise "Must set \$argv (declare -A argv)"
    fi

    if ! declare -p "params" >/dev/null 2>/dev/null ;then
        ocrd__raise "Must set \$params (declare -A params)"
    fi


    while [[ "$1" = -* ]];do
        case "$1" in
            -l|--log-level) argv['log_level']=$2 ; shift ;;
            -h|--help|--usage) ocrd__usage; exit ;;
            -J|--dump-json) ocrd__dumpjson; exit ;;
            -p|--parameter) argv['parameter']=$2 ; shift ;;
            -g|--group-id) argv['group_id']=$2 ; shift ;;
            -O|--output-file-grp) argv['output_file_grp']=$2 ; shift ;;
            -I|--input-file-grp) argv['input_file_grp']=$2 ; shift ;;
            -w|--working-dir) argv['working_dir']=$2 ; shift ;;
            -m|--mets-file) argv['mets_file']=$2 ; shift ;;
            -V|--version) ocrd ocrd-tool "$OCRD_TOOL_JSON" version; exit ;;
            *) ocrd__raise "Unknown option '$1'" ;;
        esac
        shift
    done

    if [[ "${argv[mets_file]}" = "" ]];then
        ocrd__raise "Option -m/--mets-file required"
    fi

    if [[ "${argv[log_level]}" = "" ]];then
        argv[log_level]="INFO"
    fi

    if [[ "${argv[input_file_grp]}" = "" ]];then
        argv[input_file_grp]="OCR-D-IMG"
    fi

    if [[ "${argv[output_file_grp]}" = "" ]];then
        argv[output_file_grp]="OCR-D-TEXT"
    fi

    local params_parsed=$(ocrd ocrd-tool "$OCRD_TOOL_JSON" tool $OCRD_TOOL_NAME parse-params -p "${argv[parameter]}")
    if [[ $? != 0 ]];then
        echo "Error: Failed to parse parameters:"
        echo "$params_parsed"
        exit 42
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
    declare -Agx params argv

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

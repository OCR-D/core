ocrd__raise () {
    echo >&2 "ERROR: $1"; exit 127
}

if ! declare -p "OCRD_TOOL_JSON" 2>/dev/null;then
    ocrd_raise "Must set \$OCRD_TOOL_JSON"
fi

if ! declare -p "args" 2>/dev/null;then
    ocrd_raise "Must set \$OCRD_TOOL_JSON"
fi

ocrd__dumpjson () {
    cat "$OCRD_TOOL_JSON"
}

ocrd__usage () {
    echo "
    Usage: $0 [OPTIONS]

    Options:
    -l, --log-level [OFF|ERROR|WARN|INFO|DEBUG|TRACE]
    Log level
    -J, --dump-json                 Dump tool description as JSON and exit
    -p, --parameter PATH
    -o, --output-mets TEXT          METS URL to write resulting METS to
    -g, --group-id TEXT             mets:file GROUPID
    -O, --output-file-grp TEXT      File group(s) used as output.
    -I, --input-file-grp TEXT       File group(s) used as input.
    -w, --working-dir TEXT          Working Directory
    -m, --mets TEXT                 METS URL to validate  [required]
    --help                          Show this message and exit.
    "
}

## ## ocrd__parse_args
## 
## Expects an associative array ("hash"/"dict") `args` to be defined:
## 
## ```sh
## declare -A args
## ```
ocrd__parse_args () {

    while [[ "$1" = -* ]];do
        case "$1" in
            -l|--log-level) opts['log_level']=$2 ; shift ;;
            -J|--dump-json) ocrd__dumpjson ;;
            -p|--parameter) opts['parametger']=$2 ; shift ;;
            -o|--output-mets) opts['output_mets']=$2 ; shift ;;
            -g|--group-id) opts['group_id']=$2 ; shift ;;
            -O|--output-file-grp) opts['output_file_grp']=$2 ; shift ;;
            -I|--input-file-grp) opts['input_file_grp']=$2 ; shift ;;
            -w|--working-dir) opts['working_dir']=$2 ; shift ;;
            -m|--mets-file) opts['mets_file']=$2 ; shift ;;
            *) raise "Unknown option '$1'" ;;
        esac
        shift
    done

    if [[ "${opts[mets_file]}" = "" ]];then
        raise "Option -m/--mets-file required"
    fi
}

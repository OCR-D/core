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
            -p|--parameter) ocrd__argv[parameter]="$2" ; shift ;;
            -g|--page-id) ocrd__argv[page_id]=$2 ; shift ;;
            -O|--output-file-grp) ocrd__argv[output_file_grp]=$2 ; shift ;;
            -I|--input-file-grp) ocrd__argv[input_file_grp]=$2 ; shift ;;
            -w|--working-dir) ocrd__argv[working_dir]=$(realpath "$2") ; shift ;;
            -m|--mets) ocrd__argv[mets_file]=$(realpath "$2") ; shift ;;
            -V|--version) ocrd ocrd-tool "$OCRD_TOOL_JSON" version; exit ;;
            *) ocrd__raise "Unknown option '$1'" ;;
        esac
        shift
    done

    if [[ ! -r "${ocrd__argv[mets_file]:=$PWD/mets.xml}" ]];then
        ocrd__raise "METS '${ocrd__argv[mets_file]}' not readable. Use -m/--mets-file to set correctly"
    fi

    if [[ ! -d "${ocrd__argv[working_dir]:=$(dirname "${ocrd__argv[mets_file]}")}" ]];then
        ocrd__raise "workdir '${ocrd__argv[working_dir]}' not a directory. Use -w/--working-dir to set correctly"
    fi

    if [[ ! "${ocrd__argv[log_level]:=INFO}" =~ OFF|ERROR|WARN|INFO|DEBUG|TRACE ]];then
        ocrd__raise "log level '${ocrd__argv[log_level]}' is invalid"
    fi

    # if [[ ! "${ocrd__argv[input_file_grp]:=OCR-D-IMG}" =~ OCR-D-(GT-)?(IMG|SEG|OCR|COR)(-[A-Z0-9\-]{3,})?(,OCR-D-(GT-)?(IMG|SEG|OCR|COR)(-[A-Z0-9\-]{3,})?)* ]];then
    #     echo >&2 "WARNING: input fileGrp '${ocrd__argv[input_file_grp]}' does not conform to OCR-D spec"
    # fi

    # if [[ ! "${ocrd__argv[output_file_grp]:=OCR-D-OCR}" =~ OCR-D-(GT-)?(IMG|SEG|OCR|COR)(-[A-Z0-9\-]{3,})?(,OCR-D-(GT-)?(IMG|SEG|OCR|COR)(-[A-Z0-9\-]{3,})?)* ]];then
    #     echo >&2 "WARNING: output fileGrp '${ocrd__argv[output_file_grp]}' does not conform to OCR-D spec"
    # fi


    local params_parsed retval
    params_parsed="$(ocrd ocrd-tool "$OCRD_TOOL_JSON" tool $OCRD_TOOL_NAME parse-params -p "${ocrd__argv[parameter]:-{\}}")"
    retval=$?
    if [[ $retval != 0 ]];then
        echo "Error: Failed to parse parameters (retval $retval):"
        echo "$params_parsed"
        exit 42 # $retval
    fi
    eval "$params_parsed"

}


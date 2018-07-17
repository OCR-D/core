## ### `ocrd__parse_argv`
## 
## Expects an associative array ("hash"/"dict") `argv` to be defined:
## 
## ```sh
## declare -A argv=()
## ```
ocrd__parse_argv () {

    if ! declare -p "argv" >/dev/null 2>/dev/null ;then
        ocrd__raise "Must set \$argv (declare -A argv)"
    fi

    if ! declare -p "params" >/dev/null 2>/dev/null ;then
        ocrd__raise "Must set \$params (declare -A params)"
    fi

    while [[ "${1:-}" = -* ]];do
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

    if [[ "${argv[mets_file]:-}" = "" ]];then
        ocrd__raise "Option -m/--mets-file required"
    fi

    if [[ "${argv[working_dir]:-}" = "" ]];then
        argv[working_dir]=$(dirname "${argv[mets_file]}")
    fi

    if [[ "${argv[log_level]:-}" = "" ]];then
        argv[log_level]="INFO"
    fi

    if [[ "${argv[input_file_grp]:-}" = "" ]];then
        argv[input_file_grp]="OCR-D-IMG"
    fi

    if [[ "${argv[output_file_grp]:-}" = "" ]];then
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


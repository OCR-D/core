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

    if [[ $# = 0 ]];then
        ocrd__usage
        exit 1
    fi

    ocrd__argv[overwrite]=false
    ocrd__argv[mets_file]="$PWD/mets.xml"

    local __parameters=()
    local __parameter_overrides=()

    while [[ "${1:-}" = -* ]];do
        case "$1" in
            -l|--log-level) ocrd__argv[log_level]=$2 ; shift ;;
            -h|--help|--usage) ocrd__usage; exit ;;
            -J|--dump-json) ocrd__dumpjson; exit ;;
            -p|--parameter) __parameters+=(-p "$2") ; shift ;;
            -P|--parameter-override) __parameter_overrides+=(-P "$2" "$3") ; shift ; shift ;;
            -g|--page-id) ocrd__argv[page_id]=$2 ; shift ;;
            -O|--output-file-grp) ocrd__argv[output_file_grp]=$2 ; shift ;;
            -I|--input-file-grp) ocrd__argv[input_file_grp]=$2 ; shift ;;
            -w|--working-dir) ocrd__argv[working_dir]=$(realpath "$2") ; shift ;;
            -m|--mets) ocrd__argv[mets_file]=$(realpath "$2") ; shift ;;
            --overwrite) ocrd__argv[overwrite]=true ;;
            -V|--version) ocrd ocrd-tool "$OCRD_TOOL_JSON" version; exit ;;
            *) ocrd__raise "Unknown option '$1'" ;;
        esac
        shift
    done

    if [[ ! -e "${ocrd__argv[mets_file]}" ]];then
        ocrd__raise "METS file '${ocrd__argv[mets_file]}' not found"
    fi

    if [[ ! -d "${ocrd__argv[working_dir]:=$(dirname "${ocrd__argv[mets_file]}")}" ]];then
        ocrd__raise "workdir '${ocrd__argv[working_dir]}' not a directory. Use -w/--working-dir to set correctly"
    fi

    if [[ ! "${ocrd__argv[log_level]:=INFO}" =~ OFF|ERROR|WARN|INFO|DEBUG|TRACE ]];then
        ocrd__raise "log level '${ocrd__argv[log_level]}' is invalid"
    fi

    if [[ -z "${ocrd__argv[input_file_grp]:=}" ]];then
        ocrd__raise "Provide --input-file-grp/-I explicitly!"
    fi

    if [[ -z "${ocrd__argv[output_file_grp]:=}" ]];then
        ocrd__raise "Provide --output-file-grp/-O explicitly!"
    fi

    # check fileGrps
    local _valopts=( --workspace "${ocrd__argv[working_dir]}" )
    if [[ ${ocrd__argv[overwrite]} = true ]]; then
        _valopts+=( --overwrite )
    fi
    if [[ -n "${ocrd__argv[page_id]:-}" ]]; then
        _valopts+=( --page-id "${ocrd__argv[page_id]}" )
    fi
    _valopts+=( "${OCRD_TOOL_NAME#ocrd-} -I ${ocrd__argv[input_file_grp]} -O ${ocrd__argv[output_file_grp]}" )
    ocrd validate tasks "${_valopts[@]}" || exit $?

    # check parameters
    local params_parsed retval
    params_parsed="$(ocrd ocrd-tool "$OCRD_TOOL_JSON" tool $OCRD_TOOL_NAME parse-params "${__parameters[@]}" "${__parameter_overrides[@]}")" || {
        retval=$?
        ocrd__raise "Failed to parse parameters (retval $retval):
$params_parsed"
    }
    eval "$params_parsed"

}


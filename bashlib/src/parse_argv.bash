## ### `ocrd__parse_argv`
## 
## Expects an associative array ("hash"/"dict") `argv` to be defined:
## 
## ```sh
## declare -A argv
## ```
ocrd__parse_argv () {

    while [[ "$1" = -* ]];do
        case "$1" in
            -l|--log-level) argv['log_level']=$2 ; shift ;;
            -J|--dump-json) ocrd__dumpjson ;;
            -p|--parameter) argv['parameter']=$2 ; shift ;;
            -o|--output-mets) argv['output_mets']=$2 ; shift ;;
            -g|--group-id) argv['group_id']=$2 ; shift ;;
            -O|--output-file-grp) argv['output_file_grp']=$2 ; shift ;;
            -I|--input-file-grp) argv['input_file_grp']=$2 ; shift ;;
            -w|--working-dir) argv['working_dir']=$2 ; shift ;;
            -m|--mets-file) argv['mets_file']=$2 ; shift ;;
            *) ocrd__raise "Unknown option '$1'" ;;
        esac
        shift
    done

    if [[ "${argv[mets_file]}" = "" ]];then
        ocrd__raise "Option -m/--mets-file required"
    fi
}


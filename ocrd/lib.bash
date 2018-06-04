# BEGIN-INCLUDE ./src/util.bash 
## ### `ocrd__raise`
## 
## Raise an error and exit
ocrd__raise () {
    echo >&2 "ERROR: $1"; exit 127
}

# END-INCLUDE 
# BEGIN-INCLUDE ./src/dumpjson.bash 
## ### `ocrd__dumpjson`
## 
## Output ocrd-tool.json.
## 
## Requires `$OCRD_TOOL_JSON` to be set:
## 
## ```sh
## export OCRD_TOOL_JSON=/path/to/ocrd-tool.json
## ```
## 
ocrd__dumpjson () {
    cat "$OCRD_TOOL_JSON"
}

# END-INCLUDE 
# BEGIN-INCLUDE ./src/usage.bash 
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

    if [[ "${argv[working_dir]}" = "" ]];then
        argv[working_dir]="$PWD"
    fi
}

# END-INCLUDE 

if ! which "ocrd" >/dev/null 2>/dev/null;then
    ocrd__raise "ocrd not in \$PATH"
fi

if ! declare -p "OCRD_TOOL_JSON" >/dev/null 2>/dev/null;then
    ocrd__raise "Must set \$OCRD_TOOL_JSON"
elif [[ ! -r "$OCRD_TOOL_JSON" ]];then
    ocrd__raise "Cannot read \$OCRD_TOOL_JSON: $OCRD_TOOL_JSON"
fi

if ! declare -p "argv" >/dev/null 2>/dev/null ;then
    ocrd__raise "Must set \$argv"
fi


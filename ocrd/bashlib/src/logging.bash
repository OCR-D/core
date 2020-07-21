## ### `ocrd__raise`
## 
## Raise an error and exit.
ocrd__raise () {
    echo >&2 "ERROR: $1"; exit 127
}

## ### `ocrd__log`
## 
## Delegate logging to `ocrd log`
ocrd__log () {
    local log_level="${ocrd__argv[log_level]:-}"
    if [[ -n "$log_level" ]];then
        ocrd -l "$log_level" log "$@"
    else
        ocrd log "$@"
    fi
}


## ### `ocrd__minversion`
## 
## Ensure minimum version
# ht https://stackoverflow.com/posts/4025065
ocrd__minversion () {
    local minversion="$1"
    local version=$(ocrd --version|sed 's/ocrd, version //')
    echo "$minversion < $version?"
    if [[ $minversion == $version ]];then
        return 0
    fi
    local IFS=.
    version=($version)
    minversion=($minversion)
    # fill empty fields in version with zeros
    for ((i=${#version[@]}; i<${#minversion[@]}; i++));do
        version[i]=0
    done
    for ((i=0; i<${#version[@]}; i++));do
        if [[ -z ${minversion[i]} ]];then
            # fill empty fields in minversion with zeros
            minversion[i]=0
        fi
        if ((10#${version[i]} < 10#${minversion[i]}));then
            ocrd__raise "ocrd/core is too old (${version[*]} < ${minversion[*]}). Please update OCR-D/core"
        fi
    done
}

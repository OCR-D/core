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
    #echo "$minversion < $version?"
    local IFS=.
    version=($version)
    minversion=($minversion)
    # MAJOR > MAJOR
    if (( ${version[0]} > ${minversion[0]} ));then
        return
    # MAJOR == MAJOR
    elif (( ${version[0]} == ${minversion[0]} ));then
        # MINOR > MINOR
        if (( ${version[1]} > ${minversion[1]} ));then
            return
        # MINOR == MINOR
        elif (( ${version[1]} == ${minversion[1]} ));then
            # PATCH > PATCH
            if (( ${version[2]} >= ${minversion[2]} ));then
                return
            fi
        fi
    fi
    ocrd__raise "ocrd/core is too old (${version[*]} < ${minversion[*]}). Please update OCR-D/core"
}

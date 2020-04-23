## ### `ocrd__raise`
## 
## Raise an error and exit.
ocrd__raise () {
    echo >&2 "ERROR: $1"; exit 127
}

## ### `ocrd__log`
## 
## Log an error message.
## Arguments: [`loglevel`, `message`] or just [`message`] (default level DEBUG)
ocrd__scriptname="${0##*/}"
ocrd__log () {
    local loglevel timestamp;
    if [ $# -gt 1 ];then
        loglevel=$1 ; shift
    else
        loglevel='DEBUG'
    fi
    timestamp="$(date +'%T.%3N')"
    echo >&2 "$timestamp $loglevel $ocrd__scriptname - $*"
}

## ### `ocrd__error`
## ### `ocrd__warning`
## ### `ocrd__info`
## ### `ocrd__debug`
## ### `ocrd__trace`
## 
## Log an error/warning/info/debug/trace message.
ocrd__error () { ocrd__log ERROR "$1"; }
ocrd__warning () { ocrd__log WARNING "$1"; }
ocrd__info () { ocrd__log INFO "$1"; }
ocrd__debug () { ocrd__log DEBUG "$1"; }
ocrd__trace () { ocrd__log TRACE "$1"; }

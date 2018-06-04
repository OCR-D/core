## ### `ocrd__raise`
## 
## Raise an error and exit
ocrd__raise () {
    echo >&2 "ERROR: $1"; exit 127
}

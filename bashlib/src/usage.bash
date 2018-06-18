## ### `ocrd__usage`
## 
## Print usage
## 
ocrd__usage () {
    echo "
Usage: $OCRD_TOOL_NAME [OPTIONS]

`ocrd ocrd-tool "$OCRD_TOOL_JSON" tool "$OCRD_TOOL_NAME" description`

Options:
-l, --log-level [OFF|ERROR|WARN|INFO|DEBUG|TRACE]
                                Log level
-J, --dump-json                 Dump tool description as JSON and exit
-p, --parameter PATH
-g, --group-id TEXT             mets:file GROUPID
-O, --output-file-grp TEXT      File group(s) used as output.
-I, --input-file-grp TEXT       File group(s) used as input.
-w, --working-dir TEXT          Working Directory
-m, --mets TEXT                 METS URL to validate  [required]
--help                          Show this message and exit.
    "
}



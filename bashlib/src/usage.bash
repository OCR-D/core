## ### `ocrd__usage`
## 
## Print usage
## 
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



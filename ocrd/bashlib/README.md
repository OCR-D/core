# bash library

Builds a bash script that can be sourced by other bash scripts to create OCRD-compliant CLI.

<!-- BEGIN-MARKDOWN-TOC -->
* [Building](#building)
* [API](#api)
	* [`ocrd__raise`](#ocrd__raise)
	* [`ocrd__dumpjson`](#ocrd__dumpjson)
	* [`ocrd__parse_argv`](#ocrd__parse_argv)

<!-- END-MARKDOWN-TOC -->

## Building

```sh
make lib.bash
```

## API

<!-- BEGIN-RENDER ./lib.bash -->
### `ocrd__raise`

Raise an error and exit
### `ocrd__dumpjson`

Output ocrd-tool.json.

Requires `$OCRD_TOOL_JSON` to be set:

```sh
export OCRD_TOOL_JSON=/path/to/ocrd-tool.json
```

### `ocrd__parse_argv`

Expects an associative array ("hash"/"dict") `args` to be defined:

```sh
declare -A args=()
```

<!-- END-RENDER -->

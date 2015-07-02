# getopts

Sets silent mode, otherwise `getop()` prints an error message for invalid options

    OPTERR=0

#### Specifying Required Options and Required Arguments
* `:` before - Option is required
* `:` after  - Option requires an argument

#### Case Options
* \?) - Wrong option
* :) - Missing argument

## Examples

#### Example 1

Basic usage of `getopts`
```bash
while getopts "hrdn" OPT ; do
  case $OPT in
    h) echo -e "$USAGE" && exit 0 ;;
    r) echo "remove" ;;
    d) echo "download" ;;
    n) echo "new" ;;
    \?) echo "wrong option -${OPTARG}" ;;
  esac
done
```

#### Example 2

Here we are using `getopts` with one of the options being a list separated by commas.

```bash
script.sh -t [type] -e [email] -a [app] -s [123,124,125]
```

```bash
while getopts "t:e:a:s:h" OPT ; do
  case $OPT in
        t) TYPE="$OPTARG" ;;
        e) EMAIL_ADDRS="$OPTARG" ;;
        a) APP="$OPTARG" ;;
        s) SDN_LIST="$OPTARG"
           SDN_LIST_SPACE=$(echo "$SDN_LIST" | tr ',' ' ')
           ;;
        h) echo -e "$USAGE" && exit 0 ;;
        \?) echo "Wrong option -${OPTARG}" ;;
        :) echo "Missing argument for $OPTARG" ;;
  esac
done
```
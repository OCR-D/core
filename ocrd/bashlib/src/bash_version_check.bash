((BASH_VERSINFO<4 || BASH_VERSINFO==4 && BASH_VERSINFO[1]<4)) && \
    echo >&2 "bash $BASH_VERSION is too old. Please install bash 4.4 or newer." && \
    exit 1


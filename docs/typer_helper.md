# TrackerUtils

**Usage**:

```console
$ tu [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`: Show version and exit.
* `--rich-output / --plain-output`: Use rich output  [default: rich-output]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `test`: Test trackers
* `client-test`: Test Trackers by a qbittorrent client
* `set-trackers`: Set trackers for qbittorrent client

## `tu test`

Test trackers

**Usage**:

```console
$ tu test [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-u, --tracker-provider-urls TEXT`: Tracker provider urls
* `-f, --tracker-provider-file PATH`: Tracker provider file
* `-o, --output-txt-dir PATH`: Output directory for txt files
* `--output-json-path PATH`: Output path for json file
* `--format-json / --no-format-json`: Format json file  [default: no-format-json]
* `--sort / --no-sort`: Sort output data  [default: sort]
* `--show-failed`: Show failed tasks
* `--rich-output / --plain-output`: Use rich output  [default: rich-output]
* `-r, --retry-times INTEGER`: Retry times for failed tasks  [default: 3]
* `-t, --timeout TIMEDELTA`: Timeout for each task  [default: 10s]
* `--help`: Show this message and exit.

## `tu client-test`

Test Trackers by a qbittorrent client

**Usage**:

```console
$ tu client-test [OPTIONS] URL TORRENT COMMAND [ARGS]...
```

**Arguments**:

* `URL`: Url of the qbittorrent web ui  [required]
* `TORRENT`: Torrent name or hash  [required]

**Options**:

* `-o, --output-path PATH`: Path to the output file  [required]
* `-t, --trackers-urls TEXT`: List of trackers urls
* `-f, --tackers-file PATH`: Path to the file containing trackers
* `-u, --username TEXT`: Username for the qbittorrent client  [env var: QBITTORRENT_USERNAME]
* `-p, --password TEXT`: Password for the qbittorrent client  [env var: QBITTORRENT_PASSWORD]
* `-F, --fast-mode`: Connection failure if tracker is updating with errors in Fast mode
* `-i, --polling-interval TIMEDELTA`: Interval in seconds between tracker contact attempts  [default: 100ms]
* `-y, --yes-all`: Answer yes to all prompts
* `--show-failed`: Show failed tasks
* `--rich-output / --plain-output`: Use rich output  [default: rich-output]
* `-t, --timeout TIMEDELTA`: Timeout for contact all trackers  [default: 5m]
* `--help`: Show this message and exit.

## `tu set-trackers`

Set trackers for qbittorrent client

**Usage**:

```console
$ tu set-trackers [OPTIONS] URL COMMAND [ARGS]...
```

**Arguments**:

* `URL`: Url of the qbittorrent web ui  [required]

**Options**:

* `-u, --username TEXT`: Username for the qbittorrent client  [env var: QBITTORRENT_USERNAME]
* `-p, --password TEXT`: Password for the qbittorrent client  [env var: QBITTORRENT_PASSWORD]
* `-t, --trackers-urls TEXT`: List of trackers urls
* `-f, --tackers-file PATH`: Path to the file containing trackers
* `-a, --append`: Append trackers to existing trackers
* `--help`: Show this message and exit.

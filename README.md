# TrackerUtils

A Python CLI tool for testing trackers

## Usage

### Test trackers
```bash
tu test [OPTIONS]
```                                                                                      

#### Options
| Option                    | Short | Close            | Type    | Description                                    |
| ------------------------- | ----- | ---------------- | ------- | ---------------------------------------------- |
| │ --tracker-provider-urls | -u    |                  | TEXT    | Tracker provider urls                          |
| │ --tracker-provider-file | -f    |                  | PATH    | Tracker provider file [default: None]          |
| │ --output-txt-dir        | -o    |                  | PATH    | Output directory for txt files [default: None] |
| │ --output-json-path      |       |                  | PATH    | Output path for json file [default: None]      |
| │ --format-json           |       | --no-format-json |         | Format json file [default: no-format-json]     |
| │ --sort                  |       | --no-sort        |         | Sort output data [default: sort]               |
| │ --show-failed           |       |                  |         | Show failed tasks                              |
| │ --retry-times           | -r    |                  | INTEGER | Retry times for failed tasks [default: 3]      |
| │ --timeout               | -t    |                  | FLOAT   | Timeout for each task [default: 10.0]          |

### Test trackers by qbittorrent web api
```bash
tu client-test [OPTIONS] URL TORRENT
```

#### Arguments
| Argument     | type | Description                                              |
| ------------ | ---- | -------------------------------------------------------- |
| *    url     | TEXT | Url of the qbittorrent web ui [default: None] [required] |
| *    torrent | TEXT | Torrent name or hash [default: None] [required]          |

#### Options
| Option             | Short | Close       | Type  | Description                                                                             |
| ------------------ | ----- | ----------- | ----- | --------------------------------------------------------------------------------------- |
| --trackers-urls    | -t    |             | TEXT  | List of trackers urls                                                                   |
| --tackers-file     | -f    |             | PATH  | Path to the file containing trackers [default: None]                                    |
| --username         | -u    |             | TEXT  | Username for the qbittorrent client [env var: QBITTORRENT_USERNAME] [default: None]     |
| --password         | -p    |             | TEXT  | Password for the qbittorrent client [env var: QBITTORRENT_PASSWORD] [default: None]     |
| --output-path      | -o    |             | PATH  | Path to the output file [default: None]                                                 |
| --fast-mode        |       | --slow-mode |       | Connection failure if tracker is updating with errors in Fast mode [default: slow-mode] |
| --polling-interval | -i    |             | FLOAT | Interval in seconds between tracker contact attempts [default: 3.0]                     |
| --show-failed      |       |             |       | Show failed tasks                                                                       |
| --timeout          | -t    |             | FLOAT | Timeout in seconds for all trackers [default: 1800.0]                                   |
| --help             |       |             |       | Show this message and exit.                                                             |
# TrackerUtils

A Python CLI tool for testing trackers powered by [typer](https://github.com/fastapi/typer)

[English](README.md) | [中文](README_zh-cn.md)

## Usage

### Test trackers
```bash
tu test [OPTIONS]
```                                                                                      

#### Options
| Option                  | Short | Off              | Type      | Description                                    |
| ----------------------- | ----- | ---------------- | --------- | ---------------------------------------------- |
| --tracker-provider-urls | -u    |                  | TEXT      | Tracker provider urls                          |
| --tracker-provider-file | -f    |                  | PATH      | Tracker provider file [default: None]          |
| --output-txt-dir        | -o    |                  | PATH      | Output directory for txt files [default: None] |
| --output-json-path      |       |                  | PATH      | Output path for json file [default: None]      |
| --format-json           |       | --no-format-json |           | Format json file [default: no-format-json]     |
| --sort                  |       | --no-sort        |           | Sort output data [default: sort]               |
| --show-failed           |       |                  |           | Show failed tasks                              |
| --retry-times           | -r    |                  | TIMEDELTA | Retry times for failed tasks [default: 3]      |
| --timeout               | -t    |                  | FLOAT     | Timeout for each task [default: 10s]           |

### Test trackers by qbittorrent web api
```bash
tu client-test [OPTIONS] URL TORRENT
```

#### Arguments
| Argument  | type | Description                                              |
| --------- | ---- | -------------------------------------------------------- |
| * url     | TEXT | Url of the qbittorrent web ui [default: None] [required] |
| * torrent | TEXT | Torrent name or hash [default: None] [required]          |

#### Options
| Option             | Short | Off         | Type      | Description                                                                             |
| ------------------ | ----- | ----------- | --------- | --------------------------------------------------------------------------------------- |
| --trackers-urls    | -t    |             | TEXT      | List of trackers urls                                                                   |
| --tackers-file     | -f    |             | PATH      | Path to the file containing trackers [default: None]                                    |
| --username         | -u    |             | TEXT      | Username for the qbittorrent client [env var: QBITTORRENT_USERNAME] [default: None]     |
| --password         | -p    |             | TEXT      | Password for the qbittorrent client [env var: QBITTORRENT_PASSWORD] [default: None]     |
| --output-path      | -o    |             | PATH      | Path to the output file [default: None] [required]                                      |
| --fast-mode        |       | --slow-mode |           | Connection failure if tracker is updating with errors in Fast mode [default: slow-mode] |
| --polling-interval | -i    |             | TIMEDELTA | Interval in seconds between tracker contact attempts [default: 100ms]                   |
| --yes-all          | -y    |             |           | Answer yes to all prompts                                                               |
| --show-failed      |       |             |           | Show failed tasks                                                                       |
| --timeout          | -t    |             | TIMEDELTA | Timeout in seconds for all trackers [default: 5m]                                       |
| --help             |       |             |           | Show this message and exit.                                                             |

### Set Trackers for qbittorrent client
```bash
tu set-trackers [OPTIONS] URL
```

#### Arguments
| Argument | type | Description                                              |
| -------- | ---- | -------------------------------------------------------- |
| * url    | TEXT | Url of the qbittorrent web ui [default: None] [required] |

#### Options
| Option          | Short | Type | Description                                                                         |
| --------------- | ----- | ---- | ----------------------------------------------------------------------------------- |
| --username      | -u    | TEXT | Username for the qbittorrent client [env var: QBITTORRENT_USERNAME] [default: None] |
| --password      | -p    | TEXT | Password for the qbittorrent client [env var: QBITTORRENT_PASSWORD] [default: None] |
| --trackers-urls | -t    | TEXT | List of trackers urls                                                               |
| --tackers-file  | -f    | PATH | Path to the file containing trackers [default: None]                                |
| --append        | -a    |      | Append trackers to existing trackers                                                |
| --help          |       |      | Show this message and exit.                                                         |

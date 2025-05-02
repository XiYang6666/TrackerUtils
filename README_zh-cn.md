# TrackerUtils

一个基于 [typer](https://github.com/fastapi/typer) 的 Python CLI 工具，用于测试 tracker

[English](README.md) | [中文](README_zh-cn.md)

## 使用说明

### 测试 tracker
```bash
tu test [选项]
```

#### 选项
| 选项                    | 简写 | 关闭选项         | 类型      | 描述                              |
| ----------------------- | ---- | ---------------- | --------- | --------------------------------- |
| --tracker-provider-urls | -u   |                  | TEXT      | Tracker 列表的 URLs               |
| --tracker-provider-file | -f   |                  | PATH      | Tracker 列表文件 [默认: 无]       |
| --output-txt-dir        | -o   |                  | PATH      | 输出 txt 文件的目录 [默认: 无]    |
| --output-json-path      |      |                  | PATH      | 输出 json 文件的路径 [默认: 无]   |
| --format-json           |      | --no-format-json |           | 格式化 json 文件 [默认: 不格式化] |
| --sort                  |      | --no-sort        |           | 对输出数据排序 [默认: 启用排序]   |
| --show-failed           |      |                  |           | 显示失败的任务                    |
| --retry-times           | -r   |                  | TIMEDELTA | 失败任务重试次数 [默认: 3]        |
| --timeout               | -t   |                  | FLOAT     | 单任务超时时间（秒）[默认: 10s]   |

### 通过 qBittorrent Web API 测试 tracker
```bash
tu client-test [选项] URL TORRENT
```

#### 参数
| 参数      | 类型 | 描述                                       |
| --------- | ---- | ------------------------------------------ |
| * url     | TEXT | qBittorrent Web 界面 URL [默认: 无] [必填] |
| * torrent | TEXT | 种子名称或哈希值 [默认: 无] [必填]         |

#### 选项
| 选项               | 简写 | 关闭选项    | 类型      | 描述                                                           |
| ------------------ | ---- | ----------- | --------- | -------------------------------------------------------------- |
| --trackers-urls    | -t   |             | TEXT      | Tracker URLs 列表                                              |
| --tackers-file     | -f   |             | PATH      | Tracker 列表文件路径 [默认: 无]                                |
| --username         | -u   |             | TEXT      | qBittorrent 用户名 [环境变量: QBITTORRENT_USERNAME] [默认: 无] |
| --password         | -p   |             | TEXT      | qBittorrent 密码 [环境变量: QBITTORRENT_PASSWORD] [默认: 无]   |
| --output-path      | -o   |             | PATH      | 结果输出路径 [默认: 无]                                        |
| --fast-mode        |      | --slow-mode |           | 快速模式下 tracker 更新报错视为连接失败 [默认: 慢速模式]       |
| --polling-interval | -i   |             | TIMEDELTA | 尝试联系 tracker 的时间间隔（秒）[默认: 100ms]                 |
| --yes-all          | -y   |             |           | 跳过所有确认提示                                               |
| --show-failed      |      |             |           | 显示失败任务                                                   |
| --timeout          | -t   |             | TIMEDELTA | 总超时时间（秒）[默认: 5m]                                     |
| --help             |      |             |           | 显示帮助信息                                                   |

### 为 qBittorrent 客户端设置 tracker
```bash
tu set-trackers [选项] URL
```

#### 参数
| 参数  | 类型 | 描述                                       |
| ----- | ---- | ------------------------------------------ |
| * url | TEXT | qBittorrent Web 界面 URL [默认: 无] [必填] |

#### 选项
| 选项            | 简写 | 类型 | 描述                                                           |
| --------------- | ---- | ---- | -------------------------------------------------------------- |
| --username      | -u   | TEXT | qBittorrent 用户名 [环境变量: QBITTORRENT_USERNAME] [默认: 无] |
| --password      | -p   | TEXT | qBittorrent 密码 [环境变量: QBITTORRENT_PASSWORD] [默认: 无]   |
| --trackers-urls | -t   | TEXT | Tracker URLs 列表                                              |
| --tackers-file  | -f   | PATH | Tracker 列表文件路径 [默认: 无]                                |
| --help          |      |      | 显示帮助信息                                                   |

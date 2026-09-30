# Field Ledger

Field Ledger 是一个使用 Python 标准库和 SQLite 的观测记录命令行工具。它保存导入修订，列出当前记录，并按日期和分类汇总。需要 Python 3.11 或以上版本，无需安装依赖。

在本目录运行：

```console
python -m fieldledger --db observations.sqlite import examples/demo.csv --json
python -m fieldledger --db observations.sqlite list --json
python -m fieldledger --db observations.sqlite report --from 2026-01-01 --to 2026-01-31 --category rain --json
python -m unittest discover -s tests -v
```

省略 `--json` 可查看文本输出。`--db` 放在子命令之前，默认使用当前目录的 `observations.sqlite`；数据库的父目录须已存在。查询不存在的数据库会返回空结果，不创建文件。

CSV 的必需列是 `source,external_id,day,category,value`，可选列为 `note`。字段首尾空白会被去掉。`source` 和 `external_id` 共同确定记录身份；重复导入相同内容不会增加修订。改变值、日期、分类或备注会追加一个完整版本。额外具名列被忽略。

导入结果包含新增、更新、未变化和无效行的数量，以及无效行诊断。退出码 `0` 表示成功，`1` 表示存在被跳过的无效行，`2` 表示输入或执行失败。有无效行时，其余有效行仍会在同一次事务中提交。缺列、重复列名或文件读取失败不会创建或更改数据库。

日期范围包含两个端点；分类精确匹配。统计从每条记录的最新版本出发，所有总数和分组使用相同的筛选结果。完整规则见 [数据约定](docs/data-contract.md)，内部职责见 [架构说明](docs/architecture.md)。

`examples/incident/initial.csv` 和 `corrections.csv` 展示分批提交观测及后续更正：

```console
python -m fieldledger --db incident.sqlite import examples/incident/initial.csv --json
python -m fieldledger --db incident.sqlite report --from 2026-01-01 --to 2026-01-31 --json
python -m fieldledger --db incident.sqlite import examples/incident/corrections.csv --json
python -m fieldledger --db incident.sqlite report --from 2026-01-01 --to 2026-01-31 --json
```

首次导入后，一月包含 4 条当前记录，总值为 25；更正后，一月包含 3 条当前记录，总值为 24。

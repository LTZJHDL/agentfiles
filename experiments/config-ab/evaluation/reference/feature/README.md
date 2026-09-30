# Field Ledger

Field Ledger 用 CSV 导入观测记录，保留修订历史，并查询和统计每条记录的当前版本。需要 Python 3.11 或以上版本，无需安装依赖。从本目录运行以下命令。

先预览，确认新增、更新、未变化和无效行的数量：

```text
python -m fieldledger --db observations.sqlite import observations.csv --dry-run
python -m fieldledger --db observations.sqlite import observations.csv --dry-run --json
```

预览不会保存任何修订，也不会创建数据库或其父目录。JSON 预览包含 `dry_run: true`。检查行级错误后，移除 `--dry-run` 即可正式导入：

```text
python -m fieldledger --db observations.sqlite import observations.csv
python -m fieldledger --db observations.sqlite list --json
python -m fieldledger --db observations.sqlite report --from 2026-01-01 --to 2026-01-31 --category rain --json
python -m fieldledger import --help
```

正式导入前需确保数据库父目录已存在。同一文件里的重复标识按行顺序判断变化。没有外部修改时，预览与随后的正式导入给出相同的四项计数和行级错误。预览不锁定未来的数据库状态；此工具用于没有并发写入的本地场景。

退出码为 0 表示所有行有效；1 表示存在无效行，正式导入仍会保存有效行；2 表示文件、数据库或命令错误。修复输入后应重新预览。CSV 必需列为 `source,external_id,day,category,value`，`note` 可选。完整规则见 [数据约定](docs/data-contract.md)。

运行测试：

```text
python -m unittest discover -s tests -v
```

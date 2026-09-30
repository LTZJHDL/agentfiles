这个观测数据工具的统计结果有时与记录列表不一致。请调查并修复，保留相关回归测试，并在最后解释原因、影响范围和验证结果。既有命令接口和数据约定见 `docs/data-contract.md`。

本机使用 Windows PowerShell，Python 可执行文件为 `C:\Users\LTZJH\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`，通过 `&` 调用即可，无需安装依赖。文档中的 `python` 指这个解释器。

用户的复现步骤如下，请使用一个新的临时数据库：

```text
python -m fieldledger --db incident.sqlite import examples/incident/initial.csv --json
python -m fieldledger --db incident.sqlite report --from 2026-01-01 --to 2026-01-31 --json
python -m fieldledger --db incident.sqlite import examples/incident/corrections.csv --json
python -m fieldledger --db incident.sqlite list --json
python -m fieldledger --db incident.sqlite report --from 2026-01-01 --to 2026-01-31 --json
```

用户核对原始数据后认为：第一次导入后的 1 月统计应该是 4 条、合计 25；修订后应为 3 条、合计 24，而且修订后的 `list` 看起来是正确的。请核实这些观察，修正导致不一致的原因，并检查日期端点、分类过滤和不限定日期的统计是否也受影响。修复不应通过改动或丢弃用户的记录、修订历史来让数值对上。

# Field Ledger 数据约定

Field Ledger 整理来自多个来源的观测记录。导入会保留修订历史；查询和统计呈现每条记录的当前版本。

## 记录与修订

记录由 `(source, external_id)` 共同标识。不同来源可以使用相同编号。两者均为去掉首尾空白后的非空文本，区分大小写，不限制分隔符或 Unicode 字符。

每个版本包含 `source`、`external_id`、`day`、`category`、`value` 和 `note`。`day` 是严格的 `YYYY-MM-DD` 格式及有效日历日期；`category` 是去掉首尾空白后的非空文本；`value` 是十进制整数，范围为 -1000000000 到 1000000000；`note` 是去掉首尾空白后的文本，省略时为空字符串。其他文本字段也去掉首尾空白。

首次出现的记录为新增。同一标识的内容发生变化时追加修订，日期和分类也可以改变。全部内容相同的记录为未变化，不追加修订。修订的先后由导入顺序确定，与观测日期无关。

## CSV 导入

UTF-8 CSV（允许 BOM）必须包含 `source,external_id,day,category,value` 列，可以包含 `note` 列及其他具名列；额外具名列被忽略。缺少必需列、重复列名或无法读取的文件属于整份输入错误，退出码为 2，并在 stderr 解释原因；这类错误不创建或改变数据库。

数据行缺失必需值、格式错误，或者比表头多出字段时，跳过该行并记录诊断。有效行按文件顺序处理，包括同一文件中多次出现的同一标识。后续行相对于前面有效行处理后的状态判断新增、更新或未变化。所有有效行在一次事务中提交。

导入摘要的 JSON 对象包含 `inserted`、`updated`、`unchanged`、`invalid` 四个计数，以及 `errors` 数组。每条错误包含 `row` 和非空的 `message`。`row` 按 CSV 记录计数，从表头后的 2 开始，不是含换行字段的物理行号。没有无效行时退出码为 0，有无效行时为 1；有效行仍然导入。人类可读输出表达同样的信息。

## 查询与统计

`list --json` 返回当前记录组成的 JSON 数组，每项恰好包含上述六个字段，按 `(source, external_id)` 排序。历史版本不重复出现在列表里。

统计先确定每个标识的最新修订，再按日期和分类过滤当前记录。`--from` 和 `--to` 均包含端点，省略时不设对应边界；`--category` 精确匹配分类。起止日期非法或起点晚于终点时，退出码为 2。

`report --json` 返回 `count`、`total` 和 `groups`。`count` 是当前记录数，`total` 是当前记录的整数值之和。`groups` 按 `(day, category)` 排序，每组包含 `day`、`category`、`count`、`total`。空结果为 `{"count": 0, "total": 0, "groups": []}`。所有总数与分组都使用相同的筛选结果。

## 命令接口

从项目根目录运行 Python 3.11 或以上版本，无需安装依赖：

```text
python -m fieldledger --db observations.sqlite import observations.csv --json
python -m fieldledger --db observations.sqlite list --json
python -m fieldledger --db observations.sqlite report --from 2026-01-01 --to 2026-01-31 --category rain --json
python -m unittest discover -s tests -v
```

`--db` 是主命令选项。JSON 模式的 stdout 只包含一个 JSON 值；说明及失败诊断使用 stderr。正常使用中数据库父目录应已存在，首次导入可以创建数据库。`list` 和 `report` 查询不存在的数据库时返回空结果，不创建文件。

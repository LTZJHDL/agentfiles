# Codex 整套配置 A/B 实验

本实验比较旧配置 A 与候选配置 B 在两项真实开发任务上的交付质量、耗时和消耗。每个任务、每个配置使用一个独立的新会话和干净项目副本，第一轮共四次运行。这里保存实验材料；正式运行产生的成果另行记录。

两项任务分别是为 Field Ledger 增加导入预览，以及修复统计与当前记录不一致的问题。项目使用 Python 标准库和 SQLite，不需要联网或安装依赖。任务要求位于 [功能 prompt](tasks/feature.md) 和 [缺陷 prompt](tasks/bug.md)。对被测会话只粘贴对应 prompt 的正文。

## 开始前

两组配置快照在 [configs](configs/README.md)。本轮统一使用主模型 `gpt-6-astra xhigh`、Standard 速度、最多 10 个并发子 agent。快照保存的是文件内容，不能证明新会话已经加载它们；开始计时前，在单独的配置检查会话中核对实际可调用的角色。主模型在界面中确认，不从候选仓库的主模型默认值推断。

快照只覆盖 AGENTS.md、角色文件和相关代理设置。不要用候选仓库的整份 config.toml 覆盖实际配置。两组之间，工具、skills、权限、应用版本和项目上级目录的指令保持一致。正式运行期间避免其他任务消耗同一账户额度。

## 生成四个工作副本

下面的 PowerShell 命令使用本机已提供的 Python。`$Runs` 可以换成空闲目录，但不要放在基准项目或参考答案中。生成器会为每个副本初始化独立 Git 仓库并提交起始代码，已有目标目录或记录文件会使命令停止。

```powershell
$Py = 'C:\Users\LTZJH\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$Bench = 'C:\share_workspace\agentfiles\experiments\config-ab'
$Runs = 'C:\share_workspace\config-ab-runs'
& $Py "$Bench\prepare.py" --task feature --condition A --run-id feature-A-1 --dest "$Runs\run-01"
& $Py "$Bench\prepare.py" --task bug --condition A --run-id bug-A-1 --dest "$Runs\run-02"
& $Py "$Bench\prepare.py" --task feature --condition B --run-id feature-B-1 --dest "$Runs\run-03"
& $Py "$Bench\prepare.py" --task bug --condition B --run-id bug-B-1 --dest "$Runs\run-04"
```

生成器不切换 Codex 配置。四个目录可以提前生成；目录名使用中性的运行编号，A/B 标签和运行记录留在项目外。项目内只有正常的代码、示例、文档和测试，相同任务的 A/B 副本内容一致。配置快照和任务内容的版本指纹在 `freeze.json` 中，用来发现准备期间发生的意外变化。

| 工作目录 | 运行记录 | 配置 | 任务 |
| --- | --- | --- | --- |
| run-01 | feature-A-1.json | A | 功能 |
| run-02 | bug-A-1.json | A | 缺陷 |
| run-03 | feature-B-1.json | B | 功能 |
| run-04 | bug-B-1.json | B | 缺陷 |

## 运行一轮

1. 使用当前旧配置，在 Codex 中打开 `run-01` 目录，创建新会话。把实际模型、effort、速度、应用版本及可见角色填入 `local-runs/records/feature-A-1.json` 的 `runtime`，核对后将 `configuration_verified` 改为 `true`。
2. 记录开始时间与账户额度，粘贴 [功能 prompt](tasks/feature.md) 的正文。让 agent 自主完成任务。不要把本实验说明、角色偏好或参考答案放进会话。
3. agent 宣告完成且相关子 agent 已结束后，记录结束时间、额度和会话标识，保存会话记录。发生手工指导、审批等待、工具故障或中断时，在记录中写明原因和耗时。
4. 对 `run-02` 使用新会话和 [缺陷 prompt](tasks/bug.md)，重复上述过程。
5. 应用 B 组配置，重启并完成独立的配置加载检查，再分别在 `run-03`、`run-04` 运行功能和缺陷任务。使用与 A 组完全相同的任务正文。

四次任务顺序运行，以便归属额度消耗；每个任务内部的并行方式由 agent 决定。`usage_before` 和 `usage_after` 可记录五小时、每周剩余额度及其重置时间，单位与来源写进 `usage_measurement_notes`。额度重置、显示精度不足或同时存在其他消耗时，保留原始观测并标为不可直接比较。

## 独立验收

在被测会话完成后，从外部运行验收。以第一轮功能任务为例：

```powershell
& $Py "$Bench\evaluate.py" --task feature --project "$Runs\run-01" --output "$Bench\local-runs\results\feature-A-1.json"
```

其他三轮替换任务名和运行名即可。退出码 0 表示自动检查通过，1 表示存在验收失败，2 表示评估工具无法运行。每次生成 JSON 报告、相对初始提交的 `.patch` 和包含新增源码的 `.zip`；同名输出不会覆盖。ZIP 包含 Git 跟踪及未忽略的新文件，运行时数据库等被忽略文件不包含在内。验收使用临时数据库，不应改动项目源码。

将报告路径写进对应运行记录的 `evaluation_file`。自动检查之后，按 [人工评价表](evaluation/rubric.md) 比较代码、文档和最终回复。验收耗时与准备成本不计入被测任务耗时，单独保留。

## 材料与结论范围

- [实验协议](protocol.md)：比较对象、停止与重复规则、指标解释。
- [配置说明](configs/README.md)：两组的真实差异及切换注意事项。
- [准备验证](validation.json)：起始状态和参考实现的校准结果，不是 A/B 实验成绩。
- `evaluation/reference/`：只用于校准验收的参考实现，不复制到正式工作副本。

第一轮用于检查题目、配置加载和测量方法是否可用。每组只有一次运行，结果不能说明稳定胜率，也不能把差异单独归因于某个角色或某段指令。

维护实验材料时，可用 `& $Py "$Bench\selfcheck.py"` 重新执行校准；该命令不调用 Codex，会更新 `validation.json`，详细临时结果留在被 Git 忽略的 `.scratch/` 中。业务起点、prompt、配置或验收修改后，应先明确新的实验版本并更新 `freeze.json`，再做校准和配对运行。

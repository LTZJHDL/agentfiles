# Subagent description 选型模拟

实验开始时的描述已经能区分特征鲜明的任务。operator 与 worker 的区分基本有效；professor 在明确需要表达、品味和问题定义的场景中会被选择，但在日常判断任务中，成本措辞可能提高它的出场门槛。给 kami 加上 `godlike`，本轮没有观察到对 kami 选择的影响。

本实验只检查名称和 `description` 如何影响选择，不执行任务，也不衡量实际结果质量或长期调用频率。实验期间保持五份角色配置不变；随后仅调整了 professor 的描述，采用情况见下文。文中的“当前版”和 A 组均指实验开始时保存的描述。

## 方法

三组描述各交给两个新建、未继承本对话历史的 default 子 agent。当前运行配置的默认子 agent 为 `gpt-6-astra medium`；这不是对不同主模型或 effort 的横向测试。

选择者只读取对应的角色名称、描述和任务文本。它们看不到模型配置、`developer_instructions`、其他选择者的结果，以及主 agent 对角色分工的预期。模拟统一假设任务值得委派，以便单独观察选谁；真实使用中，一部分短任务可能由主 agent 直接完成。

| 条件 | 变化 |
| --- | --- |
| A：当前版 | 原样使用仓库内的五个 `description` |
| B：角色对比版 | operator 增加 `modest reasoning depth`；worker 强调 `versatile mainstay` 和 `strong execution`；professor 增加 `regular collaborator`、`sharp judgment`，并将 `premium cost` 改为 `somewhat higher expected cost` |
| C：godlike 版 | 仅在当前 kami 描述的 `tenacious` 前增加 `godlike` |

每组的第一次按文件顺序选择，第二次倒转任务及角色列表顺序。第一轮为 16 个特征鲜明的场景，每次返回首选、备选、简短理由和自报把握。主 agent 在看到结果前记录了这些场景的偏好角色；偏好用于核对设计意图，不是客观正确答案。

第一轮结果完全一致，因此追加 8 个日常边界场景。第二轮沿用各选择者自己的上下文，没有向它们透露第一轮的整体结果，也没有为边界场景预设唯一答案。共得到 144 个选择，分布在六个上下文中，不能视为 144 个统计独立样本。

## 第一轮：明显的差异能够被读懂

16 个场景在三种描述、两次运行中，首选全部一致。

| 场景 | 所有运行的首选 |
| --- | --- |
| T01：找出超时配置的精确值和位置 | explorer |
| T02：按既有模式实现 CSV 导出 | worker |
| T03：润色产品介绍，选择表达重点 | professor |
| T04：运行既有检查命令并记录结果 | operator |
| T05：为交互复杂的分布式协议寻找证明或反例 | kami |
| T06：判断两种 API 的概念和边界 | professor |
| T07：按给定映射和脚本规范化记录 | operator |
| T08：修复原因明确、涉及三个模块的缺陷 | worker |
| T09：检索指定版本的官方默认值及出处 | explorer |
| T10：识别产品提案背后的真正问题 | professor |
| T11：按完整清单机械地重命名配置项并检查 | operator |
| T12：按迁移指南升级依赖并完成集成 | worker |
| T13：调查证据矛盾、常见解释尚未奏效的数据损坏问题 | kami |
| T14：为敏感确认流程写简短按钮文案 | professor |
| T15：按既定规则完成跨组件的设置表单 | worker |
| T16：解决多种自然思路已失败的算法不变量问题 | kami |

当前版每次选择 explorer 2 次、operator 3 次、worker 4 次、professor 4 次、kami 3 次。短文和按钮文案都交给了 professor，说明当前描述没有把它限制为长任务或极难任务。operator 也被用于会修改文件的机械任务，选择者没有把它理解成只能执行检查命令。

## 第二轮：日常判断仍有成本门槛

下表每格为同一条件两次运行的首选。两次相同则只写一次。

| 场景 | A：当前版 | B：角色对比版 | C：godlike 版 |
| --- | --- | --- | --- |
| B01：判断并改善一个 70 行辅助函数的清晰度 | worker | worker | worker |
| B02：改善普通内部文档略显生硬的开头 | operator | worker / operator | operator |
| B03：运行测试并处理直观的 fixture 不匹配 | operator | operator | operator |
| B04：实现小型设置开关，顺带决定标签和位置 | worker | worker | worker |
| B05：为三个内部函数选择更清楚的名称 | operator | worker | operator |
| B06：把简单事故报告整理成五条交接要点 | explorer / operator | operator | explorer |
| B07：简化涉及六个文件的过度复杂实现 | worker | worker | worker |
| B08：审视日常设计理由中的假设与取舍 | worker | professor | worker |

B08 是最有解释价值的差异。当前版的两次选择都认为，这种日常判断交给 worker 更合算；其中一次的原话是：

> Routine decision scrutiny needs pragmatic judgment; premium deliberation seems disproportionate.

角色对比版两次都选择 professor。其中一次解释为：

> The output centers on assessing assumptions and tradeoffs, where sharp judgment adds value despite the routine scope.

这说明当前 professor 描述可以传达判断力，却仍可能被理解为需要额外证明价值的高价专家。把它描绘成日常可请教的同事，是值得考虑的调整。不过，B 同时改变了三个角色的描述，不能将差异单独归因于 `regular collaborator` 或某个成本词。

operator 与 worker 的基本区分在两轮中都成立。B05 的变化说明，当前 `practical judgment` 允许 operator 承担一些小型语义判断；增加 `modest reasoning depth` 后，这类工作更容易流向 worker。这不是明确的错误，也体现了画像仍留有自主判断空间。

## kami 与 godlike

C 组的 kami 首选与 A 组完全相同：三个明显需要深入推敲的场景，每个运行各一次；八个边界场景中均未选择 kami。唯一不同是 B06 在一次运行中从 operator 换为 explorer，这不足以说明 `godlike` 对该选择有因果影响。

本轮支持保留 `kami` 作为有象征性的名称，但没有提供在描述中再加入 `godlike` 的选型收益证据。它可能激发的语气、自信或实际推理行为并未测试。角色的能力特点、投入程度和成本，仍是比这个修饰词更清楚的选择依据。

## 对配置文字的判断

operator 与 worker 暂无必要大改。如果希望差异更直观，可以借助 `lightweight assistant` 与 `versatile mainstay` 这类画像词，而不用增加任务清单。B 中更强的能力限定会改变一些小型判断任务的归属，是否需要这种效果取决于实际使用偏好。

professor 最值得小幅调整：保留判断、品味和表达，补上经常参与协作的意味，减弱 `premium` 带来的高价专家印象。B 的完整候选句是：

> An approachable professor and regular collaborator: broad understanding, sharp judgment, good taste, and clear expression, with measured deliberation and a somewhat higher expected cost.

这句话没有规定职责范围。实验后已将它用于正式 professor 配置，其余角色描述和所有 `developer_instructions` 保持不变。现行组合只采用了 B 组中的 professor 改动，没有重新进行选型模拟，因此 B 组的结果不能直接等同于现行组合的结果。`somewhat higher expected cost` 表达这套角色设计的成本预期，不是本实验测得的价格差。

场景及候选描述均由主 agent 编写，第一轮刻意覆盖了各角色的鲜明特点，因此不能用其一致性证明真实分工已经完善。第二轮样本也很小，并延续了第一轮上下文。这里的“把握”是选择者自报，不能当作校准过的正确率。两个阶段都没有实际执行任务，也没有检验更昂贵的角色是否产生更好的结果。

## 原始记录与校验

- [实验设计和事前偏好](plan.json)
- [当前描述](inputs/catalog-a.json)、[角色对比描述](inputs/catalog-b.json)、[godlike 描述](inputs/catalog-c.json)
- [第一轮任务](inputs/scenarios.json)、[第二轮任务](inputs/boundary-scenarios.json)
- [第一轮逐项选择](choices.csv)、[第二轮逐项选择](boundary-choices.csv)
- [第一轮统计](summary.json)、[第二轮统计](boundary-summary.json)
- 每次选择的备选、理由和把握保存在 `runs/` 下的十二份 JSON 中。

[summarize.py](summarize.py) 会检查每次运行的场景完整性、角色名称、备选和字段格式，并根据原始记录重算 CSV 和统计。第一轮使用 `python summarize.py`，第二轮使用 `python summarize.py --boundary`。这些命令只重算已有记录，不会重新调用模型。

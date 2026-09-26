# 匿名阅读体验评审

只读分配的 pairs 文件和此 rubric。不要读规范、原始运行文件、映射、事实评审、其他评审或上一轮试验。
每对按用户的问题及读者背景评价 X/Y。区别“包含相同事实”和“这些事实是否更好理解”，不要把较短、较长、分节或图表自动当优点。允许真实的轻微偏好，也允许相当。必须说明具体文本如何影响读者，不猜实验条件。

每对输出：
- pair_id
- dimensions：orientation（整体认识）、prerequisites（概念引入）、relationships（流程/依赖/比较）、locality（相关信息集中）、economy（重复与篇幅是否值得）；每项 {preference: X|Y|tie, impact: material|minor|none, evidence: 中文具体证据}
- comprehension：对本题四个预设理解问题，分别指出 X/Y 中最直接支持答案的短语、是否需拼接远处段落，缺失则直说。不要将此定位分析称为实际阅读耗时测量。
- overall_preference：X|Y|tie
- materiality：material|minor|none
- reason：整体阅读体验判断，指出具体受益或代价。允许各维度优劣相抵。
- suspected_factual_issues：只记录答案内部可见的问题；不要凭你未看到的项目实现判错。

输出 JSON 数组。你的判断是阅读体验评估，不负责源材料事实核验。

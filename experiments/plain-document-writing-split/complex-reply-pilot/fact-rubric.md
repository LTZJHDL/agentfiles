# 匿名事实核验
只读分配的任务包（含用户请求、材料、预设事实和四份匿名答案）。不要读取条件映射、表达规范、其他评审或上一轮结果。按材料核查；代码优先于文档概述。事实清单是参考而非必须逐条复述的模板，core=false 项只有在答案涉及并出错时才构成问题。
每份答案输出 {answer_id, facts:[{id,status:correct|partial|absent|incorrect,evidence,impact:none|minor|material}], other_issues:[{quote,issue,source,impact}], overall:"中文结论"}。区分事实错与合理省略；partial/absent不自动是缺陷，应看用户需求。不要评价文采或推测组别，不联网不执行源代码。输出JSON数组。

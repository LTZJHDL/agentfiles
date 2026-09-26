# 根据答案回答理解问题

仅阅读分配的 reader-packet 文件。不读取项目材料、规范、其他答案、映射或评分；不联网。每个条目是独立的一次阅读，不能以其他条目或自己的项目知识补足缺失内容。

根据该条目给出的 answer 回答其四个问题。每问记录 {question_id, answer, support_quote, status:explicit|inferred|not_stated, navigation:local|combine|missing}。
explicit 表示答案直接给出；inferred 表示需要连接答案中的多个已给信息；not_stated 表示不能从答案确定。support_quote 必须逐字摘自答案，可用数组给多处短引文。navigation=combine 表示需要拼接不同段落，不能用长度判断。
输出 JSON 数组，每项 {answer_id, task, questions:[...]}。这是信息提取任务，不要求评价哪个版本更好，不猜实验条件。

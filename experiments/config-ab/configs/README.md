# 两组配置快照

A 保存准备时 `C:\Users\LTZJH\.codex` 的相关文件，B 保存 `agentfiles/codex` 的候选文件。原始来源与主模型默认值另见 [source-notes.json](source-notes.json)。这些快照不含认证信息、通知脚本或其他无关应用设置。

| 设置 | A：旧配置 | B：候选配置 |
| --- | --- | --- |
| AGENTS.md | 原有具体委派规则 | 精简的沟通与协作引导 |
| explorer | gpt-5.6-luna medium，原有描述和限制 | gpt-6-luna medium，新角色描述 |
| operator | 无自定义角色文件 | gpt-6-luna high |
| worker | 使用运行时提供的内置角色 | gpt-6-sol high，自定义角色 |
| professor | 无自定义角色文件 | gpt-6-astra medium |
| kami | 无自定义角色文件 | gpt-6-astra max |
| 默认子 agent | gpt-6-astra medium | gpt-6-astra xhigh |
| 并发上限 | 10 | 10 |

每组包含 `AGENTS.md`、`agents/*.toml` 和 `settings.toml`。最后一个文件只是需要合并的配置片段，不是完整 config.toml。主模型在两组中固定为 `gpt-6-astra xhigh`，不要套用仓库候选 config.toml 中不同的主模型默认值。

切换时应使实际角色目录与对应组的角色集合一致，同时保留备份。尤其从 B 回到 A 时，仅复制 explorer 不会移除 operator、professor、kami 等额外角色。应用配置后重启，在正式任务以外的新会话中确认实际可调用角色与说明；不能用“文件存在”代替加载确认。内置 default、worker 等角色由运行时提供，完整可用角色列表应记入运行记录。

本实验工具只保存快照和生成项目，不修改实际 Codex 配置。以上内容说明本轮要比较的条件，不主张这些文件在未来版本中保持相同加载行为。

---
tags:
  - type/index
---
# _Inbox · 候选素材收件箱

本目录接收自动化轮询产生的协议候选素材，是知识库的 **intake queue**。候选不等于文档，只有经过 review / adopt 才会进入 `basic/` 或 `bus/<领域>/`。

## 目录约定

| 路径 | 作用 |
| --- | --- |
| `*.md` | 待处理候选（默认 `pending`） |
| `已处理/` | 已采纳或已丢弃的候选，保留溯源 |
| `_rotation-state.json` | 自动化轮转状态，不要手工编辑 |

本目录已在 `.obsidian/app.json` 中排除，不进入搜索、图谱和链接建议。

## 状态约定

候选文件可使用 frontmatter 标记状态；缺省视为 `pending`：

```yaml
---
status: pending        # pending | reviewed | adopted | dropped
protocol: BLE
created: 2026-11-05
reviewed: 2026-11-20
---
```

`adopted` / `dropped` 的候选应移动到 `已处理/`。

## 消化流程

每周一次，或 `pending > 10` 时触发：

1. 运行 `python scripts/inbox_status.py` 查看积压、最老候选和 stale 列表。
2. 从最老或与当前主题最接近的候选开始。
3. **采纳**：把内容写入 `basic/` 或 `bus/<领域>/`，在文档中标注来源 `_Inbox/已处理/<file>`，设置 `status: adopted` 后移入 `已处理/`。
4. **丢弃**：设置 `status: dropped` 并移入 `已处理/`，保留文件用于审计。
5. **暂缓**：设置 `status: reviewed`，保留在根目录，等待下一轮。
6. 维持 `pending <= 10`；超过 30 天未处理必须 reviewed 或 dropped；超过 90 天默认 dropped。

## 来源引用

- 统一引用 `_Inbox/已处理/<file>`，不要引用根目录待处理文件，因为它们会被移动。
- 候选内容可能包含外部链接和未验证数据，采纳前必须复核。

## 相关

- [Home](../Home.md)
- [TOPIC_MATRIX](../TOPIC_MATRIX.md)
- [scripts/inbox_status.py](../scripts/inbox_status.py)

# DailyWord 每日单词

## 功能总结

| 功能 | 说明 |
|------|------|
| 每日单词 | 基于日期选取，同一天同一单元显示同一个词 |
| 随机切换 | 点击"换一个"随机换词 |
| 单元切换 | ◀ ▶ 按钮切换 unit01~unit30 |
| 释义 | 显示词性+中文释义 |
| 例句 | 缺少时自动从 Free Dictionary API 联网查询（最多3句） |
| 词源 | 缺少时自动从 Wiktionary API 联网查询 |
| 数据缓存 | 联网获取的数据自动回写 JSON，下次无需再查 |
| 后台线程 | API 查询不阻塞 UI，先显示"查询中…"再更新 |
| 滚动 | 鼠标滚轮可滚动卡片内容 |
| 主题 | 与 OnlineQuote.py 相同的 Catppuccin 暗色主题 |

## 运行方式

```
python DailyWord.py
```

## 数据来源

- 词库：`vocabulary/unit01.json` ~ `unit30.json`（共 30 个单元，4618 个单词）
- 例句：[Free Dictionary API](https://dictionaryapi.dev/)（免费，无需 key）
- 词源：[Wiktionary MediaWiki API](https://en.wiktionary.org/w/api.php)（免费，无需 key）

## 词库 JSON 结构

```json
{
  "word": "salary",
  "phonetic": "[ˈsæləri]",
  "meanings": [
    { "pos": "名", "definition": "薪水；工资" }
  ],
  "examples": [
    { "en": "He earns a good salary.", "zh": "" }
  ],
  "etymology": "From Middle English salarie, from Anglo-Norman salarie..."
}
```

- `examples` 和 `etymology` 初始为空，联网查询后自动回写填充

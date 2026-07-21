# demo/

脱敏后的 Cursor × weekly-review 示例输出。

| 文件 | 说明 |
|------|------|
| `review-input-cursor-demo.json` | Agent 采集事实包（路径/会话 ID 已脱敏） |
| `2026-07-20周度复盘-Cursor-Demo.md` | 六章报告 |
| `chart-时间分布-2026-07-20.svg` | 辅助图 |
| `chart-归因Token-2026-07-20.svg` | 辅助图 |

重新生成：

```bash
cd skills/weekly-review
python -m cli --input ../../demo/review-input-cursor-demo.json -o ../../demo/2026-07-20周度复盘-Cursor-Demo.md
```

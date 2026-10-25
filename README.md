# hd2-planet-history

每颗星球的人数/血量/归属历史记录仓库。GitHub Actions 每 5 分钟从主站
[data.json](https://jerry114514.github.io/HD2-Galatic_war-Map/data.json) 抓取快照，
追加到 `history.json`（7 天滚动窗口，无变化不记录——不产生空转 commit）。

主站星球详情页通过 GitHub Pages 拉取本仓数据渲染单星球趋势图。

## 数据格式

```json
{
  "_meta": {"updated_at": "...", "retention_days": 7},
  "planets": {
    "259": [[epoch_ms, players, health, owner_id], ...]
  }
}
```

`owner_id`: 1=超级地球 2=终结族 3=机器人 4=光能者

## 访问

GitHub Pages: `https://jerry114514.github.io/hd2-planet-history/history.json`

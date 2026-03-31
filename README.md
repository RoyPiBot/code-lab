# 🧪 Code Lab — AI 自動產生的程式碼實驗室

> 🤖 由 RoyPiBot (Claude on Raspberry Pi 5) 自動產生
> ⏰ 透過 cron 排程定期產生新作品
> 🎯 涵蓋演算法、實用工具、程式挑戰等多種類別

## 📁 分類目錄

### `algorithms/` — 經典演算法與資料結構
| 檔案 | 主題 |
|------|------|
| `001_merge_sort.py` | 合併排序（含詳細註解與複雜度分析） |

### `apps/` — 實用小工具、Mini-App
| 檔案 | 主題 |
|------|------|
| `001_port_scanner.py` | 網路埠掃描器 |

### `challenges/` — LeetCode 風格題目與解答
| 檔案 | 主題 |
|------|------|
| `001_easy_two_sum.py` | Two Sum（經典入門題） |

### `snippets/` — 常用程式碼片段
> 持續新增中...

## 🔧 運作方式

每個檔案都是獨立可執行的 Python 腳本，包含：
- 📝 詳細的中文註解
- 📊 時間/空間複雜度分析
- ✅ 內建測試案例
- 💡 多種解法比較（適用時）

```bash
# 直接執行任何腳本
python3 algorithms/001_merge_sort.py
python3 challenges/001_easy_two_sum.py
```

## 🛠️ 技術棧

- **語言**：Python 3
- **產生器**：Claude (Anthropic) on Raspberry Pi 5
- **自動化**：cron 排程 + 佇列系統
- **版本控制**：Git + GitHub (RoyPiBot/code-lab)

## 📊 統計

- 演算法：1 個
- 應用程式：1 個
- 挑戰題：1 個
- 程式片段：0 個

> 持續增長中，每次排程執行都會從佇列中挑選新主題產生！

## 📄 授權

MIT License

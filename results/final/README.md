# 主实验结果

这是 2026-10-26 的一次真实模型主实验，包含最低必要处理 `minimum`、固定规则 `fixed`、智能体 `agent` 三组。主实验与[后三次补充实验](../stability/README.md)分别存储。

## 建议阅读顺序

1. [quality_before.json](quality_before.json)：原始质量问题。
2. [comparison.csv](comparison.csv)：三组保留数、填补数、轮廓系数、DB、CH 和状态。
3. [agent_status.json](agent_status.json)：模型最终策略、理由、调用数和 tokens。
4. [agent/cluster_profiles.csv](agent/cluster_profiles.csv) 与 [agent/representative_apps.csv](agent/representative_apps.csv)：簇画像和代表记录。
5. [common_metrics.csv](common_metrics.csv)、[common_group_ari.csv](common_group_ari.csv)、[common_seed_stability.csv](common_seed_stability.csv)：共同样本控制和初始化检查。

## 每组文件

| 文件名 | 如何使用 |
| --- | --- |
| `cleaned.csv` | 原始字段、解析值、代理值和标志；按 `source_row_id` 找记录 |
| `clusters.csv` | 实际参与聚类的记录、特征和簇标签 |
| `quarantine.csv` | 被隔离的核心异常记录 |
| `changes.csv` | 行级处理动作与理由 |
| `quality_after.json` | 清洗后数量与残留质量状态 |
| `k_candidates.csv` / `selected_model.json` | k=2…6 的比较及最终选定模型 |
| `cluster_profiles.csv` / `representative_apps.csv` | 各簇中位数画像与代表案例 |

`fixed/centers_standardized.csv` 是固定规则组变换空间的中心，区别于原单位的中位数画像。簇标签 0、1、2 没有大小或优劣排序。

## 图表

先看[原始质量问题](figures/raw_q1_quality.png)、[三组样本保留](figures/process_q1_retention.png)和[k 的选择](figures/process_q2_k_selection.png)。完整图表口径如下：

| 图 | 口径 |
| --- | --- |
| [raw_q1_quality](figures/raw_q1_quality.png) | 原始 n=10,841；质量项目可重叠，不应求和 |
| [raw_q2_rating](figures/raw_q2_rating.png) | 9,366 条有效评分；保留重复，未填补 |
| [raw_q2_reviews_installs](figures/raw_q2_reviews_installs.png) | 10,840 条核心有效记录；安装量为档位下界 |
| [process_q1_retention](figures/process_q1_retention.png) | 区分保留清洗档案和参与聚类 |
| [process_q1_imputation](figures/process_q1_imputation.png) | 填补操作数，同一记录可能两项均填补 |
| [process_q2_k_selection](figures/process_q2_k_selection.png) | 原生样本不同，跨组仅作描述 |
| [result_q1_remaining](figures/result_q1_remaining.png) | 填补不消除“原始未观测”状态 |
| [result_q2_centers](figures/result_q2_centers.png) | 固定规则组标准化空间中心，非原单位均值 |
| [result_q2_pca](figures/result_q2_pca.png) | 固定规则组 PCA 示意；抽取 2,500 点，不用于重新聚类 |

[run_manifest.json](run_manifest.json) 与 [logs/pipeline.jsonl](logs/pipeline.jsonl) 是运行证据；[shared_scaler.json](shared_scaler.json) 记录参考样本与缩放参数。已完成的人工复核统一移至 [docs/review](../../docs/review/README.md)。

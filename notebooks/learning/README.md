# Olist学习Notebook：公开阅读与本地练习

[个人学习路径](../../docs/role01/learning-path.md) · [1号工作导航](../../docs/role01/README.md)

这里保留的是经过整理的教学代码。原件和完整运行输出留在本地/组内私有空间；不是把整个group目录备份到公开GitHub。

## 建议阅读顺序

| 顺序 | Notebook | 学习目标 |
|---|---|---|
| 1 | [认识原始数据](01_raw_data.ipynb) | 区分订单、明细、买家和时间范围 |
| 2 | [九表结构与键](02_nine_tables.ipynb) | 列出字段、校验主键/复合键与关系 |
| 补充 | [九表学习批注版](02b_nine_tables_notes.ipynb) | 保留个人加入的关系图和练习 |
| 3 | [关系、时间与质量](03_relations_time_quality.ipynb) | 核连接缺口、日期、状态和金额 |
| 4 | [独立发现问题](00_problem_discovery.ipynb) | 区分数据事实与任务定义 |
| 5 | [选择预测期限](04_forecast_horizon.ipynb) | 比较窗口而不把正例增加当作准确率提升 |
| 6 | [窗口决策过程](05_window_decision.ipynb) | 检查覆盖、名单和跨期变化；只开放已有三期 |
| 7 | [岗位02：订单与客户](../02-role01-order-fact-and-history.ipynb) | 建立订单事实表和历史聚合 |
| 8 | [岗位03：覆盖、特征和标签](../03-role01-h02-coverage-features-labels.ipynb) | 生成独立的输入/标签并做边界核查 |
| 9 | [岗位04：独立复算与验收](../04-role01-h02-independent-review.ipynb) | 从原始表核查全部快照和交接文件 |

## 本地运行

1. 使用Python3.12，按仓库requirements.txt安装依赖。
2. 按[数据来源说明](../../data/README.md)取得Olist原始包，放在仓库data/olist-v2.zip。按[运行指南](../../docs/06-run-guide.md)解压、核验至data/raw。不要上传原始数据。
3. 注册本项目内核，在仓库根目录启动Jupyter。Notebook从当前目录向上寻找data目录；不要复制作者的电脑绝对路径。

```powershell
python -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
.\.venv312\Scripts\python.exe -m ipykernel install --user --name olist312 --display-name "Python 3.12 (Olist)"
.\.venv312\Scripts\python.exe -m jupyter lab
```

学习课可以分别按顺序执行全部单元。岗位02/03/04有前后依赖，也可以在根目录运行：

```powershell
.\.venv312\Scripts\python.exe scripts/build_h02_reviewed.py
```

**公开岗位代码的版本与输出隔离到outputs/public_learning/**，只用于本地练习；不要替换原有组内H02版本。生成的真实逐行数据、标签、执行后Notebook输出仍保持私有。提交前清除输出并检查代码中是否加入个人路径和编号；.gitignore不能自动清除Notebook单元输出。

## 整理了哪些内容

- 清除全部公开副本的outputs、执行次数、附件和个人Notebook元数据。
- 个人绝对路径改为项目内相对查找；岗位实例运行时选客户，不把真实编号写进源码。
- 原始数据入门课补上显式加载customers/orders/items，避免NameError和旧内核依赖。
- 窗口决策课的日期网格限制在已开放三期，不自动扫描潜在最终评价期。
- 重复副本只保留一份主版本；不同内容的批注版保留为补充。
- Untitled依赖其他课的变量，不冒充独立课程，整理为[草稿片段](../../docs/role01/learning-scratch-notes.md)。无法解析的下载文件未发布；进度总结已融入个人学习文档，原件保留。

## 来源和验证

基础九表教学和项目逻辑参考[CercaTrovato/olist-repurchase-analysis](https://github.com/CercaTrovato/olist-repurchase-analysis)，Olist数据许可与代码许可见[LICENSES](../../LICENSES.md)。本次改动保留来源，不把团队既有材料全部声称为个人原创。

验证状态、每份Notebook代码单元数见[发布记录](../../docs/role01/notebook-publication.json)。实际复跑输出只保存在本地验证目录，公开GitHub中不嵌入逐行客户输出。程序通过不等于本人学习或团队验收完成。

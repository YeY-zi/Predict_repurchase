# 发布前验证记录

初次记录日期：2026-10-04；反馈实验补充于 2026-10-25。本记录说明实际执行过什么，不将文件存在或程序运行完当作商业结论成立。

## 已执行

- 从 Olist 官方接口下载的 ZIP 解压 9 个 CSV，CRC 与逐文件 SHA-256 匹配；本仓库提供下载脚本和来源清单，原始 ZIP 不提交到 Git 历史。
- 在独立仓库目录中执行 `scripts/run_catboost.py`、`scripts/compare_models.py` 与 `scripts/run_segmentation.py`；使用相对路径，没有读取维护者的课程目录。
- 分类四模型和简单规则的四个指标，与保留的初次探索结果一致；分群指标亦一致。
- 两份Notebook从独立空内核运行：数据入门16个代码格、复购指标讲解5个代码格，均无错误输出。
- Markdown本地链接、Python语法、指标分母计算及五页PPT压缩包结构检查通过。
- PPT沿用已在Microsoft PowerPoint逐页查看的五页版本；公开副本仅清理作者元数据，不改幻灯片和讲稿内容。
- 补充运行 `scripts/audit_cleaning.py` 和 `scripts/run_feedback.py`；三表审计、四个特征方案的验证对照、分群规模和前 10% 名单人数经过 `scripts/verify_release.py` 核对。反馈实验在当前本地环境运行，保留完整的验证期改善与已公开测试期下降。
- 新增八页结果汇报 PPT；逐页渲染检查文字与布局，包结构、字体和重新导入检查通过。讲稿与来源放在各页备注中。

## 环境与边界

实际运行使用Windows、Python3.12.3、numpy1.26.4、pandas2.3.3、scikit-learn1.5.1、CatBoost1.2.8、matplotlib3.9.2。没有另建一个空操作系统或全新虚拟环境安装所有依赖，也未在macOS/Linux重新验证。

没有独立真人零基础试读评分；没有真实营销干预；没有确认性的多时间测试或置信区间。当前结果必须按探索实验解释；此前记录的 Python 版本是原始实验环境，新增反馈实验须以本机安装的依赖版本复现。

## 怎样自行检查

在根目录运行 `python scripts/verify_release.py`，检查链接、数据指纹和记录的指标算术。它不会训练模型。重新训练按运行指南执行；不要直接替换历史results，先比较outputs并记录差异。

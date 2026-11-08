# 草稿中保留的学习片段

本页来自未完成的Untitled草稿。它依赖其他课中建立的tables变量，不能独立执行；不是已验证教学入口。原始输出留在私有原件。


| 操作 | 通俗解释 | 为什么需要 |
|---|---|---|
| `Set-Location ...` | 进入项目文件夹 | 让电脑在正确位置寻找代码和文件 |
| `python -m venv .venv` | 给项目建立一套独立的 Python 环境 | 不同项目可以使用不同版本的工具 |
| `pip install -r requirements.txt` | 按清单安装分析工具 | 如 pandas 处理表格、NumPy 做数值计算 |
| `python scripts/extract_data.py` | 执行仓库的数据校验与解压脚本 | 确认大家拿到相同原件，并取出 9 张表 |

| 步骤 | 你要理解并完成什么 | 完成标志 |
|---|---|---|
| ① 核输入 | 原始文件是否一致、6 号和 3 号提供了什么方案 | 明确数据版本、已有方案和缺件 |
| ② 建订单表 | 明细先汇总，再连接订单与客户 | 一行一订单，行数和金额没有被连接放大 |
| ③ 核研究口径 | 哪些订单算事件、哪些客户入样、预测什么 | 有可以直接写成代码的定义 |
| ④ 核候选日期 | 每个快照的六个月历史和未来 90 天是否可观察 | 覆盖检查、标签成熟时间、已探索情况明确 |
| ⑤ 建客户快照 | 历史生成特征，未来生成标签 | 一位客户在一个快照只有一行 |
| ⑥ 检查并交付 | 抽客户复算、检查边界、拆分特征与开放标签 | 符合新协议的 H02 文件 |

| 字段 | 读完要能解释什么 |
|---|---|
| `order_id` | 用它识别一笔订单，把同一订单的商品明细汇总起来 |
| `customer_id` | 用它连接订单表和客户表 |
| `customer_unique_id` | 用它识别跨订单的同一匿名买家 |
| `order_approved_at` | 用它把批准事件放进历史窗口或未来标签窗口 |

这里只生成内存中的演示表，不保存清洗后的完整数据。评价需要单独确定选择规则，地理位置需要先确定邮编聚合方法，本节没有强行拼成一张万能宽表。

**所以呢：**六个人可以各自选题，但订单单位与连接规则必须一致。

## 5. 数据质量：缺失不都是错误，重复不都应删除

`.isna().sum()` 数缺失值；除以行数是缺失比例。`.nunique()` 数不同非空取值。缺失评论正文不等于没有评分；缺少送达时间可能和订单状态有关。先解释，再决定清洗规则。

```python
quality_rows = []
for name, df in tables.items():
    for col in df:
        quality_rows.append({'表':name, '字段':col, '缺失数':int(df[col].isna().sum()),
                             '缺失率%':100*df[col].isna().mean(), '不同非空值':df[col].nunique()})
quality = pd.DataFrame(quality_rows)
display(quality.loc[quality['缺失数'].gt(0)].round({'缺失率%':2}))
print('地理表完整重复行：', tables['geolocation'].duplicated().sum())
print('地理表不同邮编前缀：', tables['geolocation'].geolocation_zip_code_prefix.nunique())
```

**正确办法：**先把商品、支付分别汇总成“一行一订单”，再连接。agg 指定汇总；sum 求和，nunique 数不同编号；validate='one_to_one' 要求两边键都唯一。how='left' 保留所有订单，未匹配字段会是缺失值，不能自动填成 0。

groupby('order_id').size() 数每笔订单有多少行；`merge` 按键连接；`query` 按条件挑行；`iloc[0]` 取第一项。示例选择同时有多条商品与支付记录的订单，只展示这一笔，不运行全库的错误连接。  在干什么这个看不懂，就像告诉我们直接链接会导致金额重复计算什么的嘛吗，此时我们已经链接了9个表了吗？为什么知道链接的正确方法是**正确办法：**先把商品、支付分别汇总成“一行一订单”，再连接。`agg` 指定汇总；`sum` 求和，`nunique` 数不同编号；`validate='one_to_one' 要求两边键都唯一。how='left'保留所有订单，未匹配字段会是缺失值，不能自动填成 0。  我们具体怎么链接的呢？为什么要这么链接？是用**99,441 个customer_id`**，用于订单侧连接。链接完以后发现有连接前后均为 99441 笔订单。这里只生成内存中的演示表，不保存清洗后的完整数据。评价需要单独确定选择规则，地理位置需要先确定邮编聚合方法，本节没有强行拼成一张万能宽表。

**所以呢：**六个人可以各自选题，但订单单位与连接规则必须一致。什么叫六个人可以各自选题，但订单单位与连接规则必须一致？
1. 96,096 个 customer_unique_id，用于跨订单统计买家。来链接的吗？我们通过看缺失数跟缺失比率来干嘛呢？看缺失数跟缺失比率发现
   地理表有 261,831 条完整重复行和 19,015 个不同邮编前缀。即使删除完整重复行，一个邮编仍可能有多个坐标；邮编位置是近似代表位置，不是客户精确地址。  就得知邮编位置是近似代表位置，不是客户精确地址。如果区域分析根据这个特点来看以什么范围进行分析对吧，接着5.1 检查连接缺口；这个在干嘛？也是在找缺失值吗？要如何根据这个特点进行数据清洗呢，接着我看懂6了就是检查数据集时间上完整程度看出了其中几个月特别是2016年数据存在较大缺失可以舍去这段时间，也帮助我们到时候划分数据集测试集提供了依据。状态为 delivered 的订单是什么意思呀？什么叫当前订单状态是提取时结果，不是下单时能预知的信息。
   所以呢：“全部订单”和“可评价送达的订单”是两个分母。

先把商品、支付分别汇总成“一行一订单”，再连接。agg 指定汇总；sum 求和，nunique 数不同编号；validate='one_to_one' 要求两边键都唯一。how='left'保留所有订单，未匹配字段会是缺失值，不能自动填成 0。

⑤ 看缺失数、缺失率，是为了决定什么？

是为了判断：哪些字段能够支持你的问题，缺失会影响多少记录，需要怎样处理。
| 发现 | 接下来怎么想 |
|---|---|
| 批准时间缺失 | 该订单无法直接放入按批准时间划分的窗口，需要记录并按事件规则处理 |
| 评价正文缺失 | 仍可检查评分是否存在，文字分析与评分分析要分别处理 |
| 商品重量缺失 | 会影响重量相关分析，但不一定影响商品金额汇总 |
| 商品金额因没有明细而缺失 | 金额未知，不能直接用零表示 |

5.1 检查连接缺口，和检查缺失值有什么不同？

两者检查的对象不同。

普通缺失值检查会问：
这张表里已经存在的某一行，某一列有没有值？

连接缺口检查会问：
这张表里的某个编号，在另一张表里有没有对应记录？

你作为 1 号，可以这样处理：
1. 在订单事实表保留这些订单，方便追溯。
2. 标记“无商品明细”，商品金额保留缺失。
3. 应用“批准时间存在、商品金额大于零”的资格规则时，记录哪些订单因此被排除。
4. 输出每一步排除多少笔，以及剩余客户数如何变化。
同样，768 笔订单没有评价。当前复购任务并不要求有评价，因此不应仅因为这个连接缺口就把它们全部删除。

，2016 年记录稀疏且分布不连续，需要进一步核查是否适合构造历史窗口。

你现在缺的其实是“看懂关系图之后，怎样把它变成连接步骤”。连接方法可以推导出来：先确定结果表一行代表什么，再看每次连接会不会把这一行变成多行。

可以请 AI 帮你设计和写代码。但以后换数据集，你仍需要能检查它选了什么粒度、有没有把金额复制。下面就用你这张图，把九张表的处理路线走一遍。

1．先确定我们想得到哪种表。

假设当前目标是：
一行代表一笔订单，同时显示商品总额、运费、支付金额、买家地区，以及需要的商品或评价信息。

那么这一阶段以 orders 为主表很合适，因为它已经是一行一订单。

但你们最终交给模型的是一行一位买家在一个快照的记录。我们先把订单算对，再把同一个买家的历史订单汇总成客户特征。

所以，“当前以订单表为主”来自我们选择的统计单位。换成商品明细分析，可以以 order_items 为主表；换成卖家分析，最后需要汇总到卖家。

2．每连一张表，问一句：左边这一行，在右边能找到几行？

这是判断会不会膨胀的直接办法。
| 左边当前的一行 | 右边匹配情况 | 连接结果 |
|---|---|---|
| 一条商品明细 | 找到唯一一个商品资料 | 仍然一条商品明细 |
| 一笔订单 | 找到唯一一个客户资料 | 仍然一笔订单 |
| 一笔订单 | 找到 3 条商品明细 | 变成 3 行 |
| 上面的每条商品明细 | 又找到 2 条支付记录 | 变成 6 行 |
| 上面的每一行 | 又找到 2 条评价 | 变成 12 行 |
当右边的连接键唯一时，左边每一行最多匹配一行，便不会因为这次左连接而增加行数。

所以我们可以先检查：
    products["product_id"].is_unique
customers["customer_id"].is_unique

    对于右边订单号重复的 items、`payments`、`reviews`，要根据目标，先汇总或选出一条代表记录。

另外，“左边每行没有增加”也不等于所有金额都可以随便求和。例如商品明细接上订单总额后，订单总额会在各明细行重复出现。每个金额字段都有它所属的统计单位。

3．沿着你图片里的每条分支处理，九张表可以这样联系。

假设我们需要订单级信息，下面是一条完整路线。实际项目只执行需要的分支。
| 分支 | 怎样处理 | 处理完后的一行是什么 |
|---|---|---|
| `products + translation` | 按品类名连接，要求翻译表品类名唯一 | 一个商品 |
| `geolocation` | 清查坐标后，按邮编前缀形成代表坐标 | 一个邮编前缀 |
| `customers + 邮编代表坐标` | 按客户邮编前缀连接 | 一个 `customer_id` |
| `sellers + 邮编代表坐标` | 按卖家邮编前缀连接 | 一个卖家 |
| `order_items + 商品资料 + 卖家资料` | 分别按 `product_id`、`seller_id` 连接，右边编号唯一 | 一条商品明细 |
| 上面的商品明细 | 按 `order_id` 汇总金额、运费及需要的特征 | 一笔订单 |
| `payments` | 按 `order_id` 汇总支付金额、支付记录数 | 一笔订单 |
| `reviews` | 按研究问题选定评价规则，汇总或选出一条 | 一笔订单 |
| `orders + 客户资料 + 三份订单汇总` | 分别按对应键连接 | 一笔订单 |

．为什么商品资料可以先接明细，而支付记录要先汇总？

看你图中的 order_items → products：
- 一条明细只有一个 product_id。
- 商品表中这个 product_id 对应一行资料。
- 因此每条明细接上品类、重量等信息后，仍然只有一行。
同样，一个卖家编号在 sellers 中对应一行。

| 想要的订单字段 | 计算方法 |
|---|---|
| 商品金额 | 明细 `price` 求和 |
| 运费 | 明细 `freight_value` 求和 |
| 商品明细条数 | 数明细行数 |
| 不同卖家数 | `seller_id.nunique()` |
| 不同品类数 | 品类字段 `nunique()` |
| 支付金额 | 支付记录金额求和 |
| 评价分数 | 先决定首评、末评、最低分或其他有理由的规则 |

```python
"""Draw the Olist order-grain join plan. This script only draws a diagram."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def draw_join_flow(output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    font_path = Path('fonts/chinese-font.ttf')
    if font_path.exists():
        font_manager.fontManager.addfont(str(font_path))
        plt.rcParams['font.family'] = font_manager.FontProperties(fname=str(font_path)).get_name()
    else:
        plt.rcParams['font.family'] = ['Microsoft YaHei', 'Noto Sans CJK SC', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    fig, ax = plt.subplots(figsize=(24, 17))
    fig.patch.set_facecolor('#f6f8fc')
    ax.set_facecolor('#f6f8fc')
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 17)
    ax.axis('off')

    def box(x, y, width, height, title, detail, color='#2364aa', fill='#ffffff'):
        ax.add_patch(FancyBboxPatch(
            (x-width/2, y-height/2), width, height,
            boxstyle='round,pad=0.09,rounding_size=0.12',
            facecolor=fill, edgecolor=color, linewidth=1.7, zorder=3))
        ax.text(x, y+height*0.19, title, ha='center', va='center',
                fontsize=15, fontweight='bold', color=color, zorder=4)
        ax.text(x, y-height*0.19, detail, ha='center', va='center',
                fontsize=11.5, color='#28364a', linespacing=1.5, zorder=4)

    def arrow(points, label=None, label_xy=None, color='#566b84'):
        for start, end in zip(points[:-2], points[1:-1]):
            ax.plot([start[0], end[0]], [start[1], end[1]], color=color, linewidth=1.6, zorder=1)
        ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle='-|>',
                                    mutation_scale=16, linewidth=1.6, color=color, zorder=2))
        if label:
            ax.text(*label_xy, label, ha='center', va='center', fontsize=11.5,
                    color=color, linespacing=1.5,
                    bbox=dict(facecolor='#f6f8fc', edgecolor='none', pad=4), zorder=5)

    ax.text(0.5, 16.55, 'Olist 九张表 → 一行一订单', fontsize=26,
            fontweight='bold', color='#173452', va='center')
    ax.text(0.5, 15.98, '连接字段写在线上；每个框注明处理后的粒度。按所需特征选择分支。',
            fontsize=13, color='#53667c')

    box(2.8, 14.9, 4.7, 1.0, 'translation', '一行一个 product_category_name')
    box(2.8, 12.5, 4.7, 1.2, 'products + 英文品类', '一行一个 product_id\n翻译表品类名须唯一')
    arrow([(2.8,14.31),(2.8,13.19)], '按 product_category_name 左连接\nproducts → translation：many_to_one', (2.8,13.75))

    box(10.5, 14.9, 5.3, 1.0, 'geolocation', '一行一条地理记录；邮编前缀会重复', '#9a6010')
    box(10.5, 12.5, 5.8, 1.2, 'geo_zip · 邮编代表坐标', '一行一个 geolocation_zip_code_prefix\n示例：核查坐标后，按前缀取经纬度中位数', '#9a6010', '#fff9ec')
    arrow([(10.5,14.31),(10.5,13.19)], '按 geolocation_zip_code_prefix 分组汇总', (10.5,13.75), '#9a6010')

    box(8, 9.8, 4.9, 1.3, 'sellers + 卖家代表坐标', '一行一个 seller_id\n邮编连接：many_to_one')
    box(17, 9.8, 5.8, 1.3, 'customers + 买家代表坐标', '一行一个 customer_id；连接后保留原粒度\n保留 customer_unique_id 供之后按买家聚合')
    arrow([(9,11.81),(9,11.2),(8,11.2),(8,10.54)],
          'seller_zip_code_prefix\n= geolocation_zip_code_prefix', (6.8,11.25))
    arrow([(12,11.81),(12,11.2),(17,11.2),(17,10.54)],
          'customer_zip_code_prefix\n= geolocation_zip_code_prefix', (16.3,11.65))

    box(4.6, 7.1, 7.3, 1.4, 'order_items + 商品资料 + 卖家地区',
        '一行一条商品明细\n唯一键：order_id + order_item_id')
    arrow([(2.8,11.81),(2.8,7.89)],
          '按 product_id 左连接\n明细 → 商品：many_to_one', (2.8,9.8))
    arrow([(8,9.06),(8,8.5),(6.7,8.5),(6.7,7.89)],
          '按 seller_id 左连接\n明细 → 卖家：many_to_one', (6.7,8.5))

    box(11.6, 7.1, 4.4, 1.4, 'payments', '一行一条支付记录\norder_id + payment_sequential')
    box(17.4, 7.1, 4.4, 1.4, 'reviews', '一行一条评价记录\n同一订单可能有多条')

    box(4.6, 4.25, 6.5, 1.3, 'item_order · 商品订单汇总',
        '一行一订单\n商品金额 sum；运费 sum；卖家数 nunique', '#187467', '#effaf6')
    box(11.6, 4.25, 4.4, 1.3, 'payment_order',
        '一行一订单\n支付金额 sum；支付记录数 size', '#187467', '#effaf6')
    box(17.4, 4.25, 4.4, 1.3, 'review_order',
        '一行一订单\n评价规则决定保留或汇总的内容', '#187467', '#effaf6')
    arrow([(4.6,6.31),(4.6,4.99)], '按 order_id 分组汇总\n品类、地区等需另定订单级统计规则', (4.6,5.65), '#187467')
    arrow([(11.6,6.31),(11.6,4.99)], '按 order_id 分组汇总', (11.6,5.65), '#187467')
    arrow([(17.4,6.31),(17.4,4.99)], '按 order_id 分组／选择\n先约定首评、末评或其他规则', (17.4,5.65), '#187467')

    box(1.5, 1.75, 2.4, 1.1, 'orders', '一行一订单')
    box(12.0, 1.75, 16.4, 1.4, 'order_fact · 一行一订单的事实表',
        'orders 为左表，按 order_id 接三份订单汇总；按 customer_id 接客户资料\n订单号唯一；左连接保留全部订单；未匹配字段保留缺失', '#173452', '#eaf1fb')
    arrow([(2.79,1.75),(3.71,1.75)])
    for x in (4.6,11.6,17.4):
        arrow([(x,3.51),(x,2.54)], 'order_id\none_to_one', (x,3.0))
    arrow([(19.99,9.8),(22.5,9.8),(22.5,1.75),(20.29,1.75)],
          '按 customer_id 左连接\n本数据 one_to_one\n客户表不按订单再汇总', (21.65,8.35))

    ax.text(0.5,0.55,
            '验收：行粒度与唯一键 → 未匹配数 → 同范围金额守恒。客户与卖家坐标分别命名为 buyer_* / seller_*。',
            fontsize=12, color='#30465e')
    ax.text(0.5,0.13,
            '这是订单级连接设计示意。地理代表值、评价规则与字段在预测时是否可用，需按任务核定。',
            fontsize=11, color='#66778b')
    fig.subplots_adjust(left=0.01,right=0.99,bottom=0.02,top=0.99)
    png = output_dir / 'olist_nine_tables_join_flow.png'
    jpg = output_dir / 'olist_nine_tables_join_flow.jpg'
    fig.savefig(png, dpi=160, facecolor=fig.get_facecolor())
    fig.savefig(jpg, dpi=160, facecolor=fig.get_facecolor(), pil_kwargs={'quality':95})
    plt.close(fig)
    return png, jpg


if __name__ == '__main__':
    destination = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
    for image_path in draw_join_flow(destination):
        print(image_path)

```

```python
from pathlib import Path
from IPython.display import Image, display
import runpy

# 绘图文件所在目录
diagram_dir = WORK_DIR / "outputs" / "role01_join_diagram"

# 执行绘图代码，生成 PNG 和 JPG
runpy.run_path(
    str(diagram_dir / "draw_join_flow.py"),
    run_name="__main__"
)

# 在 Notebook 中展示 PNG
display(
    Image(
        filename=str(diagram_dir / "olist_nine_tables_join_flow.png"),
        width=1200
    )
)
```
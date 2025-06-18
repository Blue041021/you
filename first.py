import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False # 解决负号显示问题

# 页面基础配置（宽屏、标题、图标）
st.set_page_config(page_title="超市销售数据仪表版", page_icon="🛒", layout="wide")

# 标题与说明
st.title("2022年前3个月超市销售数据可视化分析")
st.markdown("基于真实销售订单数据，多维度分析销售表现")

# 数据加载
st.sidebar.header("数据导入与筛选")
uploaded_file = st.sidebar.file_uploader("D:/streamlit_env/文件/supermarket_sales.xlsx", type=["xlsx"])

if uploaded_file is not None:
  df=pd.read_excel(uploaded_file)
  df["日期"]=pd.to_datetime(df["日期"])
  st.sidebar.success(f"已加载数据:{uploaded_file.name}(共{len(df)}条记录)")
else:
# 模拟数据
  sample_data = {
"订单号": ["1123-19-1176", "1226-31-3081", "1692-92-5582", "1750-67-8428", "1351-62-0822"],
"分店": ["1号店", "3号店", "2号店", "1号店", "2号店"],
"城市": ["太原", "临汾", "大同", "太原", "大同"],
"顾客类型": ["会员用户", "普通用户", "会员用户", "会员用户", "会员用户"],
"性别": ["男性", "女性", "女性", "女性", "女性"],
"产品类型": ["健康美容", "电子配件", "食品饮料", "健康美容", "时尚配饰"],
"单价": [58.22, 15.28, 54.84, 74.69, 14.48],
"数量": [8, 5, 3, 7, 4],
"总价": [465.76, 76.4, 164.52, 522.83, 57.92],
"日期": ["2022-01-27", "2022-03-08", "2022-02-20", "2022-01-05", "2022-02-06"],
"时间": ["20:33", "10:29", "13:27", "13:08", "18:07"],
"评分": [8.4, 9.6, 5.9, 9.1, 4.5]
}
  df = pd.DataFrame(sample_data)
  df["日期"] = pd.to_datetime(df["日期"])
  st.sidebar.info("未上传文件，使用模拟数据演示")

# -------------------- 数据筛选控件 --------------------
st.sidebar.subheader("数据筛选")

# 日期范围筛选（基于“日期”字段）
min_date = df["日期"].min()
max_date = df["日期"].max()
selected_dates = st.sidebar.date_input(
"选择日期范围",
value=(min_date, max_date),
min_value=min_date,
max_value=max_date
)
# 转换为 datetime 用于筛选
start_date, end_date = map(pd.to_datetime, selected_dates)
filtered_df = df[(df["日期"] >= start_date) & (df["日期"] <= end_date)]

# 分店筛选
store_list = filtered_df["分店"].unique().tolist()
selected_stores = st.sidebar.multiselect(
"选择分店",
options=store_list,
default=store_list,
help="可多选分店，分析不同门店表现"
)
filtered_df = filtered_df[filtered_df["分店"].isin(selected_stores)]

# 产品类型筛选
product_type_list = filtered_df["产品类型"].unique().tolist()
selected_product_types = st.sidebar.multiselect(
"选择产品类型",
options=product_type_list,
default=product_type_list,
help="如 '健康美容'、'电子配件' 等分类"
)
filtered_df = filtered_df[filtered_df["产品类型"].isin(selected_product_types)]

# -------------------- 核心分析看板 --------------------
st.header("一、总体销售概览")
col1, col2, col3, col4 = st.columns(4)

# 总销售额（总价求和）
total_sales = filtered_df["总价"].sum()
col1.metric("总销售额（元）", f"¥ {total_sales:,.2f}")

# 订单数量（记录数）
order_count = len(filtered_df)
col2.metric("订单数量", order_count)

# 客单价（总销售额 / 订单数）
if order_count > 0:
  avg_order_value = total_sales / order_count
  col3.metric("客单价（元）", f"¥ {avg_order_value:,.2f}")
else:
  col3.metric("客单价（元）", "0.00")

# 平均评分
if order_count > 0:
  avg_rating = filtered_df["评分"].mean()
  col4.metric("平均评分", f"{avg_rating:.1f}/10")
else:
  col4.metric("平均评分", "0.0/10")

# -------------------- 可视化 1：分店销售额对比（柱状图） --------------------
st.header("二、分店销售表现对比")
col1, col2 = st.columns(2)

with col1:
  store_sales = filtered_df.groupby("分店")["总价"].sum().reset_index()

  fig, ax = plt.subplots(figsize=(8, 5))
  sns.barplot(
  x="分店",
  y="总价",
  data=store_sales,
  ax=ax,
  palette="Set2"
)
ax.set_xlabel("分店名称", fontsize=12)
ax.set_ylabel("销售额（元）", fontsize=12)
ax.set_title("各分店销售额对比", fontsize=14, fontweight="bold")
st.pyplot(fig)

# -------------------- 可视化 2：产品类型销售占比（饼图） --------------------
with col2:
  product_type_sales = filtered_df.groupby("产品类型")["总价"].sum().reset_index()

  fig, ax = plt.subplots(figsize=(8, 5))
  ax.pie(
  product_type_sales["总价"],
  labels=product_type_sales["产品类型"],
  autopct="%1.1f%%",
  startangle=90,
  textprops={"fontsize": 10}
)
ax.set_title("产品类型销售占比", fontsize=14, fontweight="bold")
st.pyplot(fig)

# -------------------- 可视化 3：每日销售趋势（折线图） --------------------
st.header("三、销售趋势分析")
col1, col2 = st.columns(2)

with col1:
  st.subheader("每日销售趋势")
# 按日期分组求和（一天可能有多笔订单）
  daily_sales = filtered_df.groupby("日期")["总价"].sum().reset_index()

  fig, ax = plt.subplots(figsize=(10, 5))
  sns.lineplot(
  x="日期",
  y="总价",
  data=daily_sales,
  ax=ax,
  color="#2ecc71",
  marker="o"
)
ax.set_xlabel("日期", fontsize=12)
ax.set_ylabel("当日销售额（元）", fontsize=12)
ax.set_title("每日销售趋势", fontsize=14, fontweight="bold")
plt.xticks(rotation=45)
st.pyplot(fig)

# -------------------- 可视化 4：顾客类型与性别分析（柱状图） --------------------
with col2:
  st.subheader("顾客类型与性别分析")
  customer_gender = filtered_df.groupby(["顾客类型", "性别"])["订单号"].count().unstack().fillna(0)

  fig, ax = plt.subplots(figsize=(10, 5))
  customer_gender.plot(kind='bar', ax=ax, colormap='viridis')
  ax.set_xlabel("顾客类型", fontsize=12)
  ax.set_ylabel("订单数量", fontsize=12)
  ax.set_title("顾客类型与性别分布", fontsize=14, fontweight="bold")
  ax.legend(title="性别")
  plt.xticks(rotation=0)
  st.pyplot(fig)

# -------------------- 可视化 5：产品类型与评分关系（箱线图） --------------------
st.header("四、产品与评分分析")
col1, col2 = st.columns(2)

with col1:
  st.subheader("产品类型与评分关系")
  fig, ax = plt.subplots(figsize=(10, 5))
  sns.boxplot(x="产品类型", y="评分", data=filtered_df, ax=ax, palette="Set3")
  ax.set_xlabel("产品类型", fontsize=12)
  ax.set_ylabel("评分", fontsize=12)
  ax.set_title("各产品类型评分分布", fontsize=14, fontweight="bold")
  plt.xticks(rotation=45, ha='right')
  st.pyplot(fig)

# -------------------- 可视化 6：单价与数量关系（散点图） --------------------
with col2:
  st.subheader("单价与数量关系")
  fig, ax = plt.subplots(figsize=(10, 5))
  sns.scatterplot(
  x="单价",
  y="数量",
  data=filtered_df,
  ax=ax,
  hue="产品类型",
  palette="Set1",
  size="总价",
  sizes=(50, 200),
  alpha=0.7
)
ax.set_xlabel("单价（元）", fontsize=12)
ax.set_ylabel("购买数量", fontsize=12)
ax.set_title("单价与购买数量关系", fontsize=14, fontweight="bold")
st.pyplot(fig)


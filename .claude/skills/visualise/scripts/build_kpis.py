import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

DATA_DIR = ".claude/skills/migrate/data/2026-05-29/"
OUT_DIR = ".claude/skills/visualise/visualization/2026-05-29/"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load data ────────────────────────────────────────────────────────────────
sales = pd.read_parquet(DATA_DIR + "fact_sales.parquet")
returns = pd.read_parquet(DATA_DIR + "fact_returns.parquet")
products = pd.read_parquet(DATA_DIR + "dim_product.parquet")
stores = pd.read_parquet(DATA_DIR + "dim_store.parquet")
customers = pd.read_parquet(DATA_DIR + "dim_customer.parquet")

# ── KPI calculations ─────────────────────────────────────────────────────────
totalSales = sales["gross_amount"].sum()
totalReturns = returns["refund_amount"].sum()
netSales = sales["net_amount"].sum() - totalReturns
avgSalesPerStore = sales.groupby("store_sk")["gross_amount"].sum().mean()
avgSalesPerProduct = sales.groupby("product_sk")["gross_amount"].sum().mean()
avgSalesPerCustomer = sales.groupby("customer_sk")["gross_amount"].sum().mean()

print(f"Total Sales:             ${totalSales:,.2f}")
print(f"Total Returns:           ${totalReturns:,.2f}")
print(f"Net Sales:               ${netSales:,.2f}")
print(f"Avg Sales per Store:     ${avgSalesPerStore:,.2f}")
print(f"Avg Sales per Product:   ${avgSalesPerProduct:,.2f}")
print(f"Avg Sales per Customer:  ${avgSalesPerCustomer:,.2f}")

PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860"]

def formatMillions(x, _):
    return f"${x/1e6:.1f}M" if x >= 1e6 else f"${x:,.0f}"

# ── Chart 1: Summary KPI bar chart ───────────────────────────────────────────
kpiLabels = [
    "Total\nSales",
    "Total\nReturns",
    "Net\nSales",
    "Avg/Store",
    "Avg/Product",
    "Avg/Customer",
]
kpiValues = [totalSales, totalReturns, netSales, avgSalesPerStore, avgSalesPerProduct, avgSalesPerCustomer]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(kpiLabels, kpiValues, color=PALETTE, edgecolor="white", linewidth=0.8)
for bar, val in zip(bars, kpiValues):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() * 1.01,
        f"${val:,.0f}",
        ha="center", va="bottom", fontsize=9, fontweight="bold",
    )
ax.yaxis.set_major_formatter(mticker.FuncFormatter(formatMillions))
ax.set_title("KPI Summary", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Amount (USD)")
ax.spines[["top", "right"]].set_visible(False)
ax.yaxis.grid(True, linestyle="--", alpha=0.4)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(OUT_DIR + "01_kpi_summary.png", dpi=150)
plt.close()
print("Saved 01_kpi_summary.png")

# ── Chart 2: Sales by Store (top 10) ─────────────────────────────────────────
salesByStore = (
    sales.groupby("store_sk")["gross_amount"]
    .sum()
    .reset_index()
    .merge(stores[["store_sk", "store_name"]], on="store_sk")
    .sort_values("gross_amount", ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(12, 6))
ax.barh(salesByStore["store_name"][::-1], salesByStore["gross_amount"][::-1], color=PALETTE[0])
ax.xaxis.set_major_formatter(mticker.FuncFormatter(formatMillions))
ax.set_title("Top 10 Stores by Gross Sales", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Gross Sales (USD)")
ax.spines[["top", "right"]].set_visible(False)
ax.xaxis.grid(True, linestyle="--", alpha=0.4)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(OUT_DIR + "02_sales_by_store.png", dpi=150)
plt.close()
print("Saved 02_sales_by_store.png")

# ── Chart 3: Sales by Product Category ───────────────────────────────────────
salesByCategory = (
    sales.merge(products[["product_sk", "category"]], on="product_sk")
    .groupby("category")["gross_amount"]
    .sum()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(10, 6))
salesByCategory.plot(kind="bar", ax=ax, color=PALETTE[2], edgecolor="white")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(formatMillions))
ax.set_title("Gross Sales by Product Category", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Gross Sales (USD)")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=30)
ax.spines[["top", "right"]].set_visible(False)
ax.yaxis.grid(True, linestyle="--", alpha=0.4)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(OUT_DIR + "03_sales_by_category.png", dpi=150)
plt.close()
print("Saved 03_sales_by_category.png")

# ── Chart 4: Returns by Reason ───────────────────────────────────────────────
returnsByReason = returns.groupby("return_reason")["refund_amount"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    returnsByReason,
    labels=returnsByReason.index,
    autopct="%1.1f%%",
    colors=PALETTE,
    startangle=140,
    wedgeprops={"edgecolor": "white", "linewidth": 1.2},
)
for autotext in autotexts:
    autotext.set_fontsize(9)
ax.set_title("Returns by Reason", fontsize=14, fontweight="bold", pad=12)
plt.tight_layout()
plt.savefig(OUT_DIR + "04_returns_by_reason.png", dpi=150)
plt.close()
print("Saved 04_returns_by_reason.png")

# ── Chart 5: Avg Sales per Customer by Loyalty Tier ──────────────────────────
salesByCustomer = (
    sales.groupby("customer_sk")["gross_amount"]
    .sum()
    .reset_index()
    .merge(customers[["customer_sk", "loyalty_tier"]], on="customer_sk")
)
avgByTier = salesByCustomer.groupby("loyalty_tier")["gross_amount"].mean().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 5))
avgByTier.plot(kind="bar", ax=ax, color=PALETTE[4], edgecolor="white")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.set_title("Avg Sales per Customer by Loyalty Tier", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Avg Gross Sales (USD)")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0)
ax.spines[["top", "right"]].set_visible(False)
ax.yaxis.grid(True, linestyle="--", alpha=0.4)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(OUT_DIR + "05_avg_sales_by_loyalty_tier.png", dpi=150)
plt.close()
print("Saved 05_avg_sales_by_loyalty_tier.png")

# ── Chart 6: Net Sales vs Returns Comparison ─────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
compareLabels = ["Gross Sales", "Total Returns", "Net Sales"]
compareValues = [totalSales, totalReturns, netSales]
compareColors = [PALETTE[0], PALETTE[3], PALETTE[2]]
bars = ax.bar(compareLabels, compareValues, color=compareColors, edgecolor="white", linewidth=0.8, width=0.5)
for bar, val in zip(bars, compareValues):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() * 1.01,
        f"${val/1e6:.2f}M",
        ha="center", va="bottom", fontsize=10, fontweight="bold",
    )
ax.yaxis.set_major_formatter(mticker.FuncFormatter(formatMillions))
ax.set_title("Gross Sales vs Returns vs Net Sales", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Amount (USD)")
ax.spines[["top", "right"]].set_visible(False)
ax.yaxis.grid(True, linestyle="--", alpha=0.4)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(OUT_DIR + "06_net_sales_vs_returns.png", dpi=150)
plt.close()
print("Saved 06_net_sales_vs_returns.png")

print("\nAll visualisations saved to", OUT_DIR)

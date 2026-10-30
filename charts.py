"""Draws the charts (matplotlib) onto a Figure that is embedded in the Tkinter window."""

import pandas as pd

PALETTE = ["#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#64748B"]


def draw_charts(fig, df, month=None):
    """month=None -> all-time view (pie + month-by-month bars).
    month='YYYY-MM' -> monthly view (pie + day-by-day bars for that month)."""
    fig.clear()
    ax_pie = fig.add_subplot(211)
    ax_bar = fig.add_subplot(212)

    if df.empty:
        for ax in (ax_pie, ax_bar):
            ax.axis("off")
        ax_pie.text(0.5, 0.5, "No expenses yet.\nAdd one to see charts!",
                    ha="center", va="center", fontsize=13, color="#64748B")
        return

    # --- Pie chart: spending by category ---
    by_category = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(by_category))]
    ax_pie.pie(
        by_category.values,
        labels=by_category.index,
        autopct="%1.0f%%",
        startangle=90,
        colors=colors,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 9},
    )
    pie_title = "Spending by Category"
    if month:
        pie_title += f" ({pd.Period(month).strftime('%B %Y')})"
    ax_pie.set_title(pie_title, fontsize=12, fontweight="bold")

    # --- Bar chart ---
    if month:
        # Monthly view: one bar per day of that month
        period = pd.Period(month)
        days = list(range(1, period.days_in_month + 1))
        daily = df.groupby(df["Date"].dt.day)["Amount"].sum().reindex(days, fill_value=0)
        bars = ax_bar.bar(days, daily.values, color=PALETTE[0], width=0.7)
        labels = [f"{v:.0f}" if v > 0 else "" for v in daily.values]
        ax_bar.bar_label(bars, labels=labels, fontsize=7, padding=2)
        ax_bar.set_title("Daily Spending", fontsize=12, fontweight="bold")
        ax_bar.set_xlabel("Day of month")
        ax_bar.set_xticks(range(1, period.days_in_month + 1, 2))
    else:
        # All-time view: one bar per month
        monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()
        labels = [p.strftime("%b %Y") for p in monthly.index]
        bars = ax_bar.bar(labels, monthly.values, color=PALETTE[0], width=0.5)
        ax_bar.bar_label(bars, fmt="%.0f", fontsize=9, padding=3)
        ax_bar.set_title("Monthly Spending", fontsize=12, fontweight="bold")

    ax_bar.set_ylabel("Amount (Rs.)")
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)
    ax_bar.tick_params(axis="x", labelsize=8)

    fig.tight_layout(pad=2)
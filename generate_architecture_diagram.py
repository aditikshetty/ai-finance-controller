import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set canvas dimensions
fig, ax = plt.subplots(figsize=(14, 11), dpi=300)
ax.set_xlim(0, 14)
ax.set_ylim(0, 11)
ax.axis("off")

# Helper function for rounded styled boxes
def draw_box(x, y, w, h, title, subtitle, bg_color, border_color):
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.2,rounding_size=0.15",
        facecolor=bg_color, edgecolor=border_color, linewidth=2
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h - 0.35, title, ha="center", va="center",
            fontsize=11, fontweight="bold", color="#0f172a")
    ax.text(x + w / 2, y + (h - 0.35) / 2, subtitle, ha="center", va="center",
            fontsize=8.5, color="#334155", linespacing=1.4)

# Helper function for connecting arrows
def draw_arrow(x1, y1, x2, y2, label=""):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color="#475569", lw=2, shrinkA=3, shrinkB=3)
    )
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.15, label,
                ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1e293b",
                bbox=dict(boxstyle="square,pad=0.15", facecolor="#ffffff", edgecolor="none"))

# 1. Ingestion Layer
draw_box(
    2.5, 9.6, 9.0, 1.1,
    "DATA INGESTION LAYER",
    "ERP Invoices (synthetic_invoices.json) • Gateway Webhooks (synthetic_webhooks.json) • Bank UTR Feeds (synthetic_bank.json)",
    "#f1f5f9", "#94a3b8"
)

# Arrow to Tier 1
draw_arrow(7.0, 9.6, 7.0, 8.8)

# 2. Tier 1: Math Core
draw_box(
    2.0, 7.3, 10.0, 1.5,
    "TIER 1: DETERMINISTIC INTEGER-PAISA MATH CORE (fee_engine.py)",
    "• Fixed-Point Currency Scaling: 1 INR = 100 Paisa (Zero Binary Float Drift)\n• Multi-Tier Fee Deductions: Gateway MDR + 18% GST on MDR + Section 194-O TDS\n• Deterministic Equality Check: Expected Net Paisa == Actual Bank Deposit\n• Performance: 12,500+ TPS | Latency < 35ms",
    "#ecfdf5", "#10b981"
)

# Splits from Tier 1
draw_arrow(4.5, 7.3, 4.5, 5.8, "Clean Match (95%)")
draw_arrow(9.5, 7.3, 9.5, 6.2, "Unmatched / Discrepancy (5%)")

# Reconciled Box (Left Branch)
draw_box(
    1.5, 4.5, 4.2, 1.3,
    "RECONCILED GENERAL LEDGER",
    "• Verified Balance Sheet Postings\n• Zero Floating-Point Drift\n• Zero LLM Compute / Zero Token Cost",
    "#e0f2fe", "#0284c7"
)

# 3. Tier 2: ML Scorer (Right Branch)
draw_box(
    7.5, 5.1, 5.0, 1.1,
    "TIER 2: VECTORIZED ML SCORER (anomaly_ml_model.py)",
    "• Feature Vector: [Gross Paisa, Discrepancy, Dispute, Delay]\n• Scikit-Learn Model: Predicts Exposure Score (0.00 to 1.00)",
    "#fef3c7", "#f59e0b"
)

# Arrow Tier 2 -> Tier 3
draw_arrow(10.0, 5.1, 10.0, 4.4)

# 4. Tier 3: Agentic Auditor
draw_box(
    7.5, 3.4, 5.0, 1.0,
    "TIER 3: AGENTIC AUDITOR (llm_auditor.py)",
    "• Model: Gemini 3.6 Flash (Low Temperature)\n• Structured Pydantic Schema Validation",
    "#ede9fe", "#8b5cf6"
)

# Tool call arrows
draw_arrow(8.5, 3.4, 7.0, 2.7)
draw_arrow(11.5, 3.4, 11.5, 2.7)

# Microservice Tools
draw_box(
    4.5, 1.8, 4.3, 0.9,
    "query_dispute_portal",
    "DSP Reference IDs, Hold Amounts, 72h Proof-of-Delivery Window",
    "#fae8ff", "#c084fc"
)
draw_box(
    9.2, 1.8, 4.3, 0.9,
    "query_bank_clearing_schedule",
    "RBI Clearing Batches (NEFT/RTGS), T+2 Transit Schedules",
    "#fae8ff", "#c084fc"
)

# Collect into Exception Ledger
draw_arrow(6.65, 1.8, 7.0, 1.2)
draw_arrow(11.35, 1.8, 7.0, 1.2)

# 5. Output / Copilot Layer
draw_box(
    1.5, 0.1, 11.0, 1.1,
    "EXECUTIVE CONSUMPTION & CFO COPILOT (api.py + app.py)",
    "• Honest Exception Ledger (ord_1025 dispute hold, ord_1015 abandoned cart, ord_1035 transit delay)\n• Interactive Streamlit Dashboard & Dynamic Context-Grounded CFO Copilot (Exact Paisa Precision)",
    "#f8fafc", "#64748b"
)

plt.tight_layout()
plt.savefig("architecture_diagram.png", dpi=300, bbox_inches="tight")
plt.savefig("architecture_diagram.svg", bbox_inches="tight")
print("Architecture diagrams successfully saved as 'architecture_diagram.png' and 'architecture_diagram.svg'")
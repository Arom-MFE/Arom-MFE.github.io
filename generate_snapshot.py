#!/usr/bin/env python3
"""
Generate snapshot files for PCR analysis website.
This script runs the PCR analysis and saves:
- latest_table.json: All table data in JSON format
- latest_plot_pcr.png: PCR by expiry plot
- latest_plot_impulse.png: Hedging impulse timeline plot
- latest_plot_eventscore.png: Event score timeline plot
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Optional, Dict
import json
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# =========================
# CONFIG (SPY-only)
# =========================
SYMBOL = "SPY"
MIN_CALL_OI = 1000
MIN_CALL_VOL = 500
MIN_TOTAL_OI = 10_000
MAX_EXPIRIES: Optional[int] = None
PLOT = True
TOP_N = 5

# =========================
# Helpers
# =========================
def _to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")

def _safe_float(x) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

# =========================
# Core aggregation
# =========================
def per_expiry_totals(symbol: str, max_expiries: Optional[int] = None) -> pd.DataFrame:
    tk = yf.Ticker(symbol)
    expiries = list(tk.options or [])
    if not expiries:
        raise RuntimeError(f"No option expirations for {symbol}")
    
    if max_expiries is not None:
        expiries = expiries[:max_expiries]
    
    rows = []
    used = 0
    
    for exp in expiries:
        try:
            ch = tk.option_chain(exp)
            calls, puts = ch.calls, ch.puts
            
            c_vol = float(calls["volume"].fillna(0).sum())
            p_vol = float(puts["volume"].fillna(0).sum())
            c_oi = float(calls["openInterest"].fillna(0).sum())
            p_oi = float(puts["openInterest"].fillna(0).sum())
            
            vol_pcr = p_vol / c_vol if c_vol > 0 else np.nan
            oi_pcr = p_oi / c_oi if c_oi > 0 else np.nan
            
            rows.append({
                "Symbol": symbol,
                "Expiry": exp,
                "Put_Volume": int(round(p_vol)),
                "Call_Volume": int(round(c_vol)),
                "Volume_PCR": round(float(vol_pcr), 6) if np.isfinite(vol_pcr) else np.nan,
                "Put_OI": int(round(p_oi)),
                "Call_OI": int(round(c_oi)),
                "OI_PCR": round(float(oi_pcr), 6) if np.isfinite(oi_pcr) else np.nan,
                "Total_OI": int(round(p_oi + c_oi)),
            })
            used += 1
        except Exception as e:
            print(f"Error processing expiry {exp}: {e}")
            continue
    
    if not rows:
        raise RuntimeError(f"No chain data aggregated for {symbol}")
    
    df = pd.DataFrame(rows).sort_values("Expiry").reset_index(drop=True)
    df.attrs["Expiries_Used"] = used
    df.attrs["Expiries_Requested"] = len(expiries)
    return df

# =========================
# Signal layer
# =========================
def add_dte(df: pd.DataFrame, asof: Optional[date] = None) -> pd.DataFrame:
    out = df.copy()
    d0 = asof or date.today()
    exp = pd.to_datetime(out["Expiry"], errors="coerce").dt.date
    out["DTE"] = exp.map(lambda x: (x - d0).days if x is not None else np.nan)
    out["DTE"] = _to_num(out["DTE"])
    return out

def add_flow_vs_positioning(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    v = _to_num(out["Volume_PCR"])
    oi = _to_num(out["OI_PCR"])
    out["Divergence_Vol_minus_OI"] = (v - oi).round(6)
    out["Impulse_Vol_over_OI"] = np.where(
        (oi > 0) & np.isfinite(oi) & np.isfinite(v),
        (v / oi),
        np.nan,
    )
    out["Impulse_Vol_over_OI"] = _to_num(out["Impulse_Vol_over_OI"]).round(6)
    return out

def add_quality_flags(
    df: pd.DataFrame,
    min_call_oi: int = MIN_CALL_OI,
    min_call_vol: int = MIN_CALL_VOL,
    min_total_oi: int = MIN_TOTAL_OI,
) -> pd.DataFrame:
    out = df.copy()
    call_oi = _to_num(out["Call_OI"])
    call_vol = _to_num(out["Call_Volume"])
    tot_oi = _to_num(out["Total_OI"])
    ok = (call_oi >= min_call_oi) & (call_vol >= min_call_vol) & (tot_oi >= min_total_oi)
    out["Quality_OK"] = ok.fillna(False)
    return out

def add_event_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    tot_oi = _to_num(out["Total_OI"]).fillna(0.0)
    denom = float(tot_oi.sum())
    if denom <= 0:
        out["EventScore_OIshare_x_OI_PCR"] = np.nan
        return out
    oi_pcr = _to_num(out["OI_PCR"])
    share = tot_oi / denom
    out["EventScore_OIshare_x_OI_PCR"] = (share * oi_pcr).round(8)
    return out

def compute_concentration_metrics(df: pd.DataFrame, top_k: int = 3) -> Dict[str, float]:
    total_oi = _to_num(df["Total_OI"]).fillna(0.0)
    sum_total_oi = float(total_oi.sum())
    if sum_total_oi <= 0:
        return {"Sum_Total_OI": 0, f"Top{top_k}_TotalOIShare": np.nan}
    share = total_oi / sum_total_oi
    top_share = float(share.sort_values(ascending=False).head(top_k).sum())
    return {
        "Sum_Total_OI": int(round(sum_total_oi)),
        f"Top{top_k}_TotalOIShare": round(top_share, 6),
    }

def enrich_per_expiry(symbol: str, max_expiries: Optional[int] = None) -> pd.DataFrame:
    base = per_expiry_totals(symbol, max_expiries=max_expiries)
    df = add_dte(base)
    df = add_flow_vs_positioning(df)
    df = add_quality_flags(df, MIN_CALL_OI, MIN_CALL_VOL, MIN_TOTAL_OI)
    df = add_event_score(df)
    df.attrs.update(base.attrs)
    return df

# =========================
# Buckets + bucket concentration scoring
# =========================
def bucket_term_structure(df: pd.DataFrame, require_quality_ok: bool = True) -> pd.DataFrame:
    buckets = [
        ("Short_1_20", 1, 20),
        ("Mid_21_60", 21, 60),
        ("Long_61_120", 61, 120),
    ]

    t = df.copy()
    if require_quality_ok and "Quality_OK" in t.columns:
        t = t[t["Quality_OK"] == True].copy()

    t["DTE"] = _to_num(t["DTE"])
    t["Put_OI"] = _to_num(t["Put_OI"])
    t["Call_OI"] = _to_num(t["Call_OI"])
    t["Put_Volume"] = _to_num(t["Put_Volume"])
    t["Call_Volume"] = _to_num(t["Call_Volume"])
    t["Total_OI"] = _to_num(t["Total_OI"]).fillna(0.0)

    denom_total_oi = float(t["Total_OI"].sum())

    rows = []
    for name, lo, hi in buckets:
        w = t[(t["DTE"] >= lo) & (t["DTE"] <= hi)].copy()

        put_oi = float(w["Put_OI"].sum())
        call_oi = float(w["Call_OI"].sum())
        put_vol = float(w["Put_Volume"].sum())
        call_vol = float(w["Call_Volume"].sum())
        total_oi = float(w["Total_OI"].sum())

        oi_pcr = put_oi / call_oi if call_oi > 0 else np.nan
        vol_pcr = put_vol / call_vol if call_vol > 0 else np.nan
        oi_share = (total_oi / denom_total_oi) if denom_total_oi > 0 else np.nan

        rows.append(
            {
                "Bucket": name,
                "DTE_Min": lo,
                "DTE_Max": hi,
                "Sum_Put_OI": int(round(put_oi)),
                "Sum_Call_OI": int(round(call_oi)),
                "Bucket_OI_PCR": round(float(oi_pcr), 6) if np.isfinite(oi_pcr) else np.nan,
                "Sum_Put_Volume": int(round(put_vol)),
                "Sum_Call_Volume": int(round(call_vol)),
                "Bucket_Volume_PCR": round(float(vol_pcr), 6) if np.isfinite(vol_pcr) else np.nan,
                "Bucket_TotalOI": int(round(total_oi)),
                "Bucket_TotalOI_Share": round(float(oi_share), 6) if np.isfinite(oi_share) else np.nan,
            }
        )

    out = pd.DataFrame(rows)

    # --- Bucket concentration scoring ---
    # Score = bucket OI share * bucket OI_PCR
    out["Bucket_Concentration_Score"] = _to_num(out["Bucket_TotalOI_Share"]) * _to_num(out["Bucket_OI_PCR"])

    denom = float(_to_num(out["Bucket_Concentration_Score"]).sum())
    out["Bucket_Concentration_Share"] = (
        (_to_num(out["Bucket_Concentration_Score"]) / denom) if denom > 0 else np.nan
    )

    # Nice formatting
    out["Bucket_Concentration_Score"] = _to_num(out["Bucket_Concentration_Score"]).round(8)
    out["Bucket_Concentration_Share"] = _to_num(out["Bucket_Concentration_Share"]).round(6)

    return out

# =========================
# Tables
# =========================
def top_expiries_by_oi_pcr(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    out = df.copy()
    out["OI_PCR"] = _to_num(out["OI_PCR"])
    out = out[out["OI_PCR"].notna()].copy()
    if out.empty:
        return out
    out = out.sort_values("OI_PCR", ascending=False).head(top_n)
    return out[[
        "Symbol", "Expiry", "OI_PCR", "Volume_PCR",
        "Put_OI", "Call_OI", "Total_OI", "Put_Volume", "Call_Volume",
    ]]

def top_by_metric(
    df: pd.DataFrame,
    metric: str,
    top_n: int = 5,
    descending: bool = True,
    require_quality_ok: bool = True,
) -> pd.DataFrame:
    if metric not in df.columns:
        raise ValueError(f"Metric '{metric}' not found")
    t = df.copy()
    if require_quality_ok and "Quality_OK" in t.columns:
        t = t[t["Quality_OK"] == True].copy()
    t[metric] = _to_num(t[metric])
    t = t[t[metric].notna()].copy()
    if t.empty:
        return t
    t = t.sort_values(metric, ascending=not descending).head(top_n)
    cols = [
        "Symbol", "Expiry", "DTE", "Volume_PCR", "OI_PCR",
        "Divergence_Vol_minus_OI", "Impulse_Vol_over_OI",
        "EventScore_OIshare_x_OI_PCR", "Put_OI", "Call_OI",
        "Total_OI", "Put_Volume", "Call_Volume", "Quality_OK",
    ]
    cols = [c for c in cols if c in t.columns]
    return t[cols]

def _per_expiry_table(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "Symbol", "Expiry", "DTE", "Put_Volume", "Call_Volume",
        "Volume_PCR", "Put_OI", "Call_OI", "OI_PCR", "Total_OI",
        "Divergence_Vol_minus_OI", "Impulse_Vol_over_OI",
        "EventScore_OIshare_x_OI_PCR", "Quality_OK",
    ]
    cols = [c for c in cols if c in df.columns]
    return df[cols].copy()

# =========================
# Plots
# =========================
def plot_pcrs_by_expiry(df: pd.DataFrame, title: Optional[str] = None) -> None:
    xlabels = df["Expiry"].astype(str).values
    oi = _to_num(df["OI_PCR"]).values
    vol = _to_num(df["Volume_PCR"]).values
    x = np.arange(len(xlabels))
    width = 0.42
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width / 2, vol, width=width, alpha=0.75, label="Volume_PCR")
    ax.bar(x + width / 2, oi, width=width, alpha=0.75, label="OI_PCR")
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation=45, ha="right")
    ax.set_xlabel("Expiration Date")
    ax.set_ylabel("Put/Call Ratio (PCR)")
    ax.set_title(title or f"{df['Symbol'].iloc[0]}: PCR by Expiry (Volume vs Open Interest)")
    ax.axhline(1.0, linestyle="--", linewidth=1, alpha=0.6)
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend()
    plt.tight_layout()
    plt.savefig('latest_plot_pcr.png', dpi=100, bbox_inches='tight')
    plt.close()

def plot_impulse_timeline(df: pd.DataFrame, top_n: int = 5, require_quality_ok: bool = True) -> None:
    t = df.copy()
    if require_quality_ok and "Quality_OK" in t.columns:
        t = t[t["Quality_OK"] == True].copy()
    t["DTE"] = _to_num(t["DTE"])
    t["Impulse_Vol_over_OI"] = _to_num(t["Impulse_Vol_over_OI"])
    t = t[t["DTE"].notna() & t["Impulse_Vol_over_OI"].notna()].copy()
    if t.empty:
        return
    t = t.sort_values("DTE").reset_index(drop=True)
    xlabels = t["Expiry"].astype(str).values
    y = t["Impulse_Vol_over_OI"].values
    x = np.arange(len(xlabels))
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(x, y, alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation=45, ha="right")
    ax.set_xlabel("Expiration Date")
    ax.set_ylabel("Impulse = Volume_PCR / OI_PCR")
    ax.set_title(f"{df['Symbol'].iloc[0]}: Hedging Impulse by Expiry (Quality-filtered)")
    ax.axhline(1.0, linestyle="--", linewidth=1, alpha=0.6)
    ax.grid(True, linestyle="--", alpha=0.35)
    top = t.sort_values("Impulse_Vol_over_OI", ascending=False).head(top_n)
    for _, r in top.iterrows():
        idx = int(r.name)
        ax.annotate(
            f"{r['Impulse_Vol_over_OI']:.2f}\nDTE={int(r['DTE'])}",
            (idx, r["Impulse_Vol_over_OI"]),
            textcoords="offset points",
            xytext=(0, 6),
            ha="center",
            fontsize=8,
        )
    plt.tight_layout()
    plt.savefig('latest_plot_impulse.png', dpi=100, bbox_inches='tight')
    plt.close()

def plot_eventscore_timeline(df: pd.DataFrame, top_n: int = 5, require_quality_ok: bool = True) -> None:
    t = df.copy()
    if require_quality_ok and "Quality_OK" in t.columns:
        t = t[t["Quality_OK"] == True].copy()
    t["DTE"] = _to_num(t["DTE"])
    t["EventScore_OIshare_x_OI_PCR"] = _to_num(t["EventScore_OIshare_x_OI_PCR"])
    t = t[t["DTE"].notna() & t["EventScore_OIshare_x_OI_PCR"].notna()].copy()
    if t.empty:
        return
    t = t.sort_values("DTE").reset_index(drop=True)
    xlabels = t["Expiry"].astype(str).values
    y = t["EventScore_OIshare_x_OI_PCR"].values
    x = np.arange(len(xlabels))
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(x, y, alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation=45, ha="right")
    ax.set_xlabel("Expiration Date")
    ax.set_ylabel("EventScore = (TotalOI share) × OI_PCR")
    ax.set_title(f"{df['Symbol'].iloc[0]}: Event Score by Expiry (Quality-filtered)")
    ax.grid(True, linestyle="--", alpha=0.35)
    top = t.sort_values("EventScore_OIshare_x_OI_PCR", ascending=False).head(top_n)
    for _, r in top.iterrows():
        idx = int(r.name)
        ax.annotate(
            f"{r['EventScore_OIshare_x_OI_PCR']:.4g}\nDTE={int(r['DTE'])}",
            (idx, r["EventScore_OIshare_x_OI_PCR"]),
            textcoords="offset points",
            xytext=(0, 6),
            ha="center",
            fontsize=8,
        )
    plt.tight_layout()
    plt.savefig('latest_plot_eventscore.png', dpi=100, bbox_inches='tight')
    plt.close()

# =========================
# Main
# =========================
def main():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nPCR by Expiry Signals Report @ {ts}\n")
    
    # Run analysis
    df = enrich_per_expiry(SYMBOL, max_expiries=MAX_EXPIRIES)
    
    # Generate tables
    top_oi = top_expiries_by_oi_pcr(df, top_n=TOP_N)
    top_impulse = top_by_metric(df, "Impulse_Vol_over_OI", top_n=TOP_N, descending=True, require_quality_ok=True)
    top_eventscore = top_by_metric(df, "EventScore_OIshare_x_OI_PCR", top_n=TOP_N, descending=True, require_quality_ok=True)
    conc = compute_concentration_metrics(df, top_k=3)
    per_expiry = _per_expiry_table(df)
    
    # Generate bucket analysis
    buckets = bucket_term_structure(df, require_quality_ok=True)
    
    # Merge signals into top_oi
    if not top_oi.empty:
        top_oi = top_oi.merge(
            df[["Expiry", "DTE", "Divergence_Vol_minus_OI", "Impulse_Vol_over_OI",
                "EventScore_OIshare_x_OI_PCR", "Quality_OK"]],
            on="Expiry",
            how="left",
        )
    
    # Save JSON data
    output_data = {
        "timestamp": ts,
        "symbol": SYMBOL,
        "expiries_used": df.attrs.get("Expiries_Used"),
        "expiries_requested": df.attrs.get("Expiries_Requested"),
        "top_n": TOP_N,
        "top_oi_pcr": top_oi.to_dict('records') if not top_oi.empty else [],
        "top_impulse": top_impulse.to_dict('records') if not top_impulse.empty else [],
        "top_eventscore": top_eventscore.to_dict('records') if not top_eventscore.empty else [],
        "concentration_summary": conc,
        "bucket_concentration": buckets.to_dict('records'),
        "bucket_term_structure": buckets.to_dict('records'),
        "per_expiry_table": per_expiry.to_dict('records'),
    }
    
    with open('latest_table.json', 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    # Generate plots
    if PLOT:
        plot_pcrs_by_expiry(df, title=f"{SYMBOL}: PCR per Expiry (Volume_PCR vs OI_PCR)")
        plot_impulse_timeline(df, top_n=TOP_N, require_quality_ok=True)
        plot_eventscore_timeline(df, top_n=TOP_N, require_quality_ok=True)
    
    print(f"\n✓ Snapshot files generated:")
    print(f"  - latest_table.json")
    print(f"  - latest_plot_pcr.png")
    print(f"  - latest_plot_impulse.png")
    print(f"  - latest_plot_eventscore.png")

if __name__ == "__main__":
    main()

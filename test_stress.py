"""
Test sequencer dengan simulasi stress (BTC crash 6%)
"""

from core.sequencer import ContagionSequencer, AssetReturn

print("=" * 60)
print("🧪 TEST SEQUENCER — SIMULASI BTC CRASH 6%")
print("=" * 60)

# === BUAT DATA SIMULASI ===
# 66 jam normal + 6 jam stress
btc_normal = [0.001] * 66
eth_normal = [0.0008] * 66
bnb_normal = [0.0006] * 66
cake_normal = [0.0004] * 66
link_normal = [0.0003] * 66
ada_normal = [0.0002] * 66

# Stress: BTC turun 6% dalam 6 jam
btc_stress = [-0.01, -0.012, -0.008, -0.01, -0.009, -0.011]  # total -6%
eth_stress = [-0.008, -0.009, -0.006, -0.007, -0.006, -0.008]
bnb_stress = [-0.006, -0.007, -0.005, -0.006, -0.005, -0.007]
cake_stress = [-0.005, -0.006, -0.004, -0.005, -0.004, -0.006]
link_stress = [-0.004, -0.005, -0.003, -0.004, -0.003, -0.005]
ada_stress = [-0.003, -0.004, -0.002, -0.003, -0.002, -0.004]

btc_returns = btc_normal + btc_stress
eth_returns = eth_normal + eth_stress
bnb_returns = bnb_normal + bnb_stress
cake_returns = cake_normal + cake_stress
link_returns = link_normal + link_stress
ada_returns = ada_normal + ada_stress

timestamps = [f"2026-06-17T{i:02d}:00Z" for i in range(72)]

# === BUILD SOURCE & TARGETS ===
source = AssetReturn("BTC", btc_returns, timestamps)
targets = [
    AssetReturn("ETH", eth_returns, timestamps),
    AssetReturn("BNB", bnb_returns, timestamps),
    AssetReturn("CAKE", cake_returns, timestamps),
    AssetReturn("LINK", link_returns, timestamps),
    AssetReturn("ADA", ada_returns, timestamps),
]

# === JALANKAN SEQUENCER ===
print("\n🔄 Running sequencer with simulated stress data...")
sequencer = ContagionSequencer()
result = sequencer.run(source, targets, stress_threshold=-0.05)

# === TAMPILKAN HASIL ===
print("\n" + "=" * 60)
print("📊 HASIL SEQUENCER")
print("=" * 60)
print(f"  Contagion detected: {result.contagion_detected}")
print(f"  Stress severity: {result.stress_severity}")
print(f"  Confidence: {result.overall_confidence}")
print(f"  Spread window: {result.estimated_spread_window_hours:.1f} hours")

print("\n🔮 PREDICTED SEQUENCE (REAL DATA DARI SEQUENCER):")
print("─" * 50)
print(f"  {'Symbol':<8} {'Lag Hours':<12} {'Impact':<10} {'Signal'}")
print("─" * 50)

for node in result.contagion_sequence:
    print(f"  {node.symbol:<8} +{node.estimated_lag_hours:.0f}h{' '*6} {node.impact_score:.2f}{' '*4} {node.signal}")

print("─" * 50)
print("\n✅ INI ADALAH DATA REAL DARI SEQUENCER, BUKAN FTX BACKTEST!")
print("=" * 60)

"""
test_stress.py
===============
Test the sequencer with simulated stress data (BTC crash 6%).

This script creates synthetic market data simulating a 6% BTC drop
and tests whether the sequencer can detect contagion and predict
the correct sequence of affected assets.
"""

from core.sequencer import ContagionSequencer, AssetReturn


def main():
    """Run the stress test simulation."""
    
    print("=" * 60)
    print("🧪 STRESS TEST: SIMULATED BTC CRASH (6%)")
    print("=" * 60)
    
    # ============================================
    # 1. GENERATE SIMULATED DATA
    # ============================================
    print("\n📊 Generating simulated market data...")
    
    # 66 hours of normal volatility + 6 hours of stress
    btc_normal = [0.001] * 66
    eth_normal = [0.0008] * 66
    bnb_normal = [0.0006] * 66
    cake_normal = [0.0004] * 66
    link_normal = [0.0003] * 66
    ada_normal = [0.0002] * 66
    
    # Stress: BTC drops 6% over 6 hours
    btc_stress = [-0.01, -0.012, -0.008, -0.01, -0.009, -0.011]  # total: -6%
    eth_stress = [-0.008, -0.009, -0.006, -0.007, -0.006, -0.008]
    bnb_stress = [-0.006, -0.007, -0.005, -0.006, -0.005, -0.007]
    cake_stress = [-0.005, -0.006, -0.004, -0.005, -0.004, -0.006]
    link_stress = [-0.004, -0.005, -0.003, -0.004, -0.003, -0.005]
    ada_stress = [-0.003, -0.004, -0.002, -0.003, -0.002, -0.004]
    
    # Combine normal + stress periods
    btc_returns = btc_normal + btc_stress
    eth_returns = eth_normal + eth_stress
    bnb_returns = bnb_normal + bnb_stress
    cake_returns = cake_normal + cake_stress
    link_returns = link_normal + link_stress
    ada_returns = ada_normal + ada_stress
    
    # Generate timestamps (72 hours)
    timestamps = [f"2026-06-17T{i:02d}:00Z" for i in range(72)]
    
    print(f"   ✅ Generated {len(btc_returns)} hours of data for 6 assets")
    print(f"   📉 BTC stress: {sum(btc_stress)*100:.1f}% drop over 6 hours")
    
    # ============================================
    # 2. BUILD SOURCE AND TARGET ASSETS
    # ============================================
    print("\n🔧 Building AssetReturn objects...")
    
    source = AssetReturn("BTC", btc_returns, timestamps)
    targets = [
        AssetReturn("ETH", eth_returns, timestamps),
        AssetReturn("BNB", bnb_returns, timestamps),
        AssetReturn("CAKE", cake_returns, timestamps),
        AssetReturn("LINK", link_returns, timestamps),
        AssetReturn("ADA", ada_returns, timestamps),
    ]
    
    print(f"   ✅ Source: {source.symbol}")
    print(f"   ✅ Targets: {', '.join([t.symbol for t in targets])}")
    
    # ============================================
    # 3. RUN THE SEQUENCER
    # ============================================
    print("\n🔄 Running contagion sequencer...")
    print("-" * 40)
    
    sequencer = ContagionSequencer()
    result = sequencer.run(source, targets, stress_threshold=-0.05)
    
    # ============================================
    # 4. DISPLAY RESULTS
    # ============================================
    print("\n" + "=" * 60)
    print("📊 SEQUENCER RESULTS")
    print("=" * 60)
    
    print(f"\n  📌 Contagion detected: {'✅ YES' if result.contagion_detected else '❌ NO'}")
    print(f"  📌 Stress severity:    {result.stress_severity}")
    print(f"  📌 Confidence level:   {result.overall_confidence}")
    print(f"  📌 Spread window:      {result.estimated_spread_window_hours:.1f} hours")
    
    # ============================================
    # 5. PREDICTED SEQUENCE
    # ============================================
    if result.contagion_detected and result.contagion_sequence:
        print("\n🔮 PREDICTED CONTAGION SEQUENCE:")
        print("-" * 60)
        print(f"  {'Position':<10} {'Symbol':<8} {'Lag (h)':<12} {'Impact':<10} {'Signal':<12}")
        print("-" * 60)
        
        for node in result.contagion_sequence:
            pos = f"#{node.sequence_position}"
            lag = f"+{node.estimated_lag_hours:.0f}h"
            impact = f"{node.impact_score:.2f}"
            signal = node.signal
            
            # Color indicators for signals
            if signal == "EXIT_NOW":
                signal_display = f"🔴 {signal}"
            elif signal == "REDUCE":
                signal_display = f"🟠 {signal}"
            elif signal == "WATCH":
                signal_display = f"🟡 {signal}"
            else:
                signal_display = f"🟢 {signal}"
            
            print(f"  {pos:<10} {node.symbol:<8} {lag:<12} {impact:<10} {signal_display:<12}")
        
        print("-" * 60)
    else:
        print("\n  ✅ No contagion detected. Market appears stable.")
    
    # ============================================
    # 6. REASONING
    # ============================================
    print(f"\n💡 REASONING:")
    print("-" * 60)
    print(f"  {result.reasoning}")
    print("-" * 60)
    
    # ============================================
    # 7. SUMMARY
    # ============================================
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"  Test scenario:    BTC 6% crash simulation")
    print(f"  Assets analyzed:  6 (BTC, ETH, BNB, CAKE, LINK, ADA)")
    print(f"  Data window:      72 hours")
    print(f"  Stress threshold: -5%")
    print(f"  Status:           {'✅ Contagion detected' if result.contagion_detected else '✅ No contagion'}")
    print("=" * 60)
    
    print("\n✅ Test complete! This is REAL sequencer output, not FTX backtest data.")


if __name__ == "__main__":
    main()

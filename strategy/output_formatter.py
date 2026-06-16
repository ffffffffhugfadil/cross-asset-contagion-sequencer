"""
strategy/output_formatter.py
============================
Formats sequencer output for LLM consumption.

Creates clean, structured JSON output with reasoning
that is easy for AI agents to parse and act upon.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime


def format_for_llm(
    contagion_detected: bool,
    source_asset: str,
    stress_severity: str,
    contagion_sequence: List[Dict],
    overall_confidence: str,
    estimated_spread_window_hours: float,
    reasoning: str,
    data_quality_flags: List[str],
    additional_context: Optional[Dict] = None,
) -> Dict:
    """
    Format sequencer output for LLM consumption.
    
    Returns a clean, well-structured dictionary with:
    - Summary for quick decision making
    - Detailed sequence for analysis
    - Reasoning for transparency
    """
    # Build summary
    if contagion_detected:
        summary = (
            f"{source_asset} stress detected ({stress_severity}). "
            f"Contagion predicted across {len(contagion_sequence)} assets "
            f"over {estimated_spread_window_hours:.1f} hours. "
            f"Confidence: {overall_confidence}."
        )
    else:
        summary = f"No contagion detected from {source_asset}. Market appears stable."
    
    # Build action items
    action_items = []
    for asset in contagion_sequence:
        action_items.append({
            'asset': asset.get('symbol'),
            'action': asset.get('signal'),
            'urgency_hours': asset.get('estimated_lag_hours', 0),
            'reason': f"Expected impact score: {asset.get('impact_score', 0):.2f}",
        })
    
    output = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'summary': summary,
        'contagion_detected': contagion_detected,
        'source_asset': source_asset,
        'stress_severity': stress_severity,
        'overall_confidence': overall_confidence,
        'estimated_spread_window_hours': round(estimated_spread_window_hours, 1),
        'contagion_sequence': [
            {
                'symbol': a.get('symbol'),
                'position': a.get('sequence_position'),
                'lag_hours': round(a.get('estimated_lag_hours', 0), 1),
                'impact_score': round(a.get('impact_score', 0), 3),
                'signal': a.get('signal'),
                'confidence': round(a.get('confidence', 0), 3),
                'correlation': round(a.get('correlation_at_lag', 0), 3),
            }
            for a in contagion_sequence
        ],
        'action_items': action_items,
        'reasoning': reasoning,
        'data_quality_flags': data_quality_flags,
    }
    
    if additional_context:
        output['context'] = additional_context
    
    return output


def format_as_markdown(output: Dict) -> str:
    """
    Format output as human-readable markdown.
    
    Useful for displaying in chat interfaces or reports.
    """
    lines = []
    
    lines.append("## Cross-Asset Contagion Sequencer Output\n")
    
    if output.get('contagion_detected'):
        lines.append(f"⚠️ **CONTAGION DETECTED** - Source: {output['source_asset']}")
        lines.append(f"   Severity: {output['stress_severity']} | Confidence: {output['overall_confidence']}\n")
        lines.append(f"**Spread Window:** {output['estimated_spread_window_hours']} hours\n")
        lines.append("### Predicted Sequence\n")
        
        lines.append("| Position | Asset | Lag (h) | Impact | Signal |")
        lines.append("|----------|-------|---------|--------|--------|")
        
        for a in output.get('contagion_sequence', []):
            lines.append(f"| {a['position']} | {a['symbol']} | {a['lag_hours']} | {a['impact_score']} | {a['signal']} |")
        
        lines.append("\n### Action Items\n")
        for item in output.get('action_items', []):
            lines.append(f"- **{item['asset']}**: {item['action']} (within {item['urgency_hours']}h)")
        
        lines.append(f"\n### Reasoning\n{output['reasoning']}")
    else:
        lines.append(f"✅ **No Contagion Detected** from {output['source_asset']}")
        lines.append(f"\n{output.get('summary', 'Market appears stable.')}")
    
    if output.get('data_quality_flags'):
        lines.append("\n### Data Quality Notes\n")
        for flag in output['data_quality_flags']:
            lines.append(f"- ⚠️ {flag}")
    
    return '\n'.join(lines)


def to_json_string(output: Dict, indent: int = 2) -> str:
    """
    Convert output dictionary to JSON string.
    
    Args:
        output: Output dictionary from format_for_llm
        indent: JSON indentation level
    
    Returns:
        Pretty-printed JSON string
    """
    return json.dumps(output, indent=indent)


def compress_for_agent(output: Dict) -> Dict:
    """
    Create a minimal version for lightweight agent consumption.
    
    Removes verbose fields, keeps only essentials for decision making.
    """
    return {
        'detected': output.get('contagion_detected', False),
        'source': output.get('source_asset'),
        'severity': output.get('stress_severity'),
        'confidence': output.get('overall_confidence'),
        'actions': [
            {'asset': a['symbol'], 'action': a['signal'], 'urgency_hours': a['lag_hours']}
            for a in output.get('contagion_sequence', [])
        ],
        'reasoning_short': output.get('reasoning', '')[:200],
    }

"""
Output format utilities for CLI
"""

import json
from typing import Any, Dict, List
from ..utils.logger import get_logger


def format_output_json(data: Any, pretty: bool = True) -> str:
    """Format output as JSON"""
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def format_output_table(
    headers: List[str],
    rows: List[List[Any]],
    col_widths: List[int] = None
) -> str:
    """Format output as table

    Args:
        headers: Column headers
        rows: Data rows
        col_widths: Optional column widths (auto-calculate if None)

    Returns:
        Formatted table string
    """
    if col_widths is None:
        # Auto-calculate column widths
        col_widths = []
        for i in range(len(headers)):
            max_len = len(str(headers[i]))
            for row in rows:
                if i < len(row):
                    max_len = max(max_len, len(str(row[i])))
            col_widths.append(max_len + 2)

    # Build separator line
    separator = "+" + "+".join("-" * w for w in col_widths) + "+"

    # Build header row
    header_row = "|" + "|".join(
        f" {str(headers[i]).ljust(col_widths[i] - 1)}"
        for i in range(len(headers))
    ) + "|"

    # Build data rows
    data_rows = []
    for row in rows:
        cells = []
        for i in range(len(col_widths)):
            if i < len(row):
                cells.append(f" {str(row[i]).ljust(col_widths[i] - 1)}")
            else:
                cells.append(" " * col_widths[i])
        data_rows.append("|" + "|".join(cells) + "|")

    # Combine all parts
    table_parts = [separator, header_row, separator]
    table_parts.extend(data_rows)
    table_parts.append(separator)

    return "\n".join(table_parts)


def format_output_simple(data: Any) -> str:
    """Format output as simple text"""
    if isinstance(data, dict):
        return "\n".join(f"{k}: {v}" for k, v in data.items())
    elif isinstance(data, (list, tuple)):
        return "\n".join(str(item) for item in data)
    else:
        return str(data)


def get_output_formatter(output_format: str):
    """Get output formatter function

    Args:
        output_format: Output format (json, table, simple)

    Returns:
        Formatter function
    """
    formatters = {
        "json": format_output_json,
        "table": format_output_table,
        "simple": format_output_simple,
    }

    return formatters.get(output_format.lower(), format_output_simple)


def format_provider_list(providers: Dict[str, Dict], output_format: str = "simple") -> str:
    """Format provider list for output

    Args:
        providers: Provider data
        output_format: Output format

    Returns:
        Formatted string
    """
    if output_format == "json":
        return format_output_json(providers)

    elif output_format == "table":
        headers = ["ID", "名称", "套餐", "优先级", "状态"]
        rows = []
        for provider_id, provider in providers.items():
            rows.append([
                provider_id,
                provider.get("name", "N/A"),
                provider.get("tier", "N/A"),
                provider.get("priority", 0),
                "启用" if provider.get("enabled", False) else "禁用"
            ])
        return format_output_table(headers, rows)

    else:  # simple
        lines = []
        for provider_id, provider in providers.items():
            status = "✅" if provider.get("enabled", False) else "❌"
            lines.append(f"{status} {provider_id}: {provider.get('name', 'N/A')}")
        return "\n".join(lines)


def format_quota_data(quota_data: Dict[str, Dict], output_format: str = "simple") -> str:
    """Format quota data for output

    Args:
        quota_data: Quota data
        output_format: Output format

    Returns:
        Formatted string
    """
    if output_format == "json":
        return format_output_json(quota_data)

    elif output_format == "table":
        headers = ["提供商", "已用", "限制", "剩余", "使用率"]
        rows = []
        for provider_id, quota_info in quota_data.items():
            used = quota_info.get("used", 0)
            limit = quota_info.get("limit", 0)
            remaining = limit - used if limit else 0
            usage_percentage = (used / limit * 100) if limit else 0

            rows.append([
                provider_id,
                str(used),
                str(limit),
                str(remaining),
                f"{usage_percentage:.1f}%"
            ])
        return format_output_table(headers, rows)

    else:  # simple
        lines = []
        for provider_id, quota_info in quota_data.items():
            used = quota_info.get("used", 0)
            limit = quota_info.get("limit", 0)
            remaining = limit - used if limit else 0
            usage_percentage = (used / limit * 100) if limit else 0

            lines.append(f"{provider_id}: {usage_percentage:.1f}% ({remaining} 剩余)")
        return "\n".join(lines)

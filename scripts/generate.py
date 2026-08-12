#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SurgeRuleSet - 规则生成脚本
自动拉取、清洗、去重并生成 Proxy / Direct / Reject 三类规则
"""

import os
import re
import base64
import json
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_DIR = os.path.join(ROOT_DIR, "rules")
MODULES_DIR = os.path.join(ROOT_DIR, "modules")

TIMEOUT = 30
UA = "Mozilla/5.0 (compatible; SurgeRuleSet/1.0; +https://github.com/Zheng-JD/SurgeRuleSet)"

SOURCES = {
    "proxy": [
        {"name": "gfwlist", "url": "https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt", "type": "gfwlist"},
        {"name": "loyalsoldier-gfw", "url": "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/gfw.txt", "type": "domain-set"},
        {"name": "loyalsoldier-proxy", "url": "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/proxy.txt", "type": "domain-set"},
    ],
    "direct": [
        {"name": "loyalsoldier-direct", "url": "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/direct.txt", "type": "domain-set"},
    ],
    "reject": [
        {"name": "loyalsoldier-reject", "url": "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/reject.txt", "type": "domain-set"},
        {"name": "pgl-yoyo", "url": "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=nohtml&showintro=0&mimetype=plaintext", "type": "plain-domain"},
    ],
}

REJECT_WHITELIST = {
    "apple.com", "icloud.com", "mzstatic.com",
    "microsoft.com", "windows.com", "office.com", "live.com", "office365.com",
    "github.com", "githubusercontent.com", "githubassets.com",
    "jsdelivr.net", "cloudflare.com", "cdnjs.cloudflare.com",
    "gstatic.com", "googleapis.com", "google.com", "googleusercontent.com",
    "youtube.com", "ytimg.com",
    "amazon.com", "amazonaws.com",
}

# 从 Proxy 中强制排除的 Apple 相关域名
APPLE_DOMAINS = {
    "apple.com", "icloud.com", "icloud.com.cn", "mzstatic.com", "cdn-apple.com",
    "apple-cloudkit.com", "apple-livephotoskit.com", "apple-mapkit.com",
    "icloud-content.com", "icloud-sandbox.com", "me.com", "mac.com",
    "apple-dns.net", "aaplimg.com",
}

def is_apple_domain(domain: str) -> bool:
    """判断是否为 Apple 相关域名，用于从 Proxy 中排除"""
    d = domain.lower()
    for root in APPLE_DOMAINS:
        if d == root or d.endswith("." + root):
            return True
    # 更精确的关键词匹配
    if (d.startswith("apple.") or d.startswith("apple-") or
        ".apple." in d or d.endswith(".apple") or
        "icloud" in d or "mzstatic" in d or "cdn-apple" in d or
        d.startswith("aaplimg")):
        return True
    return False

def fetch_url(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def is_valid_domain(domain: str) -> bool:
    if not domain or len(domain) > 253:
        return False
    if domain.startswith(".") or domain.endswith("."):
        return False
    if not re.match(r"^[a-z0-9]([a-z0-9\-\.]*[a-z0-9])?$", domain):
        return False
    if "." not in domain:
        return False
    return True

def normalize_domain(line: str) -> str | None:
    line = line.strip().lower()
    if not line or line.startswith(("#", "!", "[")):
        return None
    for prefix in (
        "||", "|https://", "|http://", "@@||", "@@",
        "0.0.0.0 ", "127.0.0.1 ", ":: ",
        "domain:", "domain-suffix,", "domain-keyword,",
        "host-suffix,", "host,",
    ):
        if line.startswith(prefix):
            line = line[len(prefix):]
    line = re.split(r"[/#\s\^\$\*\|]", line)[0]
    line = line.strip(".")
    if is_valid_domain(line):
        return line
    return None

def parse_gfwlist(content: str) -> set[str]:
    domains = set()
    try:
        decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
    except Exception:
        decoded = content
    for line in decoded.splitlines():
        domain = normalize_domain(line)
        if domain:
            domains.add(domain)
    return domains

def parse_domain_set(content: str) -> set[str]:
    domains = set()
    for line in content.splitlines():
        domain = normalize_domain(line)
        if domain:
            domains.add(domain)
    return domains

PARSERS = {
    "gfwlist": parse_gfwlist,
    "domain-set": parse_domain_set,
    "plain-domain": parse_domain_set,
}

def download_and_parse(source: dict) -> tuple[str, set[str], str | None]:
    name = source["name"]
    parser = PARSERS.get(source["type"])
    if not parser:
        return name, set(), f"未知解析类型: {source['type']}"
    try:
        content = fetch_url(source["url"])
        domains = parser(content)
        return name, domains, None
    except Exception as e:
        return name, set(), str(e)

def generate_list_file(domains: set[str], category: str, sources_used: list[str]) -> str:
    now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S CST")
    header = [
        f"# SurgeRuleSet - {category.upper()}",
        f"# Updated: {now}",
        f"# Sources: {', '.join(sources_used) if sources_used else 'none'}",
        f"# Total: {len(domains)}",
        f"# Repo: https://github.com/Zheng-JD/SurgeRuleSet",
        "#",
    ]
    body = [f"DOMAIN-SUFFIX,{d}" for d in sorted(domains)]
    return "\n".join(header + body) + "\n"

def generate_sgmodule(category: str, policy: str, list_url: str) -> str:
    name_map = {"Proxy": "SurgeRuleSet Proxy", "Direct": "SurgeRuleSet Direct", "Reject": "SurgeRuleSet Reject"}
    desc_map = {
        "Proxy": "需要代理的国外网站规则（已排除 Apple 域名）",
        "Direct": "国内可直连网站规则",
        "Reject": "广告与追踪拦截规则（保守策略，减少误杀）",
    }
    return f"""#!name={name_map.get(category, category)}
#!desc={desc_map.get(category, category)}
#!category=SurgeRuleSet

[Rule]
RULE-SET,{list_url},{policy}
"""

def main():
    os.makedirs(RULES_DIR, exist_ok=True)
    os.makedirs(MODULES_DIR, exist_ok=True)

    report = {"success": [], "failed": [], "counts": {}, "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat()}
    final_domains = {"Proxy": set(), "Direct": set(), "Reject": set()}
    sources_used = {"Proxy": [], "Direct": [], "Reject": []}

    all_tasks = [(cat.capitalize(), src) for cat, srcs in SOURCES.items() for src in srcs]

    print("开始拉取规则源...")
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(download_and_parse, src): (cat, src) for cat, src in all_tasks}
        for future in as_completed(futures):
            cat, src = futures[future]
            name, domains, error = future.result()
            if error:
                print(f"[失败] {name}: {error}")
                report["failed"].append({"name": name, "category": cat, "error": str(error)})
            else:
                print(f"[成功] {name}: {len(domains)} 条")
                report["success"].append({"name": name, "category": cat, "count": len(domains)})
                final_domains[cat].update(domains)
                sources_used[cat].append(name)

    # 1. 从 Proxy 强制移除所有 Apple 相关域名
    if final_domains["Proxy"]:
        before = len(final_domains["Proxy"])
        final_domains["Proxy"] = {d for d in final_domains["Proxy"] if not is_apple_domain(d)}
        removed = before - len(final_domains["Proxy"])
        if removed > 0:
            print(f"[清洗] Proxy 移除 Apple 相关域名: {removed} 条")

    # 2. Reject 白名单过滤
    if final_domains["Reject"]:
        before = len(final_domains["Reject"])
        final_domains["Reject"] = {
            d for d in final_domains["Reject"]
            if not any(d == w or d.endswith("." + w) for w in REJECT_WHITELIST)
        }
        removed = before - len(final_domains["Reject"])
        if removed > 0:
            print(f"[清洗] Reject 白名单移除: {removed} 条")

    # 3. 从 Proxy 移除已在 Direct 的域名
    overlap = final_domains["Proxy"] & final_domains["Direct"]
    if overlap:
        print(f"[清洗] Proxy 与 Direct 重叠移除: {len(overlap)} 条")
        final_domains["Proxy"] -= overlap

    base_raw = "https://raw.githubusercontent.com/Zheng-JD/SurgeRuleSet/main/rules"
    for cat in ["Proxy", "Direct", "Reject"]:
        domains = final_domains[cat]
        report["counts"][cat] = len(domains)
        list_content = generate_list_file(domains, cat, sources_used[cat])
        with open(os.path.join(RULES_DIR, f"{cat}.list"), "w", encoding="utf-8") as f:
            f.write(list_content)
        print(f"[生成] rules/{cat}.list ({len(domains)} 条)")

        policy = {"Proxy": "PROXY", "Direct": "DIRECT", "Reject": "REJECT"}[cat]
        module_content = generate_sgmodule(cat, policy, f"{base_raw}/{cat}.list")
        with open(os.path.join(MODULES_DIR, f"{cat}.sgmodule"), "w", encoding="utf-8") as f:
            f.write(module_content)
        print(f"[生成] modules/{cat}.sgmodule")

    with open(os.path.join(ROOT_DIR, "update_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n===== 生成完成 =====")
    for cat, count in report["counts"].items():
        print(f"  {cat}: {count} 条")
    print(f"成功源: {len(report['success'])}  失败源: {len(report['failed'])}")
    return 1 if report["failed"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
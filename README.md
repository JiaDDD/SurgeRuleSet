# SurgeRuleSet

- 自动拉取上游规则，经过去重、清洗、组合合并成聚合规则。
- 每日更新 **Surge 规则集**，提供干净的 **Proxy / Direct / Reject** 三类规则，方便直接订阅使用。


#### 为什么做这个项目？
依托 Surge 强大的性能，我不想再订阅一堆零散规则。直接一步到位：**✈️被墙的走代理，✅国内的走直连，🚫广告直接拦截**
> 规则上游经过严格筛选，Reject 采用保守策略，尽量减少误杀。

## 规则说明

| 规则 | 用途 | 建议策略 |
|------|------|----------|
| **代理** | 国外被墙/需要代理的网站 | `PROXY` |
| **直连** | 国内可直连网站/直连即可 | `DIRECT` |
| **拒绝** | 广告与追踪拦截（保守） | `REJECT` |

**注意：Apple / iCloud** 相关域名不强制放入 Direct，由你自行决定策略。

---

## 订阅链接

PROXY
```ini
https://raw.githubusercontent.com/JiaDDD/SurgeRuleSet/main/rules/Proxy.list
```

DIRECT
```ini
https://raw.githubusercontent.com/JiaDDD/SurgeRuleSet/main/rules/Direct.list
```

REJECT
```ini
https://raw.githubusercontent.com/JiaDDD/SurgeRuleSet/main/rules/Reject.list
```
## 配置示例

### 黑名单模式（推荐大多数用户）

```ini
[Rule]
# 广告拦截
https://cdn.jsdelivr.net/gh/JiaDDD/SurgeRuleSet@main/rules/Reject.list,REJECT

# 国内直连
https://cdn.jsdelivr.net/gh/JiaDDD/SurgeRuleSet@main/rules/Direct.list,DIRECT

# 需要代理的网站
https://cdn.jsdelivr.net/gh/JiaDDD/SurgeRuleSet@main/rules/Proxy.list,PROXY

# 国内 IP 直连（可选，建议保留）
GEOIP,CN,DIRECT

# 最终规则
FINAL,PROXY
```

### 白名单模式

去除代理网站规则，未命中的流量全部走代理，适合服务器线路稳定、流量充足的用户：

```ini
[Rule]
RULE-SET,https://cdn.jsdelivr.net/gh/JiaDDD/SurgeRuleSet@main/rules/Reject.list,REJECT
RULE-SET,https://cdn.jsdelivr.net/gh/JiaDDD/SurgeRuleSet@main/rules/Direct.list,DIRECT
GEOIP,CN,DIRECT
FINAL,PROXY
```

---

## 数据来源

当前采用的源（保守选择，优先低误杀）：

**Proxy**
- [gfwlist](https://github.com/gfwlist/gfwlist)
- [Loyalsoldier/surge-rules](https://github.com/Loyalsoldier/surge-rules)

**Direct**
- [Loyalsoldier/surge-rules](https://github.com/Loyalsoldier/surge-rules)

**拦截**
- [Loyalsoldier/surge-rules](https://github.com/Loyalsoldier/surge-rules)
- [Peter Lowe's Ad and tracking server list](https://pgl.yoyo.org/adservers/)

> 后续会根据实际使用反馈，在保证低误杀的前提下选择性增加其他源。

---

## 更新机制

- 每天通过 GitHub Actions 自动更新拉取上游规则，保持规则最新。

---


## 鸣谢（排名不分先后）

- [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)
- [Loyalsoldier/surge-rules](https://github.com/Loyalsoldier/surge-rules)
- [gfwlist/gfwlist](https://github.com/gfwlist/gfwlist)
- [Peter Lowe](https://pgl.yoyo.org/)

## License

MIT

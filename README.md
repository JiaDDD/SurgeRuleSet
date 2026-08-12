# SurgeRuleSet

自动拉取上游规则，经过去重、清洗、组合合并成聚合规则。
每日更新 **Surge 规则集**，提供干净的 **Proxy / Direct / Reject** 三类规则，方便直接订阅使用。

为什么要做这个项目：依托Surge强大的性能，不想订阅很多条不同规则，直接一步到位，被墙的网站走代理，国内的网站走直连，去广告的规则直接拦截，大道至简！

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

### 方式一：RULE-SET（推荐）

**GitHub Raw：**

```ini
RULE-SET,https://raw.githubusercontent.com/Zheng-JD/SurgeRuleSet/main/rules/Proxy.list,PROXY
RULE-SET,https://raw.githubusercontent.com/Zheng-JD/SurgeRuleSet/main/rules/Direct.list,DIRECT
RULE-SET,https://raw.githubusercontent.com/Zheng-JD/SurgeRuleSet/main/rules/Reject.list,REJECT
```

**jsDelivr 加速：**

```ini
RULE-SET,https://cdn.jsdelivr.net/gh/Zheng-JD/SurgeRuleSet@main/rules/Proxy.list,PROXY
RULE-SET,https://cdn.jsdelivr.net/gh/Zheng-JD/SurgeRuleSet@main/rules/Direct.list,DIRECT
RULE-SET,https://cdn.jsdelivr.net/gh/Zheng-JD/SurgeRuleSet@main/rules/Reject.list,REJECT
```

### 方式二：模块一键安装

在 Surge → 模块 → 安装模块，填入以下地址：

| 模块 | 链接 |
|------|------|
| Proxy | `https://raw.githubusercontent.com/Zheng-JD/SurgeRuleSet/main/modules/Proxy.sgmodule` |
| Direct | `https://raw.githubusercontent.com/Zheng-JD/SurgeRuleSet/main/modules/Direct.sgmodule` |
| Reject | `https://raw.githubusercontent.com/Zheng-JD/SurgeRuleSet/main/modules/Reject.sgmodule` |

jsDelivr 版本把域名换成 `cdn.jsdelivr.net/gh/Zheng-JD/SurgeRuleSet@main/modules/...` 即可。

---

## 配置示例

### 黑名单模式（推荐大多数用户）

```ini
[Rule]
# 广告拦截
RULE-SET,https://cdn.jsdelivr.net/gh/Zheng-JD/SurgeRuleSet@main/rules/Reject.list,REJECT

# 国内直连
RULE-SET,https://cdn.jsdelivr.net/gh/Zheng-JD/SurgeRuleSet@main/rules/Direct.list,DIRECT

# 需要代理的网站
RULE-SET,https://cdn.jsdelivr.net/gh/Zheng-JD/SurgeRuleSet@main/rules/Proxy.list,PROXY

# 国内 IP 直连（可选，建议保留）
GEOIP,CN,DIRECT

# 最终规则
FINAL,PROXY
```

### 白名单模式

适合服务器线路稳定、流量充足的用户：

```ini
[Rule]
RULE-SET,https://cdn.jsdelivr.net/gh/Zheng-JD/SurgeRuleSet@main/rules/Reject.list,REJECT
RULE-SET,https://cdn.jsdelivr.net/gh/Zheng-JD/SurgeRuleSet@main/rules/Direct.list,DIRECT
GEOIP,CN,DIRECT
FINAL,PROXY
```

> 白名单模式下可不加载 Proxy 规则，未命中的流量全部走代理。

### 策略组建议

```ini
[Proxy Group]
# 主策略
PROXY = select, 节点1, 节点2, 自动选择, DIRECT

# 自动选择
自动选择 = url-test, 节点1, 节点2, url=http://www.gstatic.com/generate_204, interval=600

# 广告（可选独立策略）
广告拦截 = select, REJECT, REJECT-TINYGIF
```

---

## 数据来源

当前采用的源（保守选择，优先低误杀）：

**Proxy**
- [gfwlist](https://github.com/gfwlist/gfwlist)
- [Loyalsoldier/surge-rules](https://github.com/Loyalsoldier/surge-rules) (`gfw.txt` + `proxy.txt`)

**Direct**
- [Loyalsoldier/surge-rules](https://github.com/Loyalsoldier/surge-rules) (`direct.txt`)

**拦截**
- [Loyalsoldier/surge-rules](https://github.com/Loyalsoldier/surge-rules) (`reject.txt`)
- [Peter Lowe's Ad and tracking server list](https://pgl.yoyo.org/adservers/)

> 后续会根据实际使用反馈，在保证低误杀的前提下选择性增加其他源。

---

## 更新机制

- 每天通过 GitHub Actions 自动更新，保持规则最新。

---

## 本地运行

```bash
python scripts/generate.py
```

---

## 注意事项

1. 规则按从上到下匹配，请注意顺序。
2. Reject 采用保守策略，已过滤部分容易误杀的域名。
3. Apple / iCloud 未强制归入 Direct，请根据自己网络情况决定。
4. 建议配合 `GEOIP,CN,DIRECT` 使用效果更好。

---

## 鸣谢

- [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)
- [Loyalsoldier/surge-rules](https://github.com/Loyalsoldier/surge-rules)
- [gfwlist/gfwlist](https://github.com/gfwlist/gfwlist)
- [Peter Lowe](https://pgl.yoyo.org/)

## License

MIT

# Acceptance Report Template

```markdown
# E2E 验收报告 — [产品名称]
**日期：** YYYY-MM-DD
**版本：** vX.X
**测试人：** pm-Octopus
**环境：** 本地 / 测试环境
**设计稿基准：** design/design-preview.html

---

## 测试场景汇总

| # | 场景 | 类型 | 状态 | Issue |
|---|------|------|------|-------|
| 1 | 场景名称 | 功能/UI/体验 | ✅ Pass | — |
| 2 | 场景名称 | 功能/UI/体验 | 🔴 Fail | [#7](link) |
| 3 | 场景名称 | 功能/UI/体验 | 🟡 Warning | [#8](link) |

---

## 场景详情

### 功能流程

#### 1. [测试项名称]
**场景**：[测试的具体场景描述]
**请求**：
```bash
curl -X POST http://localhost:8000/api/xxx \
  -H "Content-Type: application/json" \
  -d '{"field": "value"}'
```
**返回**：
```json
{"status": "ok", "data": {...}}
```
**结论**：✅ Pass — 返回 200，数据结构符合预期

---

### UI 对照设计稿

#### 2. [页面名称] UI 还原
**场景**：[页面描述]
**操作**：进入该页面
**截图**：![页面截图](screenshots/02-page.png)
**设计稿对比**：背景色 #0F0F1A ✅ / 金色 #C9A84C ✅ / 进度条 🔴 缺失
**结论**：🔴 Fail — 进度条未实现
**Issue**：[#8 小程序 UI 未还原设计稿](https://github.com/GhostComplex/fuyan/issues/8)

---

## Bug 汇总

| 优先级 | 描述 | Issue | 截图 |
|--------|------|-------|------|
| 🔴 P0 | bug 描述 | [#7](link) | screenshots/xx.png |
| 🟡 P1 | bug 描述 | [#8](link) | screenshots/xx.png |

---

## 结论

**整体状态：** ✅ 通过 / 🔴 未通过 / 🟡 部分通过

**说明：** [一句话总结]

**待跟进：**
- [ ] [#7](link) P0 bug 修复后重新验收
- [ ] [#8](link) P1 UI 还原后重新验收
```

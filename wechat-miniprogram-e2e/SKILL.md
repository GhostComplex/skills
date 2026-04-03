---
name: wechat-miniprogram-e2e
description: E2E functional acceptance testing for WeChat Mini Programs using miniprogram-automator. Use when performing automated UI testing, taking screenshots, simulating user interactions, or validating mini program flows against a running backend. Covers environment setup, automator connection, page interaction, screenshot capture, acceptance reporting, and bug issue creation.
---

# WeChat Mini Program E2E 验收流程

## 概述

本 skill 覆盖微信小程序端到端功能验收的完整流程：环境启动 → 自动化测试 → 截图 → 如实记录 → bug 提 Issue → 验收报告存档推送。

**验收代表用户视角，不只是"功能跑通"。范围 = 功能流程 + UI 对照设计稿 + 用户体验。**

---

## 验收核心原则（2026-04-03 确立）

> **脚本 ≠ 验收。脚本只是效率工具，判断 UI 对不对是人的事。**

### 验收方式优先级

| 方式 | 定位 | 说明 |
|------|------|------|
| **手动走完整用户旅程** | ✅ 主验收（必须） | 每次验收必须在模拟器上手动走：首页→填写→模板→预览→生成→分享 |
| **automator 脚本截图** | 🔧 辅助工具（可选） | 帮助到达页面、批量截图，提升效率，但不能替代手动操作 |

**脚本跑通 ≠ 验收通过。** 脚本参数错了照样跑完不报错，但截图对象根本不对。

### 验收范围（每次都必须）

- **PR 改动的页面**：重点比对设计稿，逐项截图
- **完整主流程回归**：无论 PR 改哪里，必须跑一遍完整路径（首页→填写→模板→预览→生成→分享），确认没有回归问题

### 截图验收 checklist（出结论前必须过）

- [ ] 每个关键步骤都有截图（不只截首屏，要滚动到底部）
- [ ] 截图与设计稿逐项对照，差异已记录
- [ ] 每条验收项能对应到具体截图（填不完表 = BLOCKED，不能出 PASS）
- [ ] 截图已 push 到 repo，URL 可访问（`curl -sI <url> | grep HTTP`）
- [ ] 验收结论发到 Issue 评论（不是群里说一句）

### 脚本使用规范

- **执行前必须先 review**：脚本写好 → 提 PR → SuperBoss review 参数有效性 → 才能执行
- **执行前先手动验参数有效性**：确认 `template_id`、`scene` 等参数在代码里真实存在
- **验收结论不能基于脚本是否跑通**，只能基于手动操作 + 截图对照设计稿

### 验收结论标准

- **PASS** = 手动走完整流程 + 每条验收项有截图 + 截图与设计稿对照无差异（或差异已确认为 P2/P3）
- **FAIL** = 有未解决的 P0/P1 bug
- **BLOCKED** = 某条验收项没有完整截图，无法出结论

### 管理者复核（SuperBoss）

PR merge 前，SuperBoss 必须在 PR 评论里写明：
> 「已复核截图：[截图1] [截图2]，与设计稿对比无问题 ✅」

不能只凭 QA 口头说通过就放行。

---

## 验收操作方式

### 模式一：完整任务验收（有测试脚本）

接到新功能验收任务时，写一个 Node.js 脚本放在 repo 的 `qa/` 目录，覆盖所有 case：

```
qa/
└── acceptance-{feature}-{date}.js   # 完整验收脚本（可复用，进 repo）
```

**脚本写好后先提 PR 给 SuperBoss review，review 通过后才开始执行。**

脚本负责：连接 automator → 逐步操作 → 每个关键状态截图 → 输出控制台日志。跑完对照设计稿出报告。

```bash
# 跑验收脚本（在 miniprogram/ 目录下跑，require 路径正确）
cd ~/workspace/fuyan/miniprogram
node ../qa/acceptance-copywriting-2026-04-03.js
```

### 模式二：单点验证（修复 PR 验收）

针对单个 bug 修复或单个功能点，写临时脚本验证：
- **一次性脚本**：用完即删，不进 repo
- **可复用的验证脚本**：移到 `qa/` 目录，提 PR 进 repo 版本控制
- **执行前同样需要 SuperBoss review**（可贴在群里或 PR 评论里确认）

**两种模式都自己写、自己跑，不需要 Juanjuan 操作 DevTools。**
**临时脚本不要留在 `miniprogram/` 目录里，用完删或移到 `qa/`。**

---

## 前置条件

- WeChat DevTools 已安装（`/Applications/wechatwebdevtools.app`）
- `miniprogram-automator` 已安装在项目 `node_modules/`
- 后端服务已启动（Docker Compose 或本地 uvicorn）
- DevTools 服务端口已开启（设置 → 安全设置 → 服务端口：开启）
- Node 具有录屏权限（系统设置 → 隐私 → 屏幕录制 → node ✅）

---

## Step 0: 验收前准备（必须）

1. **`git pull` 确认代码最新**：遇到任何问题先拉最新代码，不要在旧代码上调试

2. **确认后端环境真实性**（必须逐项确认，不能跳过）：
   ```bash
   # 确认后端进程路径（必须是项目正确路径，不是 /tmp）
   ps aux | grep uvicorn | grep -v grep
   git log -1 --oneline
   
   # 确认 API 真实性
   # 1. 餐厅搜索（验证高德 API key 有效）
   curl -X POST http://localhost:8000/api/v1/restaurants/search \
     -d '{"keyword":"外婆家","city":"上海"}' | python3 -c "..."
   # → 必须返回真实餐厅列表，不是 502/error
   
   # 2. 文案生成（验证 Qwen API key 有效）
   time curl -X POST http://localhost:8000/api/v1/copywriting/generate \
     -d '{"scene":"business",...}' | python3 -c "print(is_fallback, text)"
   # → is_fallback 必须是 False，贴耗时
   ```

3. **不许用 mock/setData 替代真实调用**：
   - ❌ 不能用 `setData` 注入餐厅数据绕过真实搜索
   - ❌ 不能在 API key 无效时继续验收
   - ✅ 必须让小程序真实发起请求，确认每个接口都通

4. **每一步都要有证据**：API 原始返回、耗时、截图

5. **出验收 checklist**，包含：
   - 功能流程 case（每个 P0/P1 功能逐一列出）
   - UI 对照 case（每页与设计稿逐页对比）
   - 用户体验 case（加载状态、错误提示、边界场景）
   - **H5 展示页**（用户收到分享链接后看到的最终效果）

6. 确认设计稿基准文件路径（如 `design/design-preview.html`）
7. automator 路径确认：`ls <project>/miniprogram/node_modules/miniprogram-automator`

---

## Step 1: 启动环境

```bash
# Option A: Docker Compose
cd <project-root>
docker compose up -d

# Option B: 本地启动
cd <project-root>/backend
source .venv311/bin/activate
uvicorn app.main:app --port 8000
```

启动后验证后端健康：
```bash
curl http://localhost:8000/health
```

---

## Step 2: 在 DevTools 中打开小程序

1. 打开 WeChat DevTools
2. 加载小程序项目目录
3. 确认服务端口已开启（设置 → 安全设置 → 服务端口）
4. **注意：服务端口号不固定，默认是 9422 但可能不同**（本机当前为 15288）

---

## Step 3: 通过 miniprogram-automator 连接

### ✅ 推荐方式：automator.launch（无需手动确认端口）

```js
const automator = require('miniprogram-automator')

// 不指定 port 让 automator 自动分配，避免冲突
const mp = await automator.launch({
  cliPath: '/Applications/wechatwebdevtools.app/Contents/MacOS/cli',
  projectPath: '/path/to/miniprogram',
  // port: 9422  // 可选，不指定则自动分配；指定时若被占用会报错
})
const page = await mp.currentPage()
```

### ⚠️ connect 方式（需要知道正确的 ws 端口）

> **重要**：DevTools 的 HTTP 服务端口（如 15288）≠ automator ws 端口。
> `ws://127.0.0.1:15288` 无法用于 automator 直连，会失败。
> 如需用 connect（DevTools 已在运行），先通过 CLI 查实际 ws 地址：
> ```bash
> /Applications/wechatwebdevtools.app/Contents/MacOS/cli auto --project /path/to/miniprogram --port 15288
> # 输出中会显示实际 ws 端口
> ```

```js
// 只有在知道正确 ws 端口时才用 connect
const mp = await automator.connect({
  wsEndpoint: 'ws://127.0.0.1:<正确的ws端口>'
})
const page = await mp.currentPage()
```

### 连接失败排查（自己排查，不打扰 Juanjuan）

1. 先确认 DevTools 服务端口是否开启（设置 → 安全设置）
2. **优先改用 `launch` 方式**，它自己管理进程和端口，最可靠
3. **不要问 Juanjuan 开端口，端口一直是开着的，问题在端口号配置**

完整 API 参考见 `references/automator-api.md`。

---

## Step 4: 页面交互

### 文本输入（中文安全）
不要用键盘模拟输入中文，改用 `callMethod`：
```js
await page.callMethod('setInputValue', { value: '用户输入的中文内容' })
await page.callMethod('onSend')
```

### ⚠️ callMethod vs tap 按钮
- **优先用 tap 按钮触发**：`await btn.tap()` 更可靠，能真实触发 bindtap 事件链
- **callMethod 只用于**：setData、同步方法、没有对应按钮的场景
- **async 方法不要用 callMethod**：async Page 方法用 callMethod 可能不生效，改用 tap 对应按钮

```js
// ✅ 推荐
const btn = await page.$('.btn-primary')
await btn.tap()

// ⚠️ 慎用（async 方法可能不生效）
await page.callMethod('onSubmit')
```

### 页面跳转后重新获取 page
页面跳转后，旧的 `page` 引用会 destroyed，**必须重新调用 `mp.currentPage()`**：
```js
await btn.tap()  // 触发跳转
await page.waitFor(2000)
// ❌ 不要继续用旧的 page
// ✅ 重新获取
page = await mp.currentPage()
console.log('New page:', page.path)
```

### 等待异步响应
```js
await page.waitFor(35000)  // 根据后端响应时间调整
```

### 页面导航
```js
// 直接导航（注意：目标页可能在 onLoad 里检查 globalData，为空会 redirect 走）
await mp.navigateTo('/pages/share/share')

// 返回上一页
await mp.navigateBack()
```

---

## Step 5: 截图

### 首选：automator 截图（无需解锁屏幕）
```js
await mp.screenshot({ path: '/absolute/path/to/screenshot.png' })
```

### 备选：系统 screencapture
```bash
# 单显示器
/usr/sbin/screencapture /path/to/screenshot.png

# 多显示器：指定主屏
/usr/sbin/screencapture -D 1 /path/to/screenshot.png
```

> **多显示器注意**：DevTools 可能开在副屏，优先用 automator 截图避免问题。

---

## Step 6: 如实记录每一步

- **边跑边记录**，不事后补
- 每个关键步骤立即截图，命名清晰（如 `01-home-screen.png`、`02-search-result.png`）
- 后端接口调用：附完整原始返回，不做摘要、不改写
- 发现异常：立即记录现象 + 报错信息，**不 debug，不绕过**

---

## Step 7: 发现问题 → 分析 → 定性（先分析，后动手）

发现问题时，**不要直接动手修**，先走以下流程：

### 7-1. 分析根因
判断问题来源：
- **实现没有对齐设计稿**（设计稿有，但代码没做对）
- **设计稿本身没有**（设计稿也没有这个效果，需要新增）

**验证方式**：截设计稿截图 vs 实际截图对比，用事实说话，不凭感觉。

### 7-2. 定性
| 类型 | 判断标准 | 处理路径 |
|------|---------|---------|
| **Bug（还原问题）** | 设计稿有，实现没做对 | 直接开 Issue → SuperCrew 修 → PR，不需要需求文档 |
| **需求变更** | 设计稿没有，要新增/改设计 | 先出需求文档 → 更新设计稿 → 开 Issue → 修 → PR |

### 7-3. 报结论，等决策
- 向 Juanjuan 报告定性结果（Bug 还是需求变更）
- **等 Juanjuan 确认后再动手**，不要自己拍板

### 7-4. 执行（确认后）

发现 Bug 时：

1. **如实记录**现象（截图 + 报错信息）
2. **只描述现象和影响范围**，不推荐修法（技术方案是开发的判断）
3. **截图放进 Issue 的正确方式**：

   **方式一（推荐）：push 到 repo 再用 raw 链接引用**
   ```bash
   # 1. 把截图复制到 repo
   cp /tmp/screenshot.png ~/workspace/fuyan/design/screenshots/bug-xxx-repro.png
   cd ~/workspace/fuyan
   git add design/screenshots/bug-xxx-repro.png
   git commit -m "qa: add BUG-XXX reproduction screenshot"
   git push origin main

   # 2. 用 ?raw=true 链接（比 raw.githubusercontent 更稳定）
   # https://github.com/GhostComplex/fuyan/blob/main/design/screenshots/bug-xxx-repro.png?raw=true
   ```

   **Issue body 里引用截图**：
   ```markdown
   ![bug描述](https://github.com/GhostComplex/fuyan/blob/main/design/screenshots/bug-xxx-repro.png?raw=true)
   ```

   **⚠️ 注意**：
   - `raw.githubusercontent.com` 链接可能有缓存延迟（404），用 `github.com/blob/...?raw=true` 更可靠
   - push 后确认截图在 GitHub 上可以显示，再把 Issue 报告给 SuperBoss
   - **复现截图和验收截图都必须贴进 Issue 评论**，不能只写 repo 路径
   - Issue 里截图能看到，才算 bug 复现/验收完整

4. **在 GitHub repo 创建 Issue**：

```bash
gh issue create --repo <owner/repo> \
  --title "P1 Bug: [一句话描述]" \
  --body "## 现象\n\n[具体现象]\n\n## 复现步骤\n\n1. 步骤一\n2. 步骤二\n\n## 预期结果\n\n[预期行为]\n\n## 实际结果\n\n[实际看到的，附截图]\n\n## 截图\n\n![repro](https://github.com/GhostComplex/fuyan/blob/main/design/screenshots/bug-xxx-repro.png?raw=true)\n\n## 影响\n\n[影响范围]" \
  --label "bug"
```

5. **截图可见后再报告给 SuperBoss**，等 SuperBoss 确认后才分配给开发

---

## Step 8: 写验收报告

### 后端 API 项格式
```
#### [编号]. [测试项名称]
**场景**：[测试的具体场景描述]
**请求**：
（完整 curl 命令）
**返回**：
（原始返回内容，不做摘要，不改写）
**结论**：✅ Pass / 🔴 Fail / 🟡 Warning — [一句话说明原因]
```

### 前端 UI 项格式
```
#### [编号]. [测试项名称]
**场景**：[测试的具体场景描述]
**操作**：[执行的交互步骤]
**截图**：![截图描述](screenshots/文件名.png)
**设计稿对比**：[与 design-preview.html 的差异描述，或"一致"]]
**结论**：✅ Pass / 🔴 Fail / 🟡 Warning — [一句话说明原因]
**Issue**：[#编号 链接]（如有 bug）
```

标准模板见 `references/report-template.md`。

---

## Step 9: 验收报告存档与推送

1. 保存到 `tasks/<task-name>/acceptance-report.md`，截图到 `tasks/<task-name>/screenshots/`
2. 推送到 repo：`design/acceptance-report-YYYY-MM-DD.md`，截图同步推
3. **不能只发在群消息里**

```bash
cd <project-root>
git add design/acceptance-report-*.md design/screenshots/
git commit -m "docs: add acceptance report YYYY-MM-DD"
git push
```

---

## 验收诚实原则（红线）

- **跑不通就报跑不通**，不能因为"大部分通了"就写全通
- **没有截图、没有原始数据，就是没跑**，不算验收
- **卡在哪就报哪**，虚报会让团队基于错误信息做决策
- 口头说"验收过了"不算验收；"基本通过"不等于通过

---

## 常见 UI 验收操作速查

### 滑动 / 滚动

```javascript
// 滚动到页面底部
await page.evaluate(() => wx.pageScrollTo({ scrollTop: 9999, duration: 0 }))

// 滚动到指定位置（像素）
await page.evaluate(() => wx.pageScrollTo({ scrollTop: 500, duration: 300 }))

// 滑动组件内部 scroll-view
const scrollView = await page.$('.scroll-view-container')
await scrollView.swipe({ startX: 300, startY: 500, endX: 300, endY: 100, steps: 10 })
```

### 点击

```javascript
// 点击按钮
const btn = await page.$('.btn-class')
await btn.tap()

// 点击列表第 N 项（0-indexed）
const items = await page.$$('.list-item')
await items[0].tap()
```

### 等待元素出现（避免时序问题）

```javascript
await page.waitFor('.target-element')  // 等元素出现
await page.waitFor(1000)               // 固定等待（不推荐，必要时用）
```

### 页面跳转后获取新页面

```javascript
// 方式一：重新获取 currentPage
await btn.tap()
await page.waitFor(1500)
page = await mp.currentPage()
console.log('New page:', page.path)

// 方式二：从页面栈取最新页
await btn.tap()
await page.waitFor(500)
const pages = await mp.pageStack()
const newPage = pages[pages.length - 1]
```

### 文本输入

```javascript
// 直接 input（input 组件）
const input = await page.$('.input-class')
await input.input('新内容')

// 中文 / 特殊内容用 setData 注入（绕过 IME 问题）
await page.callMethod('setData', { keyword: '外婆家' })
```

### picker 选择器操作

```javascript
// 触发 picker
const picker = await page.$('.picker-class')
await picker.tap()
// picker 值通过 setData 注入
await page.callMethod('setData', { dateValue: '2026-04-03' })
```

### 读取页面内容

```javascript
// 读取元素文本
const el = await page.$('.title')
const text = await el.text()
console.log(text)

// 读取元素属性
const attr = await el.attribute('class')

// 读取页面 data
const data = await page.data()
console.log(data.someField)
```

### 截图规范

```javascript
// 截图存到 repo 内 design/screenshots/，不存 /tmp
// 用变量，不要写死绝对路径
const SCREENSHOT_DIR = `${process.cwd()}/design/screenshots`

await mp.screenshot({ path: `${SCREENSHOT_DIR}/step-01-home.png` })

// 滚动后截图（捕获折叠在下方的内容）
await page.evaluate(() => wx.pageScrollTo({ scrollTop: 800, duration: 0 }))
await page.waitFor(500)
await mp.screenshot({ path: `${SCREENSHOT_DIR}/step-02-bottom.png` })
```

> ⚠️ **截图不存 `/tmp`**：存到 repo 内 `design/screenshots/`，push 后才能贴进 Issue 评论。不要写死绝对路径，换机器不用改。

### 模态框 / toast 捕获

```javascript
// toast 会自动消失，截图要快
const SCREENSHOT_DIR = `${process.cwd()}/design/screenshots`
await btn.tap()
await page.waitFor(300)
await mp.screenshot({ path: `${SCREENSHOT_DIR}/toast.png` })
```

### 网络请求拦截（mock 数据验证）

```javascript
await mp.mockWxMethod('request', (opts) => {
  return { data: { mock: true }, statusCode: 200 }
})
```

### debug / 读取报错

```javascript
// 监听 console 日志
mp.on('console', msg => console.log('[miniprogram]', msg.type, msg.text))

// 读取页面 data 排查状态
const data = await page.data()
console.log(JSON.stringify(data, null, 2))
```

```bash
# curl 直接验证后端接口（独立于小程序）
curl -X POST http://localhost:8000/api/v1/xxx \
  -H 'Content-Type: application/json' \
  -d '{"key": "value"}'
```

---

## 常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| `connection refused` 端口 | DevTools ws 端口号不对，或服务未开 | 改用 `launch` 方式；不要问 Juanjuan 开端口，端口一直开着，是端口号配置问题 |
| HTTP 端口（如 15288）连 ws 失败 | 15288 是 HTTP CLI 端口，不是 automator ws 端口 | 改用 `automator.launch`，自动分配 ws 端口 |
| 截图全黑 / 截到错误屏幕 | 多显示器，DevTools 在副屏 | 改用 automator `mp.screenshot()` |
| 中文输入失效 | 键盘模拟不支持 IME | 改用 `callMethod` 直接设值 |
| 找不到页面方法 | 方法名不匹配 | 查页面 `.js` 文件确认方法名 |
| automator 超时 | 后端响应慢 | 增大 `waitFor` 时长 |
| 422 / Pydantic 校验失败 | 入参不符合后端 schema | 如实记录，创建 Issue，报告开发 |

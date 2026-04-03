# miniprogram-automator API Reference

## Connection

```js
const automator = require('miniprogram-automator')
const mp = await automator.connect({ wsEndpoint: 'ws://127.0.0.1:<port>' })
```

## MiniProgram (`mp`)

| Method | Description |
|--------|-------------|
| `mp.currentPage()` | Get the current page object |
| `mp.navigateTo(url)` | Navigate to a page URL |
| `mp.navigateBack()` | Go back to previous page |
| `mp.switchTab(url)` | Switch to a tabBar page |
| `mp.screenshot({ path })` | Capture screenshot to file |
| `mp.close()` | Close the automator connection |

## Page (`page`)

| Method | Description |
|--------|-------------|
| `page.waitFor(ms)` | Wait for milliseconds |
| `page.waitFor(selector)` | Wait for element to appear |
| `page.$(selector)` | Select a single element |
| `page.$$(selector)` | Select multiple elements |
| `page.callMethod(name, args)` | Call a page lifecycle/custom method |
| `page.data(key)` | Read page data |
| `page.setData(data)` | Set page data directly |

## Element (`el`)

| Method | Description |
|--------|-------------|
| `el.tap()` | Simulate tap |
| `el.input(value)` | Input text (ASCII only — use `callMethod` for Chinese) |
| `el.attribute(name)` | Get element attribute |
| `el.text()` | Get element text content |
| `el.$(selector)` | Query child element |

## Selectors

Uses CSS-like selectors scoped to WXML:
```js
page.$('.class-name')
page.$('#element-id')
page.$('view.container > text')
```

## callMethod Pattern (Chinese Input)

When the page exposes a method to set input value, use:
```js
await page.callMethod('setInputValue', { value: '中文内容' })
await page.callMethod('onSend')
```

If no such method exists, inject via `setData`:
```js
await page.setData({ inputValue: '中文内容' })
await page.callMethod('onSend')
```

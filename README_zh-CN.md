![](https://img.shields.io/badge/SublimeText-4-black) ![](https://img.shields.io/badge/License-MIT-green)

[**English**](README.md) | [**中文**](README_zh-CN.md)

# Json5Formatter

使用系统 Python 的 `json5` 库格式化 JSON/JSON5 文件的 Sublime Text 插件。

## 功能

| 命令 | 说明 |
|------|------|
| **JSON5: Format as JSON** | 格式化并输出标准 JSON，**保留注释** |
| **JSON5: Format as JSON5** | 格式化为 JSON5 风格（不保留注释） |
| **JSON5: Minify** | 压缩为单行 JSON |

- 支持 JSON5 语法：`//` 和 `/* */` 注释、单引号字符串、尾逗号、无引号 key
- 自动转换单引号 → 双引号、无引号 key → 引号 key
- 输出标准 JSON（不含尾逗号）

## 安装

### 前提条件

- [Python](https://www.python.org/) 3.x（已在系统 PATH 中）
- `json5` 库：`pip install json5`

### 手动安装

Sublime Text 4

```
cd <Packages 目录>   (Preferences → Browse Packages...)
git clone git@github.com:RAMBOO1990/sublime-json5.git "Json5Formatter"
```

## 使用

### 命令面板

按 `Ctrl+Shift+P`，输入 `JSON5:`，选择需要的命令。

### 快捷键

| 快捷键 | 命令 |
|--------|------|
| `Ctrl+Shift+J` | Format as JSON |

可在 `Default.sublime-keymap` 中自定义。

## 设置

`Preferences → Package Settings → Json5Formatter → Settings`

```json
{
    // 缩进空格数
    "indent": 4,
    // 按字母顺序排序 object key
    "sort_keys": false,
    // 转义非 ASCII 字符
    "ensure_ascii": false
}
```

> `sort_keys` 和 `ensure_ascii` 仅在 Format as JSON5 和 Minify 命令中生效。Format as JSON 使用内建格式化器，暂不支持这两个选项。

## 许可

MIT

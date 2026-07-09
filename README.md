![](https://img.shields.io/badge/SublimeText-4-black) ![](https://img.shields.io/badge/License-MIT-green)

[**English**](README.md) | [**中文**](README_zh-CN.md)

# Json5Formatter

A Sublime Text plugin that formats JSON/JSON5 files using the system Python's `json5` library.

## Features

| Command | Description |
|---------|-------------|
| **JSON5: Format as JSON** | Format and output standard JSON, **preserving comments** |
| **JSON5: Format as JSON5** | Format as JSON5 style (comments not preserved) |
| **JSON5: Minify** | Compress to single-line JSON |

- Supports JSON5 syntax: `//` and `/* */` comments, single-quoted strings, trailing commas, unquoted keys
- Auto-converts single quotes → double quotes, unquoted keys → quoted keys
- Outputs standard JSON (no trailing commas)

## Installation

### Prerequisites

- [Python](https://www.python.org/) 3.x (on system PATH)
- `json5` library: `pip install json5`

### Manual Install

Sublime Text 4

```
cd <Packages directory>   (Preferences → Browse Packages...)
git clone git@github.com:RAMBOO1990/sublime-json5.git "Json5Formatter"
```

## Usage

### Command Palette

Press `Ctrl+Shift+P`, type `JSON5:`, and select the desired command.

### Key Binding

| Keys | Command |
|------|---------|
| `Ctrl+Shift+J` | Format as JSON |

Customize in `Default.sublime-keymap`.

## Settings

`Preferences → Package Settings → Json5Formatter → Settings`

```json
{
    // Number of spaces per indent level
    "indent": 4,
    // Sort object keys alphabetically
    "sort_keys": false,
    // Escape non-ASCII characters
    "ensure_ascii": false
}
```

> `sort_keys` and `ensure_ascii` only apply to the Format as JSON5 and Minify commands. Format as JSON uses the built-in formatter and does not currently support these options.

## License

MIT

# PlayerSizeChanger

一个用于MCDR（Minecraft Data Reforged）的插件，允许玩家更改自己的大小。

## 功能特点

- **更改玩家大小**：可以将玩家大小设置为方块大小（0.45）
- **恢复原始大小**：可以恢复玩家的原始大小
- **命令别名**：支持使用简短命令（如 `!!size bl` 和 `!!size res`）
- **多语言支持**：支持中文和英文
- **版本兼容**：支持不同Minecraft版本的属性ID格式
- **可点击命令**：菜单中的命令文本可点击，自动填充到聊天框

## 安装方法

1. 下载 `PlayerSizeChanger1.1.0.mcdr` 文件
2. 将文件放入MCDR的 `plugins` 目录
3. 重启MCDR服务器

## 使用命令

| 命令 | 描述 | 简写 |
|------|------|------|
| `!!size` | 显示帮助菜单 | - |
| `!!size block` | 设置为方块大小 | `!!size bl` |
| `!!size restore` | 恢复原始大小 | `!!size res` |

## 版本历史

- **1.1.0**：添加命令别名提示，优化菜单显示，修复bug
- **1.0.0**：初始版本，实现基本功能

## 兼容性

- Minecraft 1.20.5-1.21.1：使用 `minecraft:generic.scale` 属性
- Minecraft 1.21.2+：使用 `scale` 属性

## 作者

- ChiLunQAQ

## 许可证

MIT License

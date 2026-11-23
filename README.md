# Antigravity 简体中文（macOS，实验版）

基于 [antigravity-zh-plugin v1.6.0](https://github.com/yunjuanyunshu114-byte/antigravity-zh-plugin/releases/tag/v1.6.0) 的翻译词典和注入方案，为 macOS 上的 Google Antigravity 桌面版提供中文界面。本项目不是 Google 官方插件，也不是从应用插件市场安装的扩展。

**状态：实验版。** 已在一台 Apple Silicon Mac 的 Antigravity 2.34.0 上验证汉化版启动及主界面中文显示；独立发布版安装器在本机副本上验证了打包、签名及还原，尚未在其他机器、其他 macOS 版本或 Intel Mac 上验证。部分界面可能仍是英文。

## 安装前请阅读

- 本项目修改本机官方应用的 `app.asar` 和签名；不分发 Google 的应用程序或预构建资源。
- **汉化版将使用本地 ad-hoc 签名，并关闭应用及辅助进程的动态库来源校验**（`com.apple.security.cs.disable-library-validation`），安全性低于 Google 官方签名版本。不要在不接受此风险的环境使用。
- 重签名可能影响系统权限、钥匙串、登录和应用内更新。自动更新可能覆盖汉化；更新后的重新安装及兼容性尚未验证。
- 只支持 `/Applications/Antigravity.app` 中具有 Google 签名的 **2.34.0**；其他版本会停止。需要有修改该应用的权限、Python 3 和 Node.js，以及可用的 macOS `codesign`、`ditto` 工具。
- 安装前请保存所有工作。安装器会关闭 Antigravity、备份完整原版、构建中文资源、重签名并尝试启动；失败时尝试恢复。启动进程检查并不等于全面功能验收。

## 安装

从 GitHub 下载源码并解压，在项目目录运行：

```bash
python3 macos.py install
```

运行成功后，终端会打印完整的官方备份 `.app` 路径。请保留该路径及备份文件，以便恢复。备份保存在当前用户的 `~/Library/Application Support/Antigravity-ZH-macOS/` 中，可能占用较多磁盘空间。

## 恢复官方版本

保存工作后，用安装时打印的备份路径替换下面的示例：

```bash
python3 macos.py restore --backup "备份目录/Antigravity-original.app"
```

恢复程序校验备份的 Google 签名和版本；当前应用版本与备份不一致时会停止，避免覆盖更新后的版本。恢复过程会关闭应用并重启；若恢复失败，请保留备份并查看终端错误信息。

## 验证与开发

`build_offline.py` 仅对指定的官方 `app.asar` 副本生成中文归档，并不会安装。它要求旁边存在原始 `.asar.unpacked` 目录；输出目录必须不存在。

```bash
python3 build_offline.py /path/to/app.asar /path/to/new-output-directory
```

本项目不提供自动启动、后台守护、调试端口、预打包应用或自动更新机制。测试资料不得包含账号数据、应用二进制、用户对话、私有文件或 API 密钥。

## 致谢与许可

翻译引擎、词库、ASAR 处理和部分注入代码源自 [yunjuanyunshu114-byte/antigravity-zh-plugin](https://github.com/yunjuanyunshu114-byte/antigravity-zh-plugin)，原作者和 fork 作者的版权声明保留在 [LICENSE](LICENSE)。本项目按 MIT 许可发布。

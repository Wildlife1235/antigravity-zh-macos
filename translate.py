# Adapted from antigravity-zh-plugin v1.6.0, MIT License; see LICENSE.
import json
import os
import re
import asar
HERE = os.path.dirname(os.path.abspath(__file__))
def say(message):
    print(message)
def die(message, code=1):
    raise RuntimeError(message)

TAG = "Antigravity Chinese Translation Injection v5-appendonly"

DICT_PLACEHOLDER = "__DICT_ITEMS__"

ENGINE_START_MARKER = "(function() {\n  const dictionary = {"

UNPACK_PATTERNS = ["**/node_modules/chrome-devtools-mcp/**"]

BLOCK_BEGIN = "// ===== AG_ZH_BEGIN:%s ====="

BLOCK_END = "// ===== AG_ZH_END:%s ====="

BLOCK_BEGIN_PREFIX = "// ===== AG_ZH_BEGIN:"

BLOCK_PAIR_RE = re.compile(
    r"\n?// ===== AG_ZH_BEGIN:[^\n]+ =====[\s\S]*?// ===== AG_ZH_END:[^\n]+ =====\n?"
)

LEGACY_MARKERS = [
    "// ===== Antigravity Chinese Translation Injection v3-full =====",
    "// ===== Antigravity Chinese Translation Injection v2-extra =====",
    "// ===== Antigravity Chinese Translation Injection v4-appendonly =====",
    "const menuTranslationMap = {",
]

LEGACY_MENU_CALL = "if (typeof translateMenu === 'function') { menu.items.forEach(translateMenu); } "

def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_text(path, content):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def load_dictionary():
    d = {}
    dict_path = os.path.join(HERE, "dicts", "zh_cn.json")
    if not os.path.exists(dict_path):
        die("找不到字典文件: %s" % dict_path)
    with open(dict_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        d.update(data)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "key" in item and "value" in item:
                d[item["key"]] = item["value"]
    if not d:
        die("字典为空")
    return d

def load_engine_template():
    p = os.path.join(HERE, "dicts", "engine.js")
    if not os.path.exists(p):
        die("找不到引擎模板: %s" % p)
    return read_text(p)

def build_engine_block(dictionary):
    items = []
    for k, v in dictionary.items():
        items.append("    %s: %s" % (json.dumps(k, ensure_ascii=False),
                                     json.dumps(v, ensure_ascii=False)))
    dict_block = "// ===== %s =====\n  const extraDict = {\n%s\n  };\n" % (
        TAG, ",\n".join(items))
    engine = load_engine_template().replace(DICT_PLACEHOLDER, dict_block)
    return ("try {\n" + engine.rstrip() + "\n} catch (e) {\n"
            "  try { console.error('[Antigravity-ZH] 引擎初始化失败', e); } catch (_) {}\n"
            "}")

MENU_LABELS = {
    "File": "文件", "Edit": "编辑", "View": "视图", "Workspace": "工作区",
    "Window": "窗口", "Help": "帮助", "New": "新建", "New Window": "新建窗口", "New Conversation": "新建对话",
    "Docs": "使用文档", "Documentation": "使用文档", "Toggle Developer Tools": "开发者工具",
    "Check for Updates": "检查更新", "Checking for Updates...": "正在检查更新...",
    "Downloading Update...": "正在下载更新...", "Restart to Update": "重启以应用更新",
    "Undo": "撤销", "Redo": "重做", "Cut": "剪切", "Copy": "复制", "Paste": "粘贴",
    "Paste and Match Style": "粘贴并匹配样式", "Select All": "全选",
    "Minimize": "最小化", "Close": "关闭", "Quit": "退出",
    "Quit Antigravity": "退出 Antigravity", "About Antigravity": "关于 Antigravity",
    "Services": "服务", "Hide Antigravity": "隐藏 Antigravity", "Hide Others": "隐藏其他",
    "Show All": "显示全部", "Force Reload": "强制重新加载", "Reload": "重新加载",
    "Actual Size": "实际大小", "Zoom In": "放大", "Zoom Out": "缩小",
    "Toggle Full Screen": "切换全屏", "Settings": "设置", "Settings...": "设置...",
    "Preferences": "偏好设置", "Preferences...": "偏好设置...", "Exit": "退出",
    "No agents running": "没有智能体在运行", "Open Antigravity": "打开 Antigravity",
    "Learn More": "了解更多", "Show Logs": "显示日志", "Reload Window": "重新加载窗口",
    "New Agent": "新建智能体", "Open Settings": "打开设置", "Export": "导出",
    "Import": "导入", "Remove": "移除", "Delete": "删除", "Delete Permanently": "永久删除",
    "Rename": "重命名", "Duplicate": "创建副本",
    "Select Project": "选择项目", "Open Folder": "打开文件夹", "Open Terminal": "打开终端",
    "Connect to WSL": "连接到 WSL", "Reopen Locally": "在本地重新打开",
    "Connect to SSH Host": "连接到 SSH 主机", "Connect to SSH Host…": "连接到 SSH 主机…",
    "Switch to This Computer": "切换到此计算机", "SSH Config": "SSH 配置",
    "Start New Chat": "开始新对话",
    # 对话与窗格右键上下文菜单（2.34.0 showContextMenu）
    "Pin": "置顶", "Unpin": "取消置顶",
    "Pin This Conversation": "置顶此对话", "Unpin This Conversation": "取消置顶此对话",
    "Pin Entire Project": "置顶整个项目", "Unpin Project": "取消置顶项目",
    "Pin Entire Workspace": "置顶整个工作区", "Unpin Workspace": "取消置顶工作区",
    "Pin Entire Worktree": "置顶整个工作树", "Unpin Worktree": "取消置顶工作树",
    "Mark Read": "标为已读", "Mark Unread": "标为未读",
    "Mark as Read": "标为已读", "Mark as Unread": "标为未读",
    "View Debug": "查看调试信息",
    "Move to Group": "移动到分组", "New Group": "新建分组", "Remove from Group": "从分组中移除",
    "Conversation Name": "对话名称", "Conversation ID": "对话 ID",
    "Workspace Name": "工作区名称", "Worktree Name": "工作树名称", "Project Name": "项目名称",
    "Fork": "分叉", "Fork Conversation": "分叉对话",
    "Split": "分屏", "Split Right": "向右分屏", "Split Down": "向下分屏",
    "Split Left": "向左分屏", "Split Up": "向上分屏",
    "Replace with New": "替换为新建对话", "Remove from Split": "从分屏中移除",
    "Share": "共享", "Stop": "停止",
    "Archive": "归档", "Unarchive": "取消归档", "Restore": "恢复",
    "Telemetry": "遥测",
    # 标签页 / 浏览器 / 链接 / 视图右键菜单
    "Pin Tab": "固定标签页", "Unpin Tab": "取消固定标签页",
    "Keep Open": "保持打开", "Auto Pin": "自动置顶",
    "Close Tab": "关闭标签页", "Close Other Tabs": "关闭其他标签页",
    "Close All Tabs": "关闭全部标签页", "Close Tabs to the Right": "关闭右侧标签页",
    "Side Panel": "侧边栏", "Built-in Browser": "内置浏览器",
    "External Browser": "外部浏览器", "System Browser": "系统浏览器",
    "Open in Side Panel": "在侧边栏中打开", "Open in Browser": "在浏览器中打开",
    "Open in Built-in Browser": "在内置浏览器中打开", "Open in External Browser": "在外部浏览器中打开",
    "Open in System Browser": "在系统浏览器中打开", "Open in New Tab": "在新标签页中打开",
    "Open Link": "打开链接", "Copy Link": "复制链接", "Copy Link Address": "复制链接地址",
    "Copy Image": "复制图片", "Copy Image Address": "复制图片地址",
    "Copy Path": "复制路径", "Copy Relative Path": "复制相对路径",
    "Link Settings": "链接设置", "Download image": "下载图片", "Download video": "下载视频",
    "Save Image As...": "图片另存为...",
    "Reveal in File Explorer": "在文件资源管理器中显示", "Reveal in Finder": "在访达中显示",
    "Show in Folder": "在文件夹中显示", "Open in Terminal": "在终端中打开",
    "Toggle Word Wrap": "切换自动换行", "Inspect": "检查", "Inspect Element": "检查元素",
    "Refresh all credentials": "刷新全部凭据", "Refreshing credentials...": "正在刷新凭据...",
    "Show Automation Conversations": "显示自动化对话",
    "Show Plugin Conversations": "显示插件对话",
    "Idle Conversations": "空闲对话",
    "Side Question Selection": "选区侧边提问", "Reply": "回复",
    "Connection info…": "连接信息…", "Connection info": "连接信息",
    "View MCP servers": "查看 MCP 服务器",
    "Speech": "语音", "Start Speaking": "开始朗读", "Stop Speaking": "停止朗读",
    "Back": "后退", "Forward": "前进", "Refresh": "刷新",
}

MENU_ROLES = {
    "undo": "撤销", "redo": "重做", "cut": "剪切", "copy": "复制", "paste": "粘贴",
    "selectAll": "全选", "reload": "重新加载", "forceReload": "强制重新加载",
    "toggleDevTools": "开发者工具", "resetZoom": "实际大小", "zoomIn": "放大",
    "zoomOut": "缩小", "togglefullscreen": "切换全屏", "minimize": "最小化",
    "close": "关闭", "quit": "退出", "about": "关于", "services": "服务",
    "hide": "隐藏", "hideOthers": "隐藏其他", "unhide": "显示全部",
    "front": "前置全部窗口", "newWindow": "新建窗口", "window": "窗口",
    "help": "帮助", "file": "文件", "edit": "编辑", "view": "视图",
}

DIALOG_LABELS = {
    "Confirm Quit": "确认退出", "Are you sure you want to quit?": "您确定要退出吗？",
    "There may be agents or background tasks running.": "可能还有智能体或后台任务正在运行。",
    "Quit": "退出", "Cancel": "取消", "OK": "确定", "Save": "保存",
    "Don't Save": "不保存", "Yes": "是", "No": "否", "Continue": "继续",
    "Error": "错误", "Warning": "警告", "Antigravity": "Antigravity",
    "Connect a device": "连接设备",
    "Folder is on the Windows filesystem": "文件夹位于 Windows 文件系统中",
    "Cannot open folder": "无法打开文件夹",
    "Open workspace": "打开工作区",
    "Open workspaces": "打开工作区",
    "Select Download Folder": "选择下载文件夹",
    "WSL distro not found": "未找到 WSL 发行版",
    "Antigravity opened on Windows instead.": "已改为在 Windows 上打开 Antigravity。",
    "Couldn't connect to the SSH host. See the app log.": "无法连接到 SSH 主机，请查看应用日志。",
    "Choose an SSH config file": "选择 SSH 配置文件",
    "Choose another SSH config file": "选择其他 SSH 配置文件",
    "Choose Another File…": "选择其他文件…",
    "SSH connection failed": "SSH 连接失败",
    "Could not restart the SSH server": "无法重启 SSH 服务器",
    "Stop SSH server": "停止 SSH 服务器",
    "Stop Server": "停止服务器",
    "Agents running on this host will stop and its window will close.": "此主机上运行的智能体将停止，且其窗口将会关闭。",
    "Reconnect first, then stop its server.": "请先重新连接，然后再停止其服务器。",
    "Microphone access": "麦克风权限",
    "Allow": "允许",
    "Don't Allow": "不允许",
    "Sign in": "登录",
    "Sign In": "登录",
    "Shared home directory": "共享主目录",
    "Take Over": "接管",
    "Restart SSH server": "重启 SSH 服务器",
    "Restart": "重启",
    "Later": "稍后",
    "Check for Updates": "检查更新",
    "No updates available": "当前已是最新版本",
    "Choose a Passkey": "选择通行密钥 (Passkey)",
    "Select a passkey account to continue:": "选择一个通行密钥账号以继续：",
    "Connection info": "连接信息",
    "The connection was closed before it finished.": "连接在完成前已关闭。",
}

def _js_map(d):
    parts = []
    for k in d:
        parts.append("    %s: %s" % (json.dumps(k, ensure_ascii=False), json.dumps(d[k], ensure_ascii=False)))
    return "{\n" + ",\n".join(parts) + "\n  }"

MENU_PATCH_JS = """(function () {
  try {
    var electron = require('electron');
    var Menu = electron && electron.Menu;
    if (!Menu || Menu.__AG_ZH_MENU__) return;
    var LABELS = __MENU_LABELS__;
    var ROLES = __MENU_ROLES__;
    var EXT_DICT = Object.create(null);
    var EXT_DICT_LOWER = Object.create(null);
    var REVERSE_UPDATER = {
      '检查更新': 'Check for Updates',
      '正在检查更新...': 'Checking for Updates...',
      '正在下载更新...': 'Downloading Update...',
      '重启以应用更新': 'Restart to Update'
    };

    function loadExternalMenuDict() {
      try {
        var fs = require('fs');
        var os = require('os');
        var path = require('path');
        var extPath = path.join(os.homedir(), '.antigravity-zh', 'zh-CN.json');
        if (!fs.existsSync(extPath)) return;
        var raw = fs.readFileSync(extPath, 'utf-8');
        var parsed = JSON.parse(raw);
        var items = parsed.translations || parsed;
        var next = Object.create(null);
        var nextLow = Object.create(null);
        for (var k in items) {
          if (!Object.prototype.hasOwnProperty.call(items, k)) continue;
          if (k.indexOf('__') === 0 || typeof items[k] !== 'string') continue;
          next[k] = items[k];
          var lk = k.toLowerCase();
          if (!Object.prototype.hasOwnProperty.call(nextLow, lk)) nextLow[lk] = items[k];
        }
        EXT_DICT = next;
        EXT_DICT_LOWER = nextLow;
      } catch (e) {}
    }

    loadExternalMenuDict();
    try {
      var fsW = require('fs');
      var osW = require('os');
      var pathW = require('path');
      var extWatch = pathW.join(osW.homedir(), '.antigravity-zh', 'zh-CN.json');
      if (fsW.existsSync(extWatch)) {
        var timer = null;
        fsW.watch(extWatch, { persistent: false }, function () {
          if (timer) clearTimeout(timer);
          timer = setTimeout(loadExternalMenuDict, 200);
        });
      }
    } catch (e) {}

    function joinCn(prefix, rest) {
      if (!rest) return prefix;
      return /^[A-Za-z0-9]/.test(rest) ? prefix + ' ' + rest : prefix + rest;
    }

    function tr(s, depth) {
      if (typeof s !== 'string' || !s) return s;
      depth = depth || 0;
      if (depth > 3) return s;
      if (Object.prototype.hasOwnProperty.call(LABELS, s)) return LABELS[s];
      var m = /^(\\d+)\\s+(?:active\\s+)?agents?\\s+running$/i.exec(s);
      if (m) return m[1] + ' 个智能体运行中';
      m = /^(\\d+)\\s+active\\s+agents?$/i.exec(s);
      if (m) return m[1] + ' 个智能体运行中';
      m = /^(.+?)\\s+\\(Default\\)$/i.exec(s);
      if (m) return tr(m[1], depth + 1) + '（默认）';
      m = /^Open in (.+)$/i.exec(s);
      if (m) return '在 ' + tr(m[1], depth + 1) + ' 中打开';
      m = /^Pin Entire (.+)$/i.exec(s);
      if (m) return joinCn('置顶整个', tr(m[1], depth + 1));
      m = /^Unpin (.+)$/i.exec(s);
      if (m) return joinCn('取消置顶', tr(m[1], depth + 1));
      m = /^Copy (.+)$/i.exec(s);
      if (m) return joinCn('复制', tr(m[1], depth + 1));
      m = /^Move to (.+)$/i.exec(s);
      if (m) return joinCn('移动到', tr(m[1], depth + 1));
      m = /^Remove (.+) from Recent$/i.exec(s);
      if (m) return '从最近记录中移除 ' + m[1];
      m = /^Search Google for [“"](.+)[”"]$/i.exec(s);
      if (m) return '在 Google 中搜索“' + m[1] + '”';
      m = /^Switch to (.+)$/i.exec(s);
      if (m) return joinCn('切换到', tr(m[1], depth + 1));
      m = /^Connect to (.+)$/i.exec(s);
      if (m) return joinCn('连接到', tr(m[1], depth + 1));
      m = /^Open (.+)$/i.exec(s);
      if (m) return '打开 ' + tr(m[1], depth + 1);
      if (Object.prototype.hasOwnProperty.call(EXT_DICT, s)) return EXT_DICT[s];
      var low = s.toLowerCase();
      if (Object.prototype.hasOwnProperty.call(EXT_DICT_LOWER, low)) return EXT_DICT_LOWER[low];
      return s;
    }

    function walk(item) {
      if (!item || typeof item !== 'object') return;
      try {
        if (typeof item.label === 'string' && item.label) {
          item.label = tr(item.label, 0);
        } else if (!item.label && typeof item.role === 'string' && ROLES[item.role]) {
          item.label = ROLES[item.role];
        }
        if (item.id === 'check-for-updates' && typeof item.click === 'function' && !item.click.__AG_ZH_UPDATER__) {
          var origClick = item.click;
          var wrappedClick = function (mi) {
            if (mi && typeof mi.label === 'string' && Object.prototype.hasOwnProperty.call(REVERSE_UPDATER, mi.label)) {
              try { mi.label = REVERSE_UPDATER[mi.label]; } catch (e) {}
            }
            try { return origClick.apply(this, arguments); }
            finally {
              if (mi && typeof mi.label === 'string') {
                try { mi.label = tr(mi.label, 0); } catch (e) {}
              }
            }
          };
          wrappedClick.__AG_ZH_UPDATER__ = true;
          item.click = wrappedClick;
        }
        var sub = item.submenu;
        if (sub && typeof sub === 'object') {
          if (Array.isArray(sub)) sub.forEach(walk);
          else if (Array.isArray(sub.items)) sub.items.forEach(walk);
        }
      } catch (e) {}
    }

    var origSet = Menu.setApplicationMenu;
    if (typeof origSet === 'function') {
      Menu.setApplicationMenu = function (menu) {
        try { if (menu && Array.isArray(menu.items)) menu.items.forEach(walk); } catch (e) {}
        return origSet.apply(this, arguments);
      };
    }
    var origBuild = Menu.buildFromTemplate;
    if (typeof origBuild === 'function') {
      Menu.buildFromTemplate = function (template) {
        try { if (Array.isArray(template)) template.forEach(walk); } catch (e) {}
        return origBuild.apply(this, arguments);
      };
    }
    var Tray = electron && electron.Tray;
    if (Tray && Tray.prototype && typeof Tray.prototype.setContextMenu === 'function' && !Tray.prototype.__AG_ZH_TRAY__) {
      var origTraySet = Tray.prototype.setContextMenu;
      Tray.prototype.setContextMenu = function (menu) {
        try { if (menu && Array.isArray(menu.items)) menu.items.forEach(walk); } catch (e) {}
        return origTraySet.apply(this, arguments);
      };
      Tray.prototype.__AG_ZH_TRAY__ = true;
    }
    Menu.__AG_ZH_MENU__ = true;
  } catch (e) {
    try { console.error('[Antigravity-ZH] 菜单补丁失败', e); } catch (_) {}
  }
})();"""

DIALOG_PATCH_JS = """(function () {
  try {
    var electron = require('electron');
    var dialog = electron && electron.dialog;
    if (!dialog || dialog.__AG_ZH_DIALOG__) return;
    var LABELS = __DIALOG_LABELS__;
    function tr(s) {
      if (typeof s !== 'string' || !s) return s;
      if (Object.prototype.hasOwnProperty.call(LABELS, s)) return LABELS[s];
      var t = s.trim();
      if (Object.prototype.hasOwnProperty.call(LABELS, t)) return LABELS[t];
      var m = /^The WSL distro "(.+)" is no longer installed\\.$/.exec(t);
      if (m) return 'WSL 发行版“' + m[1] + '”已不再安装。';
      m = /^(.+) wants to connect to a (.+)$/.exec(t);
      if (m) {
        var kind = m[2] === 'USB device' ? ' USB 设备' : (m[2] === 'serial port' ? '串口' : ' ' + m[2]);
        return m[1] + ' 想要连接到' + kind;
      }
      m = /^Stop the Antigravity server on (.+)\\?$/.exec(t);
      if (m) return '要停止 ' + m[1] + ' 上的 Antigravity 服务器吗？';
      m = /^Not connected to (.+)$/.exec(t);
      if (m) return '未连接到 ' + m[1];
      m = /^Allow (.+) to use your microphone\\?$/.exec(t);
      if (m) return '允许 ' + m[1] + ' 使用您的麦克风吗？';
      m = /^Sign in to your organization for (.+)\\?$/.exec(t);
      if (m) return '要登录 ' + m[1] + ' 对应的组织账号吗？';
      m = /^Finish this sign-in on (.+)\\?$/.exec(t);
      if (m) return '要在 ' + m[1] + ' 上完成此次登录吗？';
      m = /^Sign in to (.+)$/.exec(t);
      if (m) return '登录到 ' + m[1];
      m = /^(.+) is running server ([^;]+);\\s*this app is ([^.]+)\\.\\s*Restart the server now\\?$/.exec(t);
      if (m) return m[1] + ' 正在运行服务器 ' + m[2] + '；当前应用版本为 ' + m[3] + '。是否立即重启服务器？';
      m = /^(.+) still runs Antigravity server ([^.]+)\\.?$/.exec(t);
      if (m) return m[1] + ' 仍在运行 Antigravity 服务器 ' + m[2] + '。';
      m = /^(.+) can't be the SSH config file$/.exec(t);
      if (m) return m[1] + ' 不能用作 SSH 配置文件';
      m = /^SSH:\\s*(.+)$/.exec(t);
      if (m) return 'SSH：' + m[1];
      m = /^The page in this window comes from (.+?)\\.\\s*If you allow it,\\s*([\\s\\S]+)$/.exec(t);
      if (m) return '此窗口中的页面来自 ' + m[1] + '。如果允许，该页面将可以使用您的麦克风。';
      m = /^Any (.+?) still running on it stops\\.\\s*The server starts again with this app's version\\.$/.exec(t);
      if (m) return '其上仍在运行的任务将会停止，随后服务器将以当前应用版本重新启动。';
      return s;
    }
    function patchOptions(o) {
      try {
        if (!o || typeof o !== 'object') return;
        if (typeof o.title === 'string') o.title = tr(o.title);
        if (typeof o.message === 'string') o.message = tr(o.message);
        if (typeof o.detail === 'string') o.detail = tr(o.detail);
        if (typeof o.checkboxLabel === 'string') o.checkboxLabel = tr(o.checkboxLabel);
        if (typeof o.buttonLabel === 'string') o.buttonLabel = tr(o.buttonLabel);
        if (Array.isArray(o.buttons)) o.buttons = o.buttons.map(tr);
      } catch (e) {}
    }
    function argOptions(a, b) {
      if (b && typeof b === 'object') return b;
      if (a && typeof a === 'object') return a;
      return null;
    }
    var names = ['showMessageBox', 'showMessageBoxSync', 'showOpenDialog', 'showOpenDialogSync',
                 'showSaveDialog', 'showSaveDialogSync', 'showErrorBox'];
    for (var i = 0; i < names.length; i++) {
      try {
        var name = names[i];
        var fn = dialog[name];
        if (typeof fn !== 'function') continue;
        dialog[name] = (function (orig, fnName) {
          return function (a, b) {
            try { patchOptions(argOptions(a, b)); } catch (e) {}
            if (fnName === 'showErrorBox') {
              try { return orig.call(this, tr(a), tr(b)); } catch (e) {}
            }
            return orig.apply(this, arguments);
          };
        })(fn, name);
      } catch (e) {}
    }
    dialog.__AG_ZH_DIALOG__ = true;
  } catch (e) {
    try { console.error('[Antigravity-ZH] 对话框补丁失败', e); } catch (_) {}
  }
})();"""

def build_menu_block():
    js = MENU_PATCH_JS.replace("__MENU_LABELS__", _js_map(MENU_LABELS))
    return js.replace("__MENU_ROLES__", _js_map(MENU_ROLES))

def build_dialog_block():
    return DIALOG_PATCH_JS.replace("__DIALOG_LABELS__", _js_map(DIALOG_LABELS))

def _truncate_tail(content, markers):
    idx = -1
    for m in markers:
        if not m:
            continue
        i = content.find(m)
        if i >= 0 and (idx < 0 or i < idx):
            idx = i
    if idx >= 0:
        content = content[:idx]
    return content.rstrip() + "\n"

def apply_blocks(path, blocks, engine=False):
    """清除旧注入块（保留第三方插件块）后，把 blocks 以标记块形式追加到文件末尾。"""
    content = read_text(path)
    content = content.replace(LEGACY_MENU_CALL, "")
    content = BLOCK_PAIR_RE.sub("\n", content)
    markers = [BLOCK_BEGIN_PREFIX] + LEGACY_MARKERS
    if engine:
        markers = markers + [ENGINE_START_MARKER]
    if any(m and m in content for m in markers):
        content = _truncate_tail(content, markers)
    else:
        content = content.rstrip() + "\n"
    for name, body in blocks:
        content += "\n" + (BLOCK_BEGIN % name) + "\n" + body.rstrip() + "\n" + (BLOCK_END % name) + "\n"
    write_text(path, content)
    return content

def patch_loading_overlay(tmp):
    path = os.path.join(tmp, "dist", "loadingOverlay.js")
    if not os.path.exists(path):
        say("[!] loadingOverlay.js 不存在，跳过加载画面翻译")
        return False
    content = read_text(path)
    if "AG_ZH_LOADING" in content:
        say("[*] loadingOverlay.js 已含中文加载提示，跳过")
        return True
    snippet = '正在加载 Antigravity'
    for bad in ("$", "`", "\\"):
        if bad in snippet:
            say("[!] 加载提示文本包含危险字符，跳过")
            return False
    old = '<div class="text">Loading Antigravity</div>'
    if old in content:
        content = content.replace(old, '<div class="text">' + snippet + '</div> <!-- AG_ZH_LOADING -->', 1)
        write_text(path, content)
        say("[OK] 加载画面翻译完成")
        return True
    if "</svg>" in content:
        css_anchor = "  @keyframes logo-pulse {"
        text_css = "  .text { margin-top: 16px; font-size: 14px; letter-spacing: 0.02em; opacity: 0.7; }\n"
        if ".text {" not in content and css_anchor in content:
            content = content.replace(css_anchor, text_css + css_anchor, 1)
        content = content.replace("</svg>", "</svg>\n  <div class=\"text\">" + snippet +
                                  "</div> <!-- AG_ZH_LOADING -->", 1)
        write_text(path, content)
        say("[OK] 加载画面翻译完成")
        return True
    say("[!] loadingOverlay.js 锚点未匹配，跳过加载画面翻译")
    return False

def original_unpacked_set(asar_path):
    """读取原 asar 中被标记为 unpacked 的文件集合（只读头，很快）。"""
    try:
        return set(rel for rel, size, unp in asar.list_files(asar_path) if unp)
    except Exception:
        return set()

def verify_new_asar(path, tmp_dir, patched_rels, expected_unpacked=None):
    """结构校验：能读头、文件数一致、unpacked 集合保持、关键注入文件含标记、入口文件存在。"""
    header_ok = False
    try:
        files = asar.list_files(path)
        header_ok = True
    except Exception as e:
        return False, "重建的 app.asar 无法读取: %s" % e
    expected = 0
    for root, dirs, fs in os.walk(tmp_dir):
        expected += len(fs)
    if len(files) != expected:
        return False, "文件数量不一致（期望 %d，实际 %d）" % (expected, len(files))
    names = set(rel for rel, size, unp in files)
    if expected_unpacked:
        got_unpacked = set(rel for rel, size, unp in files if unp)
        if got_unpacked != expected_unpacked:
            return False, "unpacked 文件集合不一致（期望 %d，实际 %d）" % (
                len(expected_unpacked), len(got_unpacked))
    try:
        pkg = asar.read_json(path, "package.json")
    except Exception as e:
        return False, "读取 package.json 失败: %s" % e
    main_rel = str(pkg.get("main") or "").replace("\\", "/").lstrip("./")
    if main_rel and main_rel not in names:
        return False, "入口文件不存在: %s" % main_rel
    for rel, marker in patched_rels:
        try:
            text = asar.read_file(path, rel).decode("utf-8", "ignore")
        except Exception as e:
            return False, "读取 %s 失败: %s" % (rel, e)
        if marker not in text:
            return False, "%s 缺少注入标记 %s" % (rel, marker)
    return True, "ok"

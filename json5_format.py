import sublime
import sublime_plugin
import subprocess

SETTINGS_FILE = "Json5Formatter.sublime-settings"

_JSON5_CODE = (
    "import json, sys, json5; "
    "print(json5.dumps(json5.loads(sys.stdin.read()), indent={indent}))"
)

_MINIFY_CODE = (
    "import json, sys, json5; "
    "json.dump(json5.loads(sys.stdin.read()), sys.stdout, "
    "indent=None, separators=(',', ':'))"
)

_PYTHON_CMD = None


def _find_python():
    global _PYTHON_CMD
    if _PYTHON_CMD is not None:
        return _PYTHON_CMD
    for cmd in ["py", "python"]:
        try:
            proc = subprocess.Popen(
                [cmd, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            proc.communicate()
            if proc.returncode == 0:
                _PYTHON_CMD = cmd
                return cmd
        except OSError:
            continue
    return None


def _run(args, text):
    cmd = [_find_python()] + args
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate(text.encode("utf-8"))
    if proc.returncode != 0:
        raise Exception(err.decode("utf-8").strip())
    result = out.decode("utf-8")
    result = result.replace("\r\n", "\n").replace("\r", "\n")
    return result.strip()


def _ensure_line_ending(text, view):
    le = view.line_endings()
    if le == "Windows":
        text = text.replace("\n", "\r\n")
    elif le == "CR":
        text = text.replace("\n", "\r")
    return text


def plugin_loaded():
    if _find_python() is None:
        sublime.error_message(
            "Json5Formatter: Python not found. "
            "Install Python and run: pip install json5"
        )
    sublime.load_settings(SETTINGS_FILE)


class Json5FormatCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        s = sublime.load_settings(SETTINGS_FILE)
        indent = s.get("indent", 4)

        from .jsonc_formatter import format_json5

        regions = [r for r in view.sel() if not r.empty()]
        if not regions:
            regions = [sublime.Region(0, view.size())]

        for region in regions:
            raw = view.substr(region).strip()
            if not raw:
                continue
            try:
                result = format_json5(raw, indent)
            except Exception as e:
                sublime.error_message("JSON5 Format: {0}".format(e))
                return
            result = _ensure_line_ending(result + "\n", view)
            view.replace(edit, region, result)


class Json5FormatAsJson5Command(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        s = sublime.load_settings(SETTINGS_FILE)
        indent = s.get("indent", 4)
        code = _JSON5_CODE.format(indent=indent)

        regions = [r for r in view.sel() if not r.empty()]
        if not regions:
            regions = [sublime.Region(0, view.size())]

        for region in regions:
            raw = view.substr(region).strip()
            if not raw:
                continue
            try:
                result = _run(["-c", code], raw)
            except Exception as e:
                sublime.error_message("JSON5 Format: {0}".format(e))
                return
            result = _ensure_line_ending(result + "\n", view)
            view.replace(edit, region, result)


class Json5MinifyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        regions = [r for r in view.sel() if not r.empty()]
        if not regions:
            regions = [sublime.Region(0, view.size())]

        for region in regions:
            raw = view.substr(region).strip()
            if not raw:
                continue
            try:
                result = _run(["-c", _MINIFY_CODE], raw)
            except Exception as e:
                sublime.error_message("JSON5 Minify: {0}".format(e))
                return
            result = _ensure_line_ending(result, view)
            view.replace(edit, region, result)

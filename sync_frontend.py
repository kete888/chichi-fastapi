"""一键同步 + 打包。

    python sync_frontend.py

依次做三件事：
    1. 同步前端到   ~/Desktop/今天吃啥-前端/
    2. 复制整个项目 ~/Desktop/今天吃啥-完整项目/   （不含 .env / .idea / __pycache__）
    3. 打包成       ~/Desktop/今天吃啥-完整项目.zip
"""

import shutil
import subprocess
from pathlib import Path

API = "http://127.0.0.1:8000"

SRC = Path(__file__).resolve().parent
DESKTOP = Path.home() / "Desktop"

FRONTEND_DST = DESKTOP / "今天吃啥-前端"
PROJECT_DST = DESKTOP / "今天吃啥-完整项目"
ZIP_PATH = DESKTOP / "今天吃啥-完整项目.zip"

# 打包时整体复制的目录
PACKAGE_DIRS = [
    "core", "db", "models", "schemas", "crud", "routers", "templates", "static",
]

# 打包时单独复制的文件
PACKAGE_FILES = [
    "main.py", "requirements.txt", ".env.example", "README.md",
    "sync_frontend.py", "test_main.http",
]

# 永远不打包的东西（.env 里有密码和密钥）
IGNORE = shutil.ignore_patterns(
    "__pycache__", "*.pyc", ".DS_Store", ".idea", ".env", ".venv", "venv",
)


def sync_frontend() -> None:
    """复制前端，并把 /static/ 改成绝对地址、给 app.js 加 API_BASE。"""
    (FRONTEND_DST / "templates").mkdir(parents=True, exist_ok=True)
    (FRONTEND_DST / "static/css").mkdir(parents=True, exist_ok=True)
    (FRONTEND_DST / "static/js").mkdir(parents=True, exist_ok=True)
    (FRONTEND_DST / "static/video").mkdir(parents=True, exist_ok=True)

    # 样式 / 视频 / 说明直接复制
    (FRONTEND_DST / "static/css/style.css").write_text(
        (SRC / "static/css/style.css").read_text(encoding="utf-8"), encoding="utf-8")

    for item in (SRC / "static/video").iterdir():
        if item.is_file() and item.suffix.lower() in {".mp4", ".webm", ".md"}:
            shutil.copy2(item, FRONTEND_DST / "static/video" / item.name)

    # 页面：/static/ 改绝对地址
    for page in (SRC / "templates").glob("*.html"):
        html = page.read_text(encoding="utf-8").replace('"/static/', f'"{API}/static/')
        (FRONTEND_DST / "templates" / page.name).write_text(html, encoding="utf-8")

    # 脚本：加 API_BASE，并给 fetch 加前缀
    js = (SRC / "static/js/app.js").read_text(encoding="utf-8")
    js = js.replace(
        "// ============ 工具 ============",
        f"// 后端地址（双击打开时需要完整地址）\nconst API_BASE = '{API}';\n\n// ============ 工具 ============",
        1,
    )
    js = js.replace("await fetch(path, {", "await fetch(API_BASE + path, {", 1)
    (FRONTEND_DST / "static/js/app.js").write_text(js, encoding="utf-8")

    print(f"① 前端已同步到 {FRONTEND_DST}")


def package_project() -> None:
    """复制整个项目（不含敏感文件和缓存），再打 zip。"""
    if PROJECT_DST.exists():
        shutil.rmtree(PROJECT_DST)
    PROJECT_DST.mkdir(parents=True)

    for name in PACKAGE_DIRS:
        src = SRC / name
        if src.is_dir():
            shutil.copytree(src, PROJECT_DST / name, ignore=IGNORE)

    for name in PACKAGE_FILES:
        src = SRC / name
        if src.is_file():
            shutil.copy2(src, PROJECT_DST / name)

    print(f"② 项目已复制到 {PROJECT_DST}")

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    # macOS 上 ditto 能正确处理中文文件名
    result = subprocess.run(
        ["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", PROJECT_DST.name, ZIP_PATH.name],
        cwd=DESKTOP,
        capture_output=True,
    )
    if result.returncode != 0:
        shutil.make_archive(str(ZIP_PATH.with_suffix("")), "zip", DESKTOP, PROJECT_DST.name)

    size = ZIP_PATH.stat().st_size / 1024 / 1024
    print(f"③ 已打包 {ZIP_PATH}  ({size:.1f} MB)")


def main() -> None:
    sync_frontend()
    package_project()
    print("\n完成。桌面上现在是三份：前端副本 / 完整项目 / 压缩包。")


if __name__ == "__main__":
    main()

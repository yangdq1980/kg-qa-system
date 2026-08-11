"""
目标机器环境检查脚本
在目标工作站上运行：python scripts/check_env.py
检查所有依赖是否就绪，输出环境报告
"""
import sys
import platform
import importlib
import subprocess
import requests
from pathlib import Path


def check_python():
    """检查 Python 版本"""
    print("=" * 60)
    print("【1/6】Python 环境")
    print("=" * 60)
    version = platform.python_version()
    print(f"  Python 版本: {version}")
    major, minor = map(int, version.split(".")[:2])
    if (major, minor) >= (3, 10) and (major, minor) < (3, 14):
        print("  ✓ 版本兼容（推荐 3.10 / 3.11 / 3.12）")
    elif (major, minor) >= (3, 14):
        print("  ⚠ 版本过高（3.14+），可能存在依赖冲突，建议使用 3.11")
    else:
        print("  ✗ 版本过低，需要 3.10+")
    print(f"  可执行路径: {sys.executable}")
    return (major, minor) >= (3, 10)


def check_dependencies():
    """检查 Python 依赖包"""
    print("\n" + "=" * 60)
    print("【2/6】Python 依赖包")
    print("=" * 60)
    required = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "networkx": "networkx",
        "matplotlib": "matplotlib",
        "docx": "python-docx",
        "markdown": "markdown",
        "sqlalchemy": "sqlalchemy",
        "requests": "requests",
        "pydantic": "pydantic",
        "dotenv": "python-dotenv",
        "numpy": "numpy",
    }
    all_ok = True
    for import_name, pkg_name in required.items():
        try:
            mod = importlib.import_module(import_name)
            ver = getattr(mod, "__version__", "未知")
            print(f"  ✓ {pkg_name}: {ver}")
        except ImportError:
            print(f"  ✗ {pkg_name}: 未安装")
            all_ok = False
    if not all_ok:
        print("\n  安装命令: pip install -r requirements.txt")
    return all_ok


def check_ollama():
    """检查 Ollama 服务"""
    print("\n" + "=" * 60)
    print("【3/6】Ollama 服务")
    print("=" * 60)
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            print(f"  ✓ 服务运行中")
            print(f"  可用模型 ({len(models)} 个):")
            for m in models:
                print(f"    - {m}")
            # 检查是否有问答模型
            qa_models = [m for m in models if any(k in m.lower() for k in ["deepseek", "qwen", "llama", "mistral"])]
            embed_models = [m for m in models if "bge" in m.lower() or "embed" in m.lower()]
            if qa_models:
                print(f"  ✓ 问答模型可用: {', '.join(qa_models)}")
            else:
                print("  ⚠ 未检测到问答模型，建议拉取: ollama pull deepseek-r1:7b")
            if embed_models:
                print(f"  ✓ 嵌入模型可用: {', '.join(embed_models)}")
            else:
                print("  ⚠ 未检测到嵌入模型，建议拉取: ollama pull bge-large")
            return True
        else:
            print(f"  ✗ 服务响应异常: HTTP {resp.status_code}")
            return False
    except requests.ConnectionError:
        print("  ✗ 无法连接 Ollama，请确认服务已启动: ollama serve")
        return False
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
        return False


def check_glm_api():
    """检查云端 GLM API 配置"""
    print("\n" + "=" * 60)
    print("【4/6】云端 GLM API（三元组抽取用）")
    print("=" * 60)
    # 检查 .env 或环境变量
    env_path = Path(__file__).parent.parent / ".env"
    api_key = None
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GLM_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    import os
    api_key = api_key or os.environ.get("GLM_API_KEY", "")

    if api_key:
        masked = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "***"
        print(f"  ✓ API Key 已配置: {masked}")
        print("  （未实际调用，避免消耗额度）")
        return True
    else:
        print("  ⚠ API Key 未配置")
        print("  请在项目根目录创建 .env 文件，添加: GLM_API_KEY=你的key")
        print("  三元组抽取功能将不可用（可改用本地 Ollama 抽取，但质量较低）")
        return False


def check_vector_store():
    """检查向量库"""
    print("\n" + "=" * 60)
    print("【5/6】向量库（enterprise-rag 复用）")
    print("=" * 60)
    base_dir = Path(__file__).parent.parent
    # 检查默认路径
    candidates = [
        base_dir / "data" / "vector_store",
        base_dir / "data" / "vector_store" / "faiss",
    ]
    found = False
    for path in candidates:
        if path.exists():
            files = list(path.glob("*"))
            print(f"  ✓ 向量库目录存在: {path}")
            print(f"    文件数: {len(files)}")
            for f in files[:5]:
                print(f"      - {f.name}")
            found = True
            break
    if not found:
        print("  ⚠ 未找到向量库目录")
        print("  请确认 enterprise-rag 的向量库路径，并在 config/settings.py 中配置 VECTOR_STORE_PATH")
        print("  问答的 RAG 部分将不可用，但图谱问答仍可运行")
    return found


def check_project_structure():
    """检查项目目录结构"""
    print("\n" + "=" * 60)
    print("【6/6】项目结构")
    print("=" * 60)
    base_dir = Path(__file__).parent.parent
    required_dirs = ["app", "app/routers", "app/services", "app/models",
                     "app/static", "config", "data", "db", "scripts", "tests"]
    required_files = ["app/main.py", "config/settings.py", "requirements.txt",
                      "app/static/index.html"]
    all_ok = True
    for d in required_dirs:
        p = base_dir / d
        if p.exists():
            print(f"  ✓ 目录: {d}/")
        else:
            print(f"  ✗ 目录缺失: {d}/")
            all_ok = False
    for f in required_files:
        p = base_dir / f
        if p.exists():
            print(f"  ✓ 文件: {f}")
        else:
            print(f"  ✗ 文件缺失: {f}")
            all_ok = False
    return all_ok


def main():
    print("\n" + "█" * 60)
    print("  知识图谱问答系统 — 目标机器环境检查")
    print("█" * 60)

    results = {
        "Python": check_python(),
        "依赖包": check_dependencies(),
        "Ollama": check_ollama(),
        "GLM API": check_glm_api(),
        "向量库": check_vector_store(),
        "项目结构": check_project_structure(),
    }

    print("\n" + "=" * 60)
    print("【检查总结】")
    print("=" * 60)
    for name, ok in results.items():
        status = "✓ 通过" if ok else "✗ 需处理"
        print(f"  {name}: {status}")

    passed = sum(results.values())
    total = len(results)
    print(f"\n  总计: {passed}/{total} 项通过")

    if passed == total:
        print("\n  🎉 环境检查全部通过！可以启动系统:")
        print("     python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n  ⚠ 部分项未通过，请根据上述提示处理后再启动。")
        print("  核心依赖（Python + 依赖包 + Ollama + 项目结构）必须通过才能运行。")
        print("  GLM API 和向量库为可选，缺失时对应功能降级。")

    return 0 if passed >= 4 else 1


if __name__ == "__main__":
    sys.exit(main())

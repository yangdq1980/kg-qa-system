"""
三元组批量抽取脚本（P1 阶段实现核心逻辑）
当前为模板框架，P1 阶段填充完整实现

运行方式：
  python scripts/extract_triples.py --all           # 抽取所有文档
  python scripts/extract_triples.py --doc path.docx # 抽取指定文档
  python scripts/extract_triples.py --resume        # 断点续跑
"""
import sys
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import settings


def parse_documents(docs_dir: Path) -> list:
    """
    解析文档目录，返回文档段落列表
    Word: python-docx 读取，按标题/段落切分
    MD: 直接读取，按 ## 标题切分
    """
    # TODO P1: 实现文档解析
    print(f"[解析] 扫描目录: {docs_dir}")
    documents = []
    for f in docs_dir.glob("*"):
        if f.suffix.lower() in (".docx", ".doc"):
            print(f"  - Word: {f.name}")
            # from docx import Document
            # doc = Document(f)
            # sections = [...]
        elif f.suffix.lower() in (".md", ".markdown"):
            print(f"  - Markdown: {f.name}")
            # text = f.read_text(encoding="utf-8")
            # sections = [...]
    return documents


def extract_triples_with_glm(section_text: str) -> list:
    """
    调用云端 GLM 抽取三元组
    Prompt 基于已确认的本体 Schema（11类实体 + 8类关系）
    返回: [{"subject": "", "subject_type": "", "relation": "", "object": "", "object_type": ""}]
    """
    # TODO P1: 构造 Prompt，调用 GLM API，解析返回的 JSON
    prompt = f"""
你是一个制造业知识抽取专家。请从以下文本中抽取三元组。

实体类型（只能从以下选择）：{', '.join(settings.ENTITY_TYPES)}
关系类型（只能从以下选择）：{', '.join(settings.RELATION_TYPES)}

文本：
{section_text}

请以 JSON 数组格式返回，每个元素包含 subject, subject_type, relation, object, object_type。
只返回 JSON，不要其他解释。
"""
    # 调用 GLM API...
    return []


def disambiguate_entities(triples: list) -> list:
    """实体消歧：同名同类型合并，简称全称对齐"""
    # TODO P1: 实现消歧逻辑
    return triples


def save_to_db(triples: list, doc_id: str):
    """将三元组存入 SQLite 和 NetworkX 图"""
    # TODO P1: 写入数据库，更新图谱缓存
    pass


def main():
    parser = argparse.ArgumentParser(description="三元组批量抽取")
    parser.add_argument("--all", action="store_true", help="抽取所有文档")
    parser.add_argument("--doc", type=str, help="抽取指定文档路径")
    parser.add_argument("--resume", action="store_true", help="断点续跑（跳过已抽取）")
    parser.add_argument("--use-local", action="store_true", help="使用本地Ollama抽取（不使用云端GLM）")
    args = parser.parse_args()

    print("=" * 60)
    print("  三元组批量抽取（P1 模板，核心逻辑待实现）")
    print("=" * 60)
    print(f"  文档目录: {settings.DOCS_DIR}")
    print(f"  抽取模型: {'本地 Ollama' if args.use_local else '云端 GLM (' + settings.GLM_MODEL + ')'}")
    print(f"  实体类型: {len(settings.ENTITY_TYPES)} 种")
    print(f"  关系类型: {len(settings.RELATION_TYPES)} 种")
    print()

    docs_dir = BASE_DIR / settings.DOCS_DIR
    if not docs_dir.exists():
        print(f"✗ 文档目录不存在: {docs_dir}")
        print("  请将 Word/MD 文档放入 data/docs/ 目录后再运行")
        return

    documents = parse_documents(docs_dir)
    print(f"\n共发现 {len(documents)} 个文档（段落级待统计）")
    print("P1 阶段将实现完整的抽取、消歧、入库流程。")


if __name__ == "__main__":
    main()

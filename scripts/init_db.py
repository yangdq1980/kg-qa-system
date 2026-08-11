"""
数据库初始化脚本
在目标机器上运行：python scripts/init_db.py
创建 SQLite 表结构，初始化空图谱
"""
import sys
from pathlib import Path

# 确保项目根目录在 sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import create_engine, Column, String, Text, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

from config.settings import settings

Base = declarative_base()


# ===== 表结构定义 =====

class Document(Base):
    """文档元数据"""
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, comment="文档MD5或路径哈希")
    name = Column(String(255), nullable=False, comment="文档名")
    path = Column(String(512), nullable=False, comment="文档路径")
    doc_type = Column(String(32), default="word", comment="文档类型: word/markdown/pdf")
    size_bytes = Column(Integer, default=0)
    section_count = Column(Integer, default=0, comment="切分后的段落数")
    extracted = Column(Integer, default=0, comment="是否已抽取三元组: 0未 1已 2失败")
    extracted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Entity(Base):
    """实体表"""
    __tablename__ = "entities"

    id = Column(String(64), primary_key=True, comment="实体ID（名称+类型的哈希）")
    name = Column(String(255), nullable=False, comment="实体名称")
    type = Column(String(32), nullable=False, comment="实体类型")
    aliases = Column(Text, default="", comment="别名列表，JSON数组")
    source_docs = Column(Text, default="", comment="来源文档ID列表，JSON数组")
    properties = Column(Text, default="{}", comment="扩展属性，JSON")
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("idx_entity_name", "name"),
        Index("idx_entity_type", "type"),
    )


class Triple(Base):
    """三元组表"""
    __tablename__ = "triples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(String(64), ForeignKey("entities.id"), nullable=False)
    relation = Column(String(32), nullable=False, comment="关系类型")
    object_id = Column(String(64), ForeignKey("entities.id"), nullable=False)
    source_doc = Column(String(64), nullable=True, comment="来源文档ID")
    source_section = Column(String(255), nullable=True, comment="来源段落标识")
    confidence = Column(Float, default=1.0, comment="置信度 0-1")
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("idx_triple_subject", "subject_id"),
        Index("idx_triple_object", "object_id"),
        Index("idx_triple_relation", "relation"),
        Index("idx_triple_unique", "subject_id", "relation", "object_id", unique=True),
    )


class ExtractLog(Base):
    """抽取日志表"""
    __tablename__ = "extract_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String(64), nullable=False)
    status = Column(String(16), default="pending", comment="pending/running/success/failed")
    entities_extracted = Column(Integer, default=0)
    triples_extracted = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)


class QAHHistory(Base):
    """问答历史表"""
    __tablename__ = "qa_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(Text, default="[]", comment="来源列表，JSON")
    highlighted_ids = Column(Text, default="[]", comment="高亮实体ID，JSON")
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


def init_db():
    """初始化数据库"""
    db_path = BASE_DIR / settings.SQLITE_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)

    print(f"✓ 数据库已初始化: {db_path}")
    print(f"  表结构:")
    for table in Base.metadata.tables:
        print(f"    - {table}")

    # 输出统计
    Session = sessionmaker(bind=engine)
    session = Session()
    print(f"\n  当前数据量:")
    print(f"    文档数: {session.query(Document).count()}")
    print(f"    实体数: {session.query(Entity).count()}")
    print(f"    三元组数: {session.query(Triple).count()}")
    session.close()

    print("\n✓ 初始化完成。P1 阶段将开始文档解析和三元组抽取。")


if __name__ == "__main__":
    init_db()

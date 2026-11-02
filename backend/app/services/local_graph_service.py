"""
本地知识图谱服务 (Local Graph Service)
作为 Zep Cloud 的完全离线/本地替代引擎，实现零成本、免 API Key 的 GraphRAG
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from ..config import Config
from ..utils.logger import get_logger
from ..utils.llm_client import LLMClient

logger = get_logger('mirofish.local_graph')


@dataclass
class LocalNode:
    uuid: str
    name: str
    labels: List[str]
    summary: str
    attributes: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LocalEdge:
    uuid: str
    name: str
    fact: str
    source_node_uuid: str
    target_node_uuid: str
    source_node_name: Optional[str] = None
    target_node_name: Optional[str] = None
    valid_at: Optional[str] = None
    invalid_at: Optional[str] = None
    expired_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LocalGraphService:
    """本地知识图谱管理器"""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.join(Config.UPLOAD_FOLDER, 'local_graphs')
        os.makedirs(self.base_dir, exist_ok=True)

    def _graph_dir(self, graph_id: str) -> str:
        d = os.path.join(self.base_dir, graph_id)
        os.makedirs(d, exist_ok=True)
        return d

    def create_graph(self, graph_name: str = "MiroFish Local Graph") -> str:
        graph_id = f"local_{uuid.uuid4().hex[:12]}"
        g_dir = self._graph_dir(graph_id)
        
        meta = {
            "graph_id": graph_id,
            "name": graph_name,
            "created_at": datetime.now().isoformat(),
            "node_count": 0,
            "edge_count": 0,
            "entity_types": []
        }
        with open(os.path.join(g_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        with open(os.path.join(g_dir, "nodes.json"), "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

        with open(os.path.join(g_dir, "edges.json"), "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

        with open(os.path.join(g_dir, "episodes.json"), "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

        logger.info(f"Created local graph: {graph_id} ({graph_name})")
        return graph_id

    def build_from_text(
        self,
        graph_id: str,
        text: str,
        ontology: Dict[str, Any],
        llm_client: Optional[LLMClient] = None
    ) -> Dict[str, Any]:
        """使用 LLM 或规则从文本及本体提取实体与关系，构建本地图谱"""
        g_dir = self._graph_dir(graph_id)
        entity_types = [et.get("name") for et in ontology.get("entity_types", []) if et.get("name")]
        
        extracted_nodes: List[Dict[str, Any]] = []
        extracted_edges: List[Dict[str, Any]] = []

        # 尝试通过 LLM 进行实体与关系抽取
        client = llm_client or LLMClient()
        prompt = f"""Kamu adalah pakar Information Extraction. Ekstraksilah entitas dan relasi penting dari dokumen berikut berdasarkan skema ontologi yang diberikan.

SKEMA ENTITAS TERSEDIA:
{json.dumps(entity_types, ensure_ascii=False)}

DOKUMEN:
{text[:4000]}

Format output WAJIB JSON:
{{
  "nodes": [
    {{"name": "Nama Entitas", "type": "Tipe dari Skema", "summary": "Deskripsi singkat peran entitas"}}
  ],
  "edges": [
    {{"source": "Nama Entitas A", "target": "Nama Entitas B", "relation": "TIPE_RELASI", "fact": "Fakta hubungan"}}
  ]
}}
Hanya output JSON valid!"""

        try:
            res = client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            raw = json.loads(res.strip())
            raw_nodes = raw.get("nodes", [])
            raw_edges = raw.get("edges", [])
        except Exception as e:
            logger.warning(f"LLM graph extraction error: {e}, using heuristic fallback")
            raw_nodes = []
            raw_edges = []

        # 兜底：如果 LLM 未能提取出足够节点，根据本体 examples 和词频生成基本节点
        if len(raw_nodes) < 3:
            for et in ontology.get("entity_types", []):
                t_name = et.get("name", "Person")
                for ex in et.get("examples", [])[:2]:
                    raw_nodes.append({
                        "name": ex,
                        "type": t_name,
                        "summary": f"Entitas berkarakter {t_name} dalam konteks simulasi."
                    })

        # 映射生成唯一的 UUID
        name_to_uuid = {}
        for item in raw_nodes:
            n_name = item.get("name", "").strip()
            if not n_name or n_name in name_to_uuid:
                continue
            n_uuid = f"node_{uuid.uuid4().hex[:8]}"
            name_to_uuid[n_name] = n_uuid
            t_type = item.get("type", "Person")
            extracted_nodes.append({
                "uuid": n_uuid,
                "name": n_name,
                "labels": [t_type, "Entity", "Node"],
                "summary": item.get("summary", f"{n_name} adalah {t_type}"),
                "attributes": {"entity_type": t_type}
            })

        for edge in raw_edges:
            src = edge.get("source", "").strip()
            tgt = edge.get("target", "").strip()
            if src in name_to_uuid and tgt in name_to_uuid and src != tgt:
                extracted_edges.append({
                    "uuid": f"edge_{uuid.uuid4().hex[:8]}",
                    "name": edge.get("relation", "RELATES_TO"),
                    "fact": edge.get("fact", f"{src} berinteraksi dengan {tgt}"),
                    "source_node_uuid": name_to_uuid[src],
                    "target_node_uuid": name_to_uuid[tgt],
                    "source_node_name": src,
                    "target_node_name": tgt,
                    "valid_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        # 写入文件
        with open(os.path.join(g_dir, "nodes.json"), "w", encoding="utf-8") as f:
            json.dump(extracted_nodes, f, ensure_ascii=False, indent=2)

        with open(os.path.join(g_dir, "edges.json"), "w", encoding="utf-8") as f:
            json.dump(extracted_edges, f, ensure_ascii=False, indent=2)

        meta = {
            "graph_id": graph_id,
            "created_at": datetime.now().isoformat(),
            "node_count": len(extracted_nodes),
            "edge_count": len(extracted_edges),
            "entity_types": list(set([n["labels"][0] for n in extracted_nodes]))
        }
        with open(os.path.join(g_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return meta

    def get_nodes(self, graph_id: str) -> List[Dict[str, Any]]:
        path = os.path.join(self._graph_dir(graph_id), "nodes.json")
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_edges(self, graph_id: str) -> List[Dict[str, Any]]:
        path = os.path.join(self._graph_dir(graph_id), "edges.json")
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_meta(self, graph_id: str) -> Dict[str, Any]:
        path = os.path.join(self._graph_dir(graph_id), "meta.json")
        if not os.path.exists(path):
            return {"graph_id": graph_id, "node_count": 0, "edge_count": 0, "entity_types": []}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def add_episode(self, graph_id: str, text: str, timestamp: Optional[str] = None):
        """记录动态时序事件 (Temporal Episode)"""
        g_dir = self._graph_dir(graph_id)
        episodes_path = os.path.join(g_dir, "episodes.json")
        episodes = []
        if os.path.exists(episodes_path):
            try:
                with open(episodes_path, "r", encoding="utf-8") as f:
                    episodes = json.load(f)
            except Exception:
                episodes = []

        episodes.append({
            "timestamp": timestamp or datetime.now().isoformat(),
            "content": text
        })
        with open(episodes_path, "w", encoding="utf-8") as f:
            json.dump(episodes[-500:], f, ensure_ascii=False, indent=2)

    def search(self, graph_id: str, query: str, limit: int = 20) -> Dict[str, Any]:
        """本地搜索：匹配事实与实体"""
        q_words = [w.lower() for w in query.replace(',', ' ').split() if len(w) > 1]
        nodes = self.get_nodes(graph_id)
        edges = self.get_edges(graph_id)

        matching_nodes = []
        for n in nodes:
            score = sum(1 for w in q_words if w in n["name"].lower() or w in n["summary"].lower())
            if score > 0 or not q_words:
                matching_nodes.append((score, n))
        matching_nodes.sort(key=lambda x: x[0], reverse=True)

        matching_edges = []
        for e in edges:
            score = sum(1 for w in q_words if w in e["fact"].lower() or w in (e.get("name") or "").lower())
            if score > 0 or not q_words:
                matching_edges.append((score, e))
        matching_edges.sort(key=lambda x: x[0], reverse=True)

        facts = [e["fact"] for _, e in matching_edges[:limit]]
        return {
            "facts": facts,
            "edges": [e for _, e in matching_edges[:limit]],
            "nodes": [n for _, n in matching_nodes[:limit]],
            "query": query,
            "total_count": len(facts)
        }

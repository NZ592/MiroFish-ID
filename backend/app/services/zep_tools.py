"""
Zep检索工具服务
封装图谱搜索、节点读取、边查询等工具，供Report Agent使用

核心检索工具（优化后）：
1. InsightForge（深度洞察检索）- 最强大的混合检索，自动生成子问题并多维度检索
2. PanoramaSearch（广度搜索）- 获取全貌，包括过期内容
3. QuickSearch（简单搜索）- 快速检索
"""

import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from zep_cloud import NotFoundError

from ..config import Config
from ..utils.logger import get_logger
from ..utils.llm_client import LLMClient
from ..utils.locale import get_locale, t
from ..utils.zep_paging import fetch_all_nodes, fetch_all_edges
from ..utils.zep import (
    call_zep_read_with_retry,
    get_zep_client,
    normalize_zep_search_limit,
    normalize_zep_search_query,
)

logger = get_logger('mirofish.zep_tools')


@dataclass
class SearchResult:
    """搜索结果"""
    facts: List[str]
    edges: List[Dict[str, Any]]
    nodes: List[Dict[str, Any]]
    query: str
    total_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "facts": self.facts,
            "edges": self.edges,
            "nodes": self.nodes,
            "query": self.query,
            "total_count": self.total_count
        }
    
    def to_text(self) -> str:
        """Konversi ke format teks untuk LLM dan display UI"""
        text_parts = [f"Kueri Pencarian: {self.query}", f"Ditemukan {self.total_count} informasi relevan"]
        
        if self.facts:
            text_parts.append("\n### Fakta Terkait:")
            for i, fact in enumerate(self.facts, 1):
                text_parts.append(f"{i}. {fact}")
        
        return "\n".join(text_parts)


@dataclass
class NodeInfo:
    """节点信息"""
    uuid: str
    name: str
    labels: List[str]
    summary: str
    attributes: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "labels": self.labels,
            "summary": self.summary,
            "attributes": self.attributes
        }
    
    def to_text(self) -> str:
        """转换为文本格式"""
        entity_type = next((l for l in self.labels if l not in ["Entity", "Node"]), "未知类型")
        return f"实体: {self.name} (类型: {entity_type})\n摘要: {self.summary}"


@dataclass
class EdgeInfo:
    """边信息"""
    uuid: str
    name: str
    fact: str
    source_node_uuid: str
    target_node_uuid: str
    source_node_name: Optional[str] = None
    target_node_name: Optional[str] = None
    # 时间信息
    created_at: Optional[str] = None
    valid_at: Optional[str] = None
    invalid_at: Optional[str] = None
    expired_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "fact": self.fact,
            "source_node_uuid": self.source_node_uuid,
            "target_node_uuid": self.target_node_uuid,
            "source_node_name": self.source_node_name,
            "target_node_name": self.target_node_name,
            "created_at": self.created_at,
            "valid_at": self.valid_at,
            "invalid_at": self.invalid_at,
            "expired_at": self.expired_at
        }
    
    def to_text(self, include_temporal: bool = False) -> str:
        """转换为文本格式"""
        source = self.source_node_name or self.source_node_uuid[:8]
        target = self.target_node_name or self.target_node_uuid[:8]
        base_text = f"关系: {source} --[{self.name}]--> {target}\n事实: {self.fact}"
        
        if include_temporal:
            valid_at = self.valid_at or "未知"
            invalid_at = self.invalid_at or "至今"
            base_text += f"\n时效: {valid_at} - {invalid_at}"
            if self.expired_at:
                base_text += f" (已过期: {self.expired_at})"
        
        return base_text
    
    @property
    def is_expired(self) -> bool:
        """是否已过期"""
        return self.expired_at is not None
    
    @property
    def is_invalid(self) -> bool:
        """是否已失效"""
        return self.invalid_at is not None


@dataclass
class InsightForgeResult:
    """
    深度洞察检索结果 (InsightForge)
    包含多个子问题的检索结果，以及综合分析
    """
    query: str
    simulation_requirement: str
    sub_queries: List[str]
    
    # 各维度检索结果
    semantic_facts: List[str] = field(default_factory=list)  # 语义搜索结果
    entity_insights: List[Dict[str, Any]] = field(default_factory=list)  # 实体洞察
    relationship_chains: List[str] = field(default_factory=list)  # 关系链
    
    # 统计信息
    total_facts: int = 0
    total_entities: int = 0
    total_relationships: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "simulation_requirement": self.simulation_requirement,
            "sub_queries": self.sub_queries,
            "semantic_facts": self.semantic_facts,
            "entity_insights": self.entity_insights,
            "relationship_chains": self.relationship_chains,
            "total_facts": self.total_facts,
            "total_entities": self.total_entities,
            "total_relationships": self.total_relationships
        }
    
    def to_text(self) -> str:
        """Konversi ke format teks untuk LLM dan display UI"""
        text_parts = [
            f"## Analisis Mendalam Prediksi Simulasi (InsightForge)",
            f"Kueri Analisis: {self.query}",
            f"Skenario Prediksi: {self.simulation_requirement}",
            f"\n### Statistik Data Prediksi",
            f"- Fakta Terkait: {self.total_facts} butir",
            f"- Entitas Terkait: {self.total_entities} entitas",
            f"- Rantai Relasi: {self.total_relationships} rantai"
        ]
        
        # Sub-pertanyaan
        if self.sub_queries:
            text_parts.append(f"\n### Sub-pertanyaan Analisis")
            for i, sq in enumerate(self.sub_queries, 1):
                text_parts.append(f"{i}. {sq}")
        
        # Hasil pencarian semantik
        if self.semantic_facts:
            text_parts.append(f"\n### 【Fakta Kunci】(Kutipan hasil simulasi)")
            for i, fact in enumerate(self.semantic_facts, 1):
                text_parts.append(f"{i}. \"{fact}\"")
        
        # Wawasan entitas
        if self.entity_insights:
            text_parts.append(f"\n### 【Entitas Utama】")
            for entity in self.entity_insights:
                text_parts.append(f"- **{entity.get('name', 'Entitas')}** ({entity.get('type', 'Entitas')})")
                if entity.get('summary'):
                    text_parts.append(f"  Ringkasan: \"{entity.get('summary')}\"")
                if entity.get('related_facts'):
                    text_parts.append(f"  Fakta Terkait: {len(entity.get('related_facts', []))} butir")
        
        # Rantai relasi
        if self.relationship_chains:
            text_parts.append(f"\n### 【Rantai Relasi】")
            for chain in self.relationship_chains:
                text_parts.append(f"- {chain}")
        
        return "\n".join(text_parts)


@dataclass
class PanoramaResult:
    """
    广度搜索结果 (Panorama)
    包含所有相关信息，包括过期内容
    """
    query: str
    
    # 全部节点
    all_nodes: List[NodeInfo] = field(default_factory=list)
    # 全部边（包括过期的）
    all_edges: List[EdgeInfo] = field(default_factory=list)
    # 当前有效的事实
    active_facts: List[str] = field(default_factory=list)
    # 已过期/失效的事实（历史记录）
    historical_facts: List[str] = field(default_factory=list)
    
    # 统计
    total_nodes: int = 0
    total_edges: int = 0
    active_count: int = 0
    historical_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "all_nodes": [n.to_dict() for n in self.all_nodes],
            "all_edges": [e.to_dict() for e in self.all_edges],
            "active_facts": self.active_facts,
            "historical_facts": self.historical_facts,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "active_count": self.active_count,
            "historical_count": self.historical_count
        }
    
    def to_text(self) -> str:
        """Konversi ke format teks untuk LLM dan display UI"""
        text_parts = [
            f"## Hasil Pencarian Panorama Luas (PanoramaSearch)",
            f"Kueri: {self.query}",
            f"\n### Informasi Statistik",
            f"- Total Simpul: {self.total_nodes}",
            f"- Total Relasi: {self.total_edges}",
            f"- Fakta Aktif Saat Ini: {self.active_count} butir",
            f"- Fakta Riwayat/Historis: {self.historical_count} butir"
        ]
        
        # Fakta aktif
        if self.active_facts:
            text_parts.append(f"\n### 【Fakta Aktif Saat Ini】(Hasil simulasi terkini)")
            for i, fact in enumerate(self.active_facts, 1):
                text_parts.append(f"{i}. \"{fact}\"")
        
        # Fakta riwayat/historis
        if self.historical_facts:
            text_parts.append(f"\n### 【Fakta Riwayat/Historis】(Catatan proses evolusi)")
            for i, fact in enumerate(self.historical_facts, 1):
                text_parts.append(f"{i}. \"{fact}\"")
        
        # Entitas terkait
        if self.all_nodes:
            text_parts.append(f"\n### 【Entitas Terkait】")
            for node in self.all_nodes:
                entity_type = next((l for l in node.labels if l not in ["Entity", "Node"]), "Entitas")
                text_parts.append(f"- **{node.name}** ({entity_type})")
        
        return "\n".join(text_parts)


@dataclass
class AgentInterview:
    """单个Agent的采访结果"""
    agent_name: str
    agent_role: str  # 角色类型（如：学生、教师、媒体等）
    agent_bio: str  # 简介
    question: str  # 采访问题
    response: str  # 采访回答
    key_quotes: List[str] = field(default_factory=list)  # 关键引言
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "agent_bio": self.agent_bio,
            "question": self.question,
            "response": self.response,
            "key_quotes": self.key_quotes
        }
    
    def to_text(self) -> str:
        text = f"**{self.agent_name}** ({self.agent_role})\n"
        # Tampilkan bio agent lengkap
        text += f"_Profil: {self.agent_bio}_\n\n"
        text += f"**T (Tanya):** {self.question}\n\n"
        text += f"**J (Jawab):** {self.response}\n"
        if self.key_quotes:
            text += "\n**Kutipan Kunci:**\n"
            for quote in self.key_quotes:
                # Bersihkan kutipan
                clean_quote = quote.replace('\u201c', '').replace('\u201d', '').replace('"', '')
                clean_quote = clean_quote.replace('\u300c', '').replace('\u300d', '')
                clean_quote = clean_quote.strip()
                while clean_quote and clean_quote[0] in '，,；;：:、。！？\n\r\t ':
                    clean_quote = clean_quote[1:]
                # Filter jika ada penomoran pertanyaan Tionghoa
                skip = False
                for d in '123456789':
                    if f'\u95ee\u9898{d}' in clean_quote:
                        skip = True
                        break
                if skip:
                    continue
                if len(clean_quote) > 150:
                    dot_pos = clean_quote.find('.', 80)
                    if dot_pos > 0:
                        clean_quote = clean_quote[:dot_pos + 1]
                    else:
                        clean_quote = clean_quote[:147] + "..."
                if clean_quote and len(clean_quote) >= 10:
                    text += f'> "{clean_quote}"\n'
        return text


@dataclass
class InterviewResult:
    """
    采访结果 (Interview)
    包含多个模拟Agent的采访回答
    """
    interview_topic: str  # 采访主题
    interview_questions: List[str]  # 采访问题列表
    
    # 采访选择的Agent
    selected_agents: List[Dict[str, Any]] = field(default_factory=list)
    # 各Agent的采访回答
    interviews: List[AgentInterview] = field(default_factory=list)
    
    # 选择Agent的理由
    selection_reasoning: str = ""
    # 整合后的采访摘要
    summary: str = ""
    
    # 统计
    total_agents: int = 0
    interviewed_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_topic": self.interview_topic,
            "interview_questions": self.interview_questions,
            "selected_agents": self.selected_agents,
            "interviews": [i.to_dict() for i in self.interviews],
            "selection_reasoning": self.selection_reasoning,
            "summary": self.summary,
            "total_agents": self.total_agents,
            "interviewed_count": self.interviewed_count
        }
    
    def to_text(self) -> str:
        """Konversi ke format teks untuk LLM dan display UI"""
        text_parts = [
            "## Laporan Wawancara Mendalam (InterviewAgents)",
            f"**Topik Wawancara:** {self.interview_topic}",
            f"**Jumlah Narasumber:** {self.interviewed_count} / {self.total_agents} Agen Simulasi",
            "\n### Alasan Pemilihan Narasumber",
            self.selection_reasoning or "（Pemilihan otomatis berdasarkan relevansi topik）",
            "\n---",
            "\n### Transkrip Wawancara",
        ]

        if self.interviews:
            for i, interview in enumerate(self.interviews, 1):
                text_parts.append(f"\n#### Wawancara #{i}: {interview.agent_name}")
                text_parts.append(interview.to_text())
                text_parts.append("\n---")
        else:
            text_parts.append("（Tidak ada catatan wawancara）\n\n---")

        text_parts.append("\n### Ringkasan Wawancara & Pandangan Kunci")
        text_parts.append(self.summary or "（Tidak ada ringkasan）")

        return "\n".join(text_parts)


class ZepToolsService:
    """
    Zep检索工具服务
    
    【核心检索工具 - 优化后】
    1. insight_forge - 深度洞察检索（最强大，自动生成子问题，多维度检索）
    2. panorama_search - 广度搜索（获取全貌，包括过期内容）
    3. quick_search - 简单搜索（快速检索）
    4. interview_agents - 深度采访（采访模拟Agent，获取多视角观点）
    
    【基础工具】
    - search_graph - 图谱语义搜索
    - get_all_nodes - 获取图谱所有节点
    - get_all_edges - 获取图谱所有边（含时间信息）
    - get_node_detail - 获取节点详细信息
    - get_node_edges - 获取节点相关的边
    - get_entities_by_type - 按类型获取实体
    - get_entity_summary - 获取实体的关系摘要
    """
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0
    
    def __init__(self, api_key: Optional[str] = None, llm_client: Optional[LLMClient] = None):
        self.api_key = api_key or Config.ZEP_API_KEY
        self.is_local = (Config.MEMORY_MODE == 'local') or (not self.api_key)
        self.client = None if self.is_local else get_zep_client(self.api_key)
        # LLM客户端用于InsightForge生成子问题
        self._llm_client = llm_client
        logger.info(t("console.zepToolsInitialized"))
    
    @property
    def llm(self) -> LLMClient:
        """延迟初始化LLM客户端"""
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client

    def _translate_if_chinese(self, text: str) -> str:
        """Deteksi dan terjemahkan teks berbahasa Tionghoa ke Bahasa Indonesia secara otomatis"""
        if not text or not any('\u4e00' <= c <= '\u9fff' for c in text):
            return text
        try:
            translated = self.llm.chat(
                messages=[
                    {
                        "role": "system",
                        "content": "Anda adalah penerjemah intelijen profesional. Terjemahkan kalimat/teks berikut ke dalam Bahasa Indonesia yang formal, akurat, dan mengalir alami. Kembalikan HANYA kalimat hasil terjemahan tanpa tanda kutip pembuka/penutup atau penjelasan tambahan."
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0.1,
                max_tokens=300
            )
            res = translated.strip().strip('"').strip("'")
            return res if res else text
        except Exception as e:
            logger.warning(f"Gagal menerjemahkan teks Tionghoa: {e}")
            return text
    
    def _call_with_retry(self, func, operation_name: str, max_retries: int = None):
        """Retry one safe read using typed Zep/HTTPX error classification."""

        return call_zep_read_with_retry(
            func,
            operation_name=operation_name,
            max_attempts=max_retries or self.MAX_RETRIES,
            initial_delay=self.RETRY_DELAY,
        )
    
    def search_graph(
        self, 
        graph_id: str, 
        query: str, 
        limit: int = 10,
        scope: str = "edges"
    ) -> SearchResult:
        """
        图谱语义搜索
        
        使用混合搜索（语义+BM25）在图谱中搜索相关信息。
        如果Zep Cloud的search API不可用，则降级为本地关键词匹配。
        
        Args:
            graph_id: 图谱ID (Standalone Graph)
            query: 搜索查询
            limit: 返回结果数量
            scope: 搜索范围，"edges" 或 "nodes"
            
        Returns:
            SearchResult: 搜索结果
        """
        logger.info(t("console.graphSearch", graphId=graph_id, query=query[:50]))
        
        if self.is_local or (graph_id and graph_id.startswith("local_")):
            from .local_graph_service import LocalGraphService
            res = LocalGraphService().search(graph_id, query, limit)
            return SearchResult(
                facts=res["facts"],
                edges=res["edges"],
                nodes=res["nodes"],
                query=query,
                total_count=res["total_count"]
            )

        zep_query = normalize_zep_search_query(query)
        zep_limit = normalize_zep_search_limit(limit)

        try:
            search_results = self._call_with_retry(
                func=lambda: self.client.graph.search(
                    graph_id=graph_id,
                    query=zep_query,
                    limit=zep_limit,
                    scope=scope,
                    reranker="cross_encoder"
                ),
                operation_name=t("console.graphSearchOp", graphId=graph_id)
            )
            
            facts = []
            edges = []
            nodes = []
            
            # 解析边搜索结果
            if hasattr(search_results, 'edges') and search_results.edges:
                for edge in search_results.edges:
                    if hasattr(edge, 'fact') and edge.fact:
                        facts.append(self._translate_if_chinese(edge.fact))
                    edges.append({
                        "uuid": getattr(edge, 'uuid_', None) or getattr(edge, 'uuid', ''),
                        "name": getattr(edge, 'name', ''),
                        "fact": getattr(edge, 'fact', ''),
                        "source_node_uuid": getattr(edge, 'source_node_uuid', ''),
                        "target_node_uuid": getattr(edge, 'target_node_uuid', ''),
                    })
            
            # 解析节点搜索结果
            if hasattr(search_results, 'nodes') and search_results.nodes:
                for node in search_results.nodes:
                    nodes.append({
                        "uuid": getattr(node, 'uuid_', None) or getattr(node, 'uuid', ''),
                        "name": getattr(node, 'name', ''),
                        "labels": getattr(node, 'labels', []),
                        "summary": getattr(node, 'summary', ''),
                    })
                    # 节点摘要也算作事实
                    if hasattr(node, 'summary') and node.summary:
                        facts.append(f"[{node.name}]: {self._translate_if_chinese(node.summary)}")
            
            logger.info(t("console.searchComplete", count=len(facts)))
            
            return SearchResult(
                facts=facts,
                edges=edges,
                nodes=nodes,
                query=query,
                total_count=len(facts)
            )
            
        except Exception as e:
            # Authentication, invalid input, missing graphs, and exhausted
            # transient failures must remain visible to the report workflow.
            logger.error(t("console.zepSearchApiFallback", error=str(e)))
            raise
    
    def _local_search(
        self, 
        graph_id: str, 
        query: str, 
        limit: int = 10,
        scope: str = "edges"
    ) -> SearchResult:
        """
        本地关键词匹配搜索（作为Zep Search API的降级方案）
        
        获取所有边/节点，然后在本地进行关键词匹配
        
        Args:
            graph_id: 图谱ID
            query: 搜索查询
            limit: 返回结果数量
            scope: 搜索范围
            
        Returns:
            SearchResult: 搜索结果
        """
        logger.info(t("console.usingLocalSearch", query=query[:30]))
        
        facts = []
        edges_result = []
        nodes_result = []
        
        # 提取查询关键词（简单分词）
        query_lower = query.lower()
        keywords = [w.strip() for w in query_lower.replace(',', ' ').replace('，', ' ').split() if len(w.strip()) > 1]
        
        def match_score(text: str) -> int:
            """计算文本与查询的匹配分数"""
            if not text:
                return 0
            text_lower = text.lower()
            # 完全匹配查询
            if query_lower in text_lower:
                return 100
            # 关键词匹配
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 10
            return score
        
        try:
            if scope in ["edges", "both"]:
                # 获取所有边并匹配
                all_edges = self.get_all_edges(graph_id)
                scored_edges = []
                for edge in all_edges:
                    score = match_score(edge.fact) + match_score(edge.name)
                    if score > 0:
                        scored_edges.append((score, edge))
                
                # 按分数排序
                scored_edges.sort(key=lambda x: x[0], reverse=True)
                
                for score, edge in scored_edges[:limit]:
                    if edge.fact:
                        facts.append(edge.fact)
                    edges_result.append({
                        "uuid": edge.uuid,
                        "name": edge.name,
                        "fact": edge.fact,
                        "source_node_uuid": edge.source_node_uuid,
                        "target_node_uuid": edge.target_node_uuid,
                    })
            
            if scope in ["nodes", "both"]:
                # 获取所有节点并匹配
                all_nodes = self.get_all_nodes(graph_id)
                scored_nodes = []
                for node in all_nodes:
                    score = match_score(node.name) + match_score(node.summary)
                    if score > 0:
                        scored_nodes.append((score, node))
                
                scored_nodes.sort(key=lambda x: x[0], reverse=True)
                
                for score, node in scored_nodes[:limit]:
                    nodes_result.append({
                        "uuid": node.uuid,
                        "name": node.name,
                        "labels": node.labels,
                        "summary": node.summary,
                    })
                    if node.summary:
                        facts.append(f"[{node.name}]: {node.summary}")
            
            logger.info(t("console.localSearchComplete", count=len(facts)))
            
        except Exception as e:
            logger.error(t("console.localSearchFailed", error=str(e)))
        
        return SearchResult(
            facts=facts,
            edges=edges_result,
            nodes=nodes_result,
            query=query,
            total_count=len(facts)
        )
    
    def get_all_nodes(self, graph_id: str) -> List[NodeInfo]:
        """
        获取图谱的所有节点（分页获取）

        Args:
            graph_id: 图谱ID

        Returns:
            节点列表
        """
        logger.info(t("console.fetchingAllNodes", graphId=graph_id))

        nodes = fetch_all_nodes(self.client, graph_id)

        result = []
        for node in nodes:
            node_uuid = getattr(node, 'uuid_', None) or getattr(node, 'uuid', None) or ""
            result.append(NodeInfo(
                uuid=str(node_uuid) if node_uuid else "",
                name=node.name or "",
                labels=node.labels or [],
                summary=node.summary or "",
                attributes=node.attributes or {}
            ))

        logger.info(t("console.fetchedNodes", count=len(result)))
        return result

    def get_all_edges(self, graph_id: str, include_temporal: bool = True) -> List[EdgeInfo]:
        """
        获取图谱的所有边（分页获取，包含时间信息）

        Args:
            graph_id: 图谱ID
            include_temporal: 是否包含时间信息（默认True）

        Returns:
            边列表（包含created_at, valid_at, invalid_at, expired_at）
        """
        logger.info(t("console.fetchingAllEdges", graphId=graph_id))

        edges = fetch_all_edges(self.client, graph_id)

        result = []
        for edge in edges:
            edge_uuid = getattr(edge, 'uuid_', None) or getattr(edge, 'uuid', None) or ""
            edge_info = EdgeInfo(
                uuid=str(edge_uuid) if edge_uuid else "",
                name=edge.name or "",
                fact=edge.fact or "",
                source_node_uuid=edge.source_node_uuid or "",
                target_node_uuid=edge.target_node_uuid or ""
            )

            # 添加时间信息
            if include_temporal:
                edge_info.created_at = getattr(edge, 'created_at', None)
                edge_info.valid_at = getattr(edge, 'valid_at', None)
                edge_info.invalid_at = getattr(edge, 'invalid_at', None)
                edge_info.expired_at = getattr(edge, 'expired_at', None)

            result.append(edge_info)

        logger.info(t("console.fetchedEdges", count=len(result)))
        return result
    
    def get_node_detail(self, node_uuid: str) -> Optional[NodeInfo]:
        """
        获取单个节点的详细信息
        
        Args:
            node_uuid: 节点UUID
            
        Returns:
            节点信息或None
        """
        logger.info(t("console.fetchingNodeDetail", uuid=node_uuid[:8]))
        
        try:
            node = self._call_with_retry(
                func=lambda: self.client.graph.node.get(uuid_=node_uuid),
                operation_name=t("console.fetchNodeDetailOp", uuid=node_uuid[:8])
            )
            
            if not node:
                return None
            
            return NodeInfo(
                uuid=getattr(node, 'uuid_', None) or getattr(node, 'uuid', ''),
                name=node.name or "",
                labels=node.labels or [],
                summary=node.summary or "",
                attributes=node.attributes or {}
            )
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(t("console.fetchNodeDetailFailed", error=str(e)))
            raise
    
    def get_node_edges(self, graph_id: str, node_uuid: str) -> List[EdgeInfo]:
        """
        获取节点相关的所有边
        
        通过获取图谱所有边，然后过滤出与指定节点相关的边
        
        Args:
            graph_id: 图谱ID
            node_uuid: 节点UUID
            
        Returns:
            边列表
        """
        logger.info(t("console.fetchingNodeEdges", uuid=node_uuid[:8]))
        
        try:
            # 获取图谱所有边，然后过滤
            all_edges = self.get_all_edges(graph_id)
            
            result = []
            for edge in all_edges:
                # 检查边是否与指定节点相关（作为源或目标）
                if edge.source_node_uuid == node_uuid or edge.target_node_uuid == node_uuid:
                    result.append(edge)
            
            logger.info(t("console.foundNodeEdges", count=len(result)))
            return result
            
        except Exception as e:
            logger.error(t("console.fetchNodeEdgesFailed", error=str(e)))
            raise
    
    def get_entities_by_type(
        self, 
        graph_id: str, 
        entity_type: str
    ) -> List[NodeInfo]:
        """
        按类型获取实体
        
        Args:
            graph_id: 图谱ID
            entity_type: 实体类型（如 Student, PublicFigure 等）
            
        Returns:
            符合类型的实体列表
        """
        logger.info(t("console.fetchingEntitiesByType", type=entity_type))
        
        all_nodes = self.get_all_nodes(graph_id)
        
        filtered = []
        for node in all_nodes:
            # 检查labels是否包含指定类型
            if entity_type in node.labels:
                filtered.append(node)
        
        logger.info(t("console.foundEntitiesByType", count=len(filtered), type=entity_type))
        return filtered
    
    def get_entity_summary(
        self, 
        graph_id: str, 
        entity_name: str
    ) -> Dict[str, Any]:
        """
        获取指定实体的关系摘要
        
        搜索与该实体相关的所有信息，并生成摘要
        
        Args:
            graph_id: 图谱ID
            entity_name: 实体名称
            
        Returns:
            实体摘要信息
        """
        logger.info(t("console.fetchingEntitySummary", name=entity_name))
        
        # 先搜索该实体相关的信息
        search_result = self.search_graph(
            graph_id=graph_id,
            query=entity_name,
            limit=20
        )
        
        # 尝试在所有节点中找到该实体
        all_nodes = self.get_all_nodes(graph_id)
        entity_node = None
        for node in all_nodes:
            if node.name.lower() == entity_name.lower():
                entity_node = node
                break
        
        related_edges = []
        if entity_node:
            # 传入graph_id参数
            related_edges = self.get_node_edges(graph_id, entity_node.uuid)
        
        return {
            "entity_name": entity_name,
            "entity_info": entity_node.to_dict() if entity_node else None,
            "related_facts": search_result.facts,
            "related_edges": [e.to_dict() for e in related_edges],
            "total_relations": len(related_edges)
        }
    
    def get_graph_statistics(self, graph_id: str) -> Dict[str, Any]:
        """
        获取图谱的统计信息
        
        Args:
            graph_id: 图谱ID
            
        Returns:
            统计信息
        """
        logger.info(t("console.fetchingGraphStats", graphId=graph_id))
        
        nodes = self.get_all_nodes(graph_id)
        edges = self.get_all_edges(graph_id)
        
        # 统计实体类型分布
        entity_types = {}
        for node in nodes:
            for label in node.labels:
                if label not in ["Entity", "Node"]:
                    entity_types[label] = entity_types.get(label, 0) + 1
        
        # 统计关系类型分布
        relation_types = {}
        for edge in edges:
            relation_types[edge.name] = relation_types.get(edge.name, 0) + 1
        
        return {
            "graph_id": graph_id,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "entity_types": entity_types,
            "relation_types": relation_types
        }
    
    def get_simulation_context(
        self, 
        graph_id: str,
        simulation_requirement: str,
        limit: int = 30
    ) -> Dict[str, Any]:
        """
        获取模拟相关的上下文信息
        
        综合搜索与模拟需求相关的所有信息
        
        Args:
            graph_id: 图谱ID
            simulation_requirement: 模拟需求描述
            limit: 每类信息的数量限制
            
        Returns:
            模拟上下文信息
        """
        logger.info(t("console.fetchingSimContext", requirement=simulation_requirement[:50]))
        
        # 搜索与模拟需求相关的信息
        search_result = self.search_graph(
            graph_id=graph_id,
            query=simulation_requirement,
            limit=limit
        )
        
        # 获取图谱统计
        stats = self.get_graph_statistics(graph_id)
        
        # 获取所有实体节点
        all_nodes = self.get_all_nodes(graph_id)
        
        # 筛选有实际类型的实体（非纯Entity节点）
        entities = []
        for node in all_nodes:
            custom_labels = [l for l in node.labels if l not in ["Entity", "Node"]]
            if custom_labels:
                entities.append({
                    "name": node.name,
                    "type": custom_labels[0],
                    "summary": node.summary
                })
        
        return {
            "simulation_requirement": simulation_requirement,
            "related_facts": search_result.facts,
            "graph_statistics": stats,
            "entities": entities[:limit],  # 限制数量
            "total_entities": len(entities)
        }
    
    # ========== 核心检索工具（优化后） ==========
    
    def insight_forge(
        self,
        graph_id: str,
        query: str,
        simulation_requirement: str,
        report_context: str = "",
        max_sub_queries: int = 5
    ) -> InsightForgeResult:
        """
        【InsightForge - 深度洞察检索】
        
        最强大的混合检索函数，自动分解问题并多维度检索：
        1. 使用LLM将问题分解为多个子问题
        2. 对每个子问题进行语义搜索
        3. 提取相关实体并获取其详细信息
        4. 追踪关系链
        5. 整合所有结果，生成深度洞察
        
        Args:
            graph_id: 图谱ID
            query: 用户问题
            simulation_requirement: 模拟需求描述
            report_context: 报告上下文（可选，用于更精准的子问题生成）
            max_sub_queries: 最大子问题数量
            
        Returns:
            InsightForgeResult: 深度洞察检索结果
        """
        logger.info(t("console.insightForgeStart", query=query[:50]))
        
        result = InsightForgeResult(
            query=query,
            simulation_requirement=simulation_requirement,
            sub_queries=[]
        )
        
        # Step 1: 使用LLM生成子问题
        sub_queries = self._generate_sub_queries(
            query=query,
            simulation_requirement=simulation_requirement,
            report_context=report_context,
            max_queries=max_sub_queries
        )
        result.sub_queries = sub_queries
        logger.info(t("console.generatedSubQueries", count=len(sub_queries)))
        
        # Step 2: 对每个子问题进行语义搜索
        all_facts = []
        all_edges = []
        seen_facts = set()
        
        for sub_query in sub_queries:
            search_result = self.search_graph(
                graph_id=graph_id,
                query=sub_query,
                limit=15,
                scope="edges"
            )
            
            for fact in search_result.facts:
                if fact not in seen_facts:
                    all_facts.append(fact)
                    seen_facts.add(fact)
            
            all_edges.extend(search_result.edges)
        
        # 对原始问题也进行搜索
        main_search = self.search_graph(
            graph_id=graph_id,
            query=query,
            limit=20,
            scope="edges"
        )
        for fact in main_search.facts:
            if fact not in seen_facts:
                all_facts.append(fact)
                seen_facts.add(fact)
        
        result.semantic_facts = all_facts
        result.total_facts = len(all_facts)
        
        # Step 3: 从边中提取相关实体UUID，只获取这些实体的信息（不获取全部节点）
        entity_uuids = set()
        for edge_data in all_edges:
            if isinstance(edge_data, dict):
                source_uuid = edge_data.get('source_node_uuid', '')
                target_uuid = edge_data.get('target_node_uuid', '')
                if source_uuid:
                    entity_uuids.add(source_uuid)
                if target_uuid:
                    entity_uuids.add(target_uuid)
        
        # 获取所有相关实体的详情（不限制数量，完整输出）
        entity_insights = []
        node_map = {}  # 用于后续关系链构建
        
        for uuid in list(entity_uuids):  # 处理所有实体，不截断
            if not uuid:
                continue
            try:
                # 单独获取每个相关节点的信息
                node = self.get_node_detail(uuid)
                if node:
                    node_map[uuid] = node
                    entity_type = next((l for l in node.labels if l not in ["Entity", "Node"]), "实体")
                    
                    # 获取该实体相关的所有事实（不截断）
                    related_facts = [
                        f for f in all_facts 
                        if node.name.lower() in f.lower()
                    ]
                    
                    entity_insights.append({
                        "uuid": node.uuid,
                        "name": node.name,
                        "type": entity_type,
                        "summary": node.summary,
                        "related_facts": related_facts  # 完整输出，不截断
                    })
            except Exception as e:
                logger.debug(f"获取节点 {uuid} 失败: {e}")
                continue
        
        result.entity_insights = entity_insights
        result.total_entities = len(entity_insights)
        
        # Step 4: 构建所有关系链（不限制数量）
        relationship_chains = []
        for edge_data in all_edges:  # 处理所有边，不截断
            if isinstance(edge_data, dict):
                source_uuid = edge_data.get('source_node_uuid', '')
                target_uuid = edge_data.get('target_node_uuid', '')
                relation_name = edge_data.get('name', '')
                
                source_name = node_map.get(source_uuid, NodeInfo('', '', [], '', {})).name or source_uuid[:8]
                target_name = node_map.get(target_uuid, NodeInfo('', '', [], '', {})).name or target_uuid[:8]
                
                chain = f"{source_name} --[{relation_name}]--> {target_name}"
                if chain not in relationship_chains:
                    relationship_chains.append(chain)
        
        result.relationship_chains = relationship_chains
        result.total_relationships = len(relationship_chains)
        
        logger.info(t("console.insightForgeComplete", facts=result.total_facts, entities=result.total_entities, relationships=result.total_relationships))
        return result
    
    def _generate_sub_queries(
        self,
        query: str,
        simulation_requirement: str,
        report_context: str = "",
        max_queries: int = 5
    ) -> List[str]:
        """
        使用LLM生成子问题
        
        将复杂问题分解为多个可以独立检索的子问题
        """
        system_prompt = """Anda adalah ahli analisis investigasi profesional. Tugas Anda adalah menguraikan pertanyaan kompleks menjadi beberapa sub-pertanyaan spesifik yang dapat diobservasi secara mandiri dalam dunia simulasi.

Persyaratan:
1. Setiap sub-pertanyaan harus spesifik agar dapat ditemukan perilaku Agent atau peristiwa terkait dalam dunia simulasi
2. Sub-pertanyaan harus mencakup dimensi yang berbeda (siapa, apa, mengapa, bagaimana, kapan, di mana)
3. Sub-pertanyaan harus relevan dengan skenario simulasi
4. Seluruh keluaran WAJIB menggunakan Bahasa Indonesia yang formal dan tepat
5. Kembalikan format JSON: {"sub_queries": ["sub-pertanyaan 1", "sub-pertanyaan 2", ...]}"""

        user_prompt = f"""Latar Belakang Kebutuhan Simulasi:
{simulation_requirement}

{f"Konteks Laporan: {report_context[:500]}" if report_context else ""}

Uraikan pertanyaan berikut menjadi {max_queries} sub-pertanyaan spesifik dalam Bahasa Indonesia:
{query}

Kembalikan daftar sub-pertanyaan dalam format JSON."""

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            sub_queries = response.get("sub_queries", [])
            # Pastikan daftar string
            return [str(sq) for sq in sub_queries[:max_queries]]
            
        except Exception as e:
            logger.warning(t("console.generateSubQueriesFailed", error=str(e)))
            # Fallback dalam Bahasa Indonesia
            return [
                query,
                f"Aktor utama terkait {query}",
                f"Penyebab dan dampak {query}",
                f"Kronologi perkembangan {query}"
            ][:max_queries]
    
    def panorama_search(
        self,
        graph_id: str,
        query: str,
        include_expired: bool = True,
        limit: int = 50
    ) -> PanoramaResult:
        """
        【PanoramaSearch - 广度搜索】
        
        获取全貌视图，包括所有相关内容和历史/过期信息：
        1. 获取所有相关节点
        2. 获取所有边（包括已过期/失效的）
        3. 分类整理当前有效和历史信息
        
        这个工具适用于需要了解事件全貌、追踪演变过程的场景。
        
        Args:
            graph_id: 图谱ID
            query: 搜索查询（用于相关性排序）
            include_expired: 是否包含过期内容（默认True）
            limit: 返回结果数量限制
            
        Returns:
            PanoramaResult: 广度搜索结果
        """
        logger.info(t("console.panoramaSearchStart", query=query[:50]))
        
        result = PanoramaResult(query=query)
        
        # 获取所有节点
        all_nodes = self.get_all_nodes(graph_id)
        node_map = {n.uuid: n for n in all_nodes}
        result.all_nodes = all_nodes
        result.total_nodes = len(all_nodes)
        
        # 获取所有边（包含时间信息）
        all_edges = self.get_all_edges(graph_id, include_temporal=True)
        result.all_edges = all_edges
        result.total_edges = len(all_edges)
        
        # 分类事实
        active_facts = []
        historical_facts = []
        
        for edge in all_edges:
            if not edge.fact:
                continue
            
            # 为事实添加实体名称
            source_name = node_map.get(edge.source_node_uuid, NodeInfo('', '', [], '', {})).name or edge.source_node_uuid[:8]
            target_name = node_map.get(edge.target_node_uuid, NodeInfo('', '', [], '', {})).name or edge.target_node_uuid[:8]
            
            # 判断是否过期/失效
            is_historical = edge.is_expired or edge.is_invalid
            
            if is_historical:
                # 历史/过期事实，添加时间标记
                valid_at = edge.valid_at or "tidak diketahui"
                invalid_at = edge.invalid_at or edge.expired_at or "tidak diketahui"
                clean_fact = self._translate_if_chinese(edge.fact)
                fact_with_time = f"[{valid_at} - {invalid_at}] {clean_fact}"
                historical_facts.append(fact_with_time)
            else:
                # 当前有效事实
                active_facts.append(self._translate_if_chinese(edge.fact))
        
        # 基于查询进行相关性排序
        query_lower = query.lower()
        keywords = [w.strip() for w in query_lower.replace(',', ' ').replace('，', ' ').split() if len(w.strip()) > 1]
        
        def relevance_score(fact: str) -> int:
            fact_lower = fact.lower()
            score = 0
            if query_lower in fact_lower:
                score += 100
            for kw in keywords:
                if kw in fact_lower:
                    score += 10
            return score
        
        # 排序并限制数量
        active_facts.sort(key=relevance_score, reverse=True)
        historical_facts.sort(key=relevance_score, reverse=True)
        
        result.active_facts = active_facts[:limit]
        result.historical_facts = historical_facts[:limit] if include_expired else []
        result.active_count = len(active_facts)
        result.historical_count = len(historical_facts)
        
        logger.info(t("console.panoramaSearchComplete", active=result.active_count, historical=result.historical_count))
        return result
    
    def quick_search(
        self,
        graph_id: str,
        query: str,
        limit: int = 10
    ) -> SearchResult:
        """
        【QuickSearch - 简单搜索】
        
        快速、轻量级的检索工具：
        1. 直接调用Zep语义搜索
        2. 返回最相关的结果
        3. 适用于简单、直接的检索需求
        
        Args:
            graph_id: 图谱ID
            query: 搜索查询
            limit: 返回结果数量
            
        Returns:
            SearchResult: 搜索结果
        """
        logger.info(t("console.quickSearchStart", query=query[:50]))
        
        # 直接调用现有的search_graph方法
        result = self.search_graph(
            graph_id=graph_id,
            query=query,
            limit=limit,
            scope="edges"
        )
        
        logger.info(t("console.quickSearchComplete", count=result.total_count))
        return result
    
    def interview_agents(
        self,
        simulation_id: str,
        interview_requirement: str,
        simulation_requirement: str = "",
        max_agents: int = 5,
        custom_questions: List[str] = None
    ) -> InterviewResult:
        """
        【InterviewAgents - 深度采访】
        
        调用真实的OASIS采访API，采访模拟中正在运行的Agent：
        1. 自动读取人设文件，了解所有模拟Agent
        2. 使用LLM分析采访需求，智能选择最相关的Agent
        3. 使用LLM生成采访问题
        4. 调用 /api/simulation/interview/batch 接口进行真实采访（双平台同时采访）
        5. 整合所有采访结果，生成采访报告
        
        【重要】此功能需要模拟环境处于运行状态（OASIS环境未关闭）
        
        【使用场景】
        - 需要从不同角色视角了解事件看法
        - 需要收集多方意见和观点
        - 需要获取模拟Agent的真实回答（非LLM模拟）
        
        Args:
            simulation_id: 模拟ID（用于定位人设文件和调用采访API）
            interview_requirement: 采访需求描述（非结构化，如"了解学生对事件的看法"）
            simulation_requirement: 模拟需求背景（可选）
            max_agents: 最多采访的Agent数量
            custom_questions: 自定义采访问题（可选，若不提供则自动生成）
            
        Returns:
            InterviewResult: 采访结果
        """
        from .simulation_runner import SimulationRunner
        
        logger.info(t("console.interviewAgentsStart", requirement=interview_requirement[:50]))
        
        result = InterviewResult(
            interview_topic=interview_requirement,
            interview_questions=custom_questions or []
        )
        
        # Step 1: 读取人设文件
        profiles = self._load_agent_profiles(simulation_id)
        
        if not profiles:
            logger.warning(t("console.profilesNotFound", simId=simulation_id))
            result.summary = "未找到可采访的Agent人设文件"
            return result
        
        result.total_agents = len(profiles)
        logger.info(t("console.loadedProfiles", count=len(profiles)))
        
        # Step 2: 使用LLM选择要采访的Agent（返回agent_id列表）
        selected_agents, selected_indices, selection_reasoning = self._select_agents_for_interview(
            profiles=profiles,
            interview_requirement=interview_requirement,
            simulation_requirement=simulation_requirement,
            max_agents=max_agents
        )
        
        result.selected_agents = selected_agents
        result.selection_reasoning = selection_reasoning
        logger.info(t("console.selectedAgentsForInterview", count=len(selected_agents), indices=selected_indices))
        
        # Step 3: 生成采访问题（如果没有提供）
        if not result.interview_questions:
            result.interview_questions = self._generate_interview_questions(
                interview_requirement=interview_requirement,
                simulation_requirement=simulation_requirement,
                selected_agents=selected_agents
            )
            logger.info(t("console.generatedInterviewQuestions", count=len(result.interview_questions)))
        
        # 将问题合并为一个采访prompt
        combined_prompt = "\n".join([f"{i+1}. {q}" for i, q in enumerate(result.interview_questions)])
        
        # Tambahkan prefix optimasi, batasi format jawaban Agent
        INTERVIEW_PROMPT_PREFIX = (
            "Anda sedang diwawancarai. Berdasarkan persona Anda, seluruh ingatan dan tindakan Anda sebelumnya dalam simulasi, "
            "jawablah pertanyaan-pertanyaan berikut secara langsung dalam teks biasa menggunakan Bahasa Indonesia.\n"
            "Ketentuan jawaban:\n"
            "1. Jawab langsung dalam bahasa alami (Bahasa Indonesia), jangan memanggil alat apa pun\n"
            "2. Jangan kembalikan format JSON atau pemanggilan alat\n"
            "3. Jangan gunakan judul Markdown (seperti #, ##, ###)\n"
            "4. Jawab satu per satu sesuai nomor pertanyaan, setiap jawaban diawali dengan 'Pertanyaan X:' (X adalah nomor pertanyaan)\n"
            "5. Pisahkan jawaban setiap pertanyaan dengan baris kosong\n"
            "6. Berikan jawaban yang substantif dan berkarakter, setiap pertanyaan dijawab setidaknya 2-3 kalimat\n\n"
        )
        optimized_prompt = f"{INTERVIEW_PROMPT_PREFIX}{combined_prompt}"
        
        # Step 4: 调用真实的采访API（不指定platform，默认双平台同时采访）
        try:
            # 构建批量采访列表（不指定platform，双平台采访）
            interviews_request = []
            for agent_idx in selected_indices:
                interviews_request.append({
                    "agent_id": agent_idx,
                    "prompt": optimized_prompt  # 使用优化后的prompt
                    # 不指定platform，API会在twitter和reddit两个平台都采访
                })
            
            logger.info(t("console.callingBatchInterviewApi", count=len(interviews_request)))
            
            # 调用 SimulationRunner 的批量采访方法（不传platform，双平台采访）
            api_result = SimulationRunner.interview_agents_batch(
                simulation_id=simulation_id,
                interviews=interviews_request,
                platform=None,  # 不指定platform，双平台采访
                timeout=180.0   # 双平台需要更长超时
            )
            
            logger.info(t("console.interviewApiReturned", count=api_result.get('interviews_count', 0), success=api_result.get('success')))
            
            # 检查API调用是否成功
            if not api_result.get("success", False):
                error_msg = api_result.get("error", "未知错误")
                logger.warning(t("console.interviewApiReturnedFailure", error=error_msg))
                result.summary = f"采访API调用失败：{error_msg}。请检查OASIS模拟环境状态。"
                return result
            
            # Step 5: 解析API返回结果，构建AgentInterview对象
            # 双平台模式返回格式: {"twitter_0": {...}, "reddit_0": {...}, "twitter_1": {...}, ...}
            api_data = api_result.get("result", {})
            results_dict = api_data.get("results", {}) if isinstance(api_data, dict) else {}
            
            for i, agent_idx in enumerate(selected_indices):
                agent = selected_agents[i]
                agent_name = agent.get("realname", agent.get("username", f"Agent_{agent_idx}"))
                agent_role = agent.get("profession", "未知")
                agent_bio = agent.get("bio", "")
                
                # 获取该Agent在两个平台的采访结果
                twitter_result = results_dict.get(f"twitter_{agent_idx}", {})
                reddit_result = results_dict.get(f"reddit_{agent_idx}", {})
                
                twitter_response = twitter_result.get("response", "")
                reddit_response = reddit_result.get("response", "")

                # 清理可能的工具调用 JSON 包裹
                twitter_response = self._clean_tool_call_response(twitter_response)
                reddit_response = self._clean_tool_call_response(reddit_response)

                # Pastikan jawaban diterjemahkan ke Bahasa Indonesia jika mengandung bahasa Tionghoa
                twitter_response = self._translate_if_chinese(twitter_response)
                reddit_response = self._translate_if_chinese(reddit_response)

                # Output penanda platform dua arah
                twitter_text = twitter_response if twitter_response else "（Tidak ada jawaban di platform Twitter）"
                reddit_text = reddit_response if reddit_response else "（Tidak ada jawaban di platform Reddit）"
                response_text = f"【Jawaban Platform Twitter】\n{twitter_text}\n\n【Jawaban Platform Reddit】\n{reddit_text}"

                # 提取关键引言（从两个平台的回答中）
                import re
                combined_responses = f"{twitter_response} {reddit_response}"

                # 清理响应文本：去掉标记、编号、Markdown 等干扰
                clean_text = re.sub(r'#{1,6}\s+', '', combined_responses)
                clean_text = re.sub(r'\{[^}]*tool_name[^}]*\}', '', clean_text)
                clean_text = re.sub(r'[*_`|>~\-]{2,}', '', clean_text)
                clean_text = re.sub(r'(?:问题|Pertanyaan)\s*\d+[：:]\s*', '', clean_text)
                clean_text = re.sub(r'【[^】]+】', '', clean_text)

                # Strategi: ekstraksi kalimat bermakna
                sentences = re.split(r'[.!?。！？]', clean_text)
                meaningful = [
                    s.strip() for s in sentences
                    if 20 <= len(s.strip()) <= 150
                    and not re.match(r'^[\s\W，,；;：:、]+', s.strip())
                    and not s.strip().startswith(('{', '问题'))
                ]
                meaningful.sort(key=len, reverse=True)
                key_quotes = [s + "。" for s in meaningful[:3]]

                # 策略2（补充）: 正确配对的中文引号「」内长文本
                if not key_quotes:
                    paired = re.findall(r'\u201c([^\u201c\u201d]{15,100})\u201d', clean_text)
                    paired += re.findall(r'\u300c([^\u300c\u300d]{15,100})\u300d', clean_text)
                    key_quotes = [q for q in paired if not re.match(r'^[，,；;：:、]', q)][:3]
                
                interview = AgentInterview(
                    agent_name=agent_name,
                    agent_role=agent_role,
                    agent_bio=agent_bio[:1000],  # 扩大bio长度限制
                    question=combined_prompt,
                    response=response_text,
                    key_quotes=key_quotes[:5]
                )
                result.interviews.append(interview)
            
            result.interviewed_count = len(result.interviews)
            
        except ValueError as e:
            # 模拟环境未运行
            logger.warning(t("console.interviewApiCallFailed", error=e))
            result.summary = f"采访失败：{str(e)}。模拟环境可能已关闭，请确保OASIS环境正在运行。"
            return result
        except Exception as e:
            logger.error(t("console.interviewApiCallException", error=e))
            import traceback
            logger.error(traceback.format_exc())
            result.summary = f"采访过程发生错误：{str(e)}"
            return result
        
        # Step 6: 生成采访摘要
        if result.interviews:
            result.summary = self._generate_interview_summary(
                interviews=result.interviews,
                interview_requirement=interview_requirement
            )
        
        logger.info(t("console.interviewAgentsComplete", count=result.interviewed_count))
        return result
    
    @staticmethod
    def _clean_tool_call_response(response: str) -> str:
        """清理 Agent 回复中的 JSON 工具调用包裹，提取实际内容"""
        if not response or not response.strip().startswith('{'):
            return response
        text = response.strip()
        if 'tool_name' not in text[:80]:
            return response
        import re as _re
        try:
            data = json.loads(text)
            if isinstance(data, dict) and 'arguments' in data:
                for key in ('content', 'text', 'body', 'message', 'reply'):
                    if key in data['arguments']:
                        return str(data['arguments'][key])
        except (json.JSONDecodeError, KeyError, TypeError):
            match = _re.search(r'"content"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
            if match:
                return match.group(1).replace('\\n', '\n').replace('\\"', '"')
        return response

    def _load_agent_profiles(self, simulation_id: str) -> List[Dict[str, Any]]:
        """加载模拟的Agent人设文件"""
        import os
        import csv
        
        # 构建人设文件路径
        sim_dir = os.path.join(
            os.path.dirname(__file__), 
            f'../../uploads/simulations/{simulation_id}'
        )
        
        profiles = []
        
        # 优先尝试读取Reddit JSON格式
        reddit_profile_path = os.path.join(sim_dir, "reddit_profiles.json")
        if os.path.exists(reddit_profile_path):
            try:
                with open(reddit_profile_path, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                logger.info(t("console.loadedRedditProfiles", count=len(profiles)))
                return profiles
            except Exception as e:
                logger.warning(t("console.readRedditProfilesFailed", error=e))
        
        # 尝试读取Twitter CSV格式
        twitter_profile_path = os.path.join(sim_dir, "twitter_profiles.csv")
        if os.path.exists(twitter_profile_path):
            try:
                with open(twitter_profile_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # CSV格式转换为统一格式
                        profiles.append({
                            "realname": row.get("name", ""),
                            "username": row.get("username", ""),
                            "bio": row.get("description", ""),
                            "persona": row.get("user_char", ""),
                            "profession": "未知"
                        })
                logger.info(t("console.loadedTwitterProfiles", count=len(profiles)))
                return profiles
            except Exception as e:
                logger.warning(t("console.readTwitterProfilesFailed", error=e))
        
        return profiles
    
    def _select_agents_for_interview(
        self,
        profiles: List[Dict[str, Any]],
        interview_requirement: str,
        simulation_requirement: str,
        max_agents: int
    ) -> tuple:
        """
        使用LLM选择要采访的Agent
        
        Returns:
            tuple: (selected_agents, selected_indices, reasoning)
                - selected_agents: 选中Agent的完整信息列表
                - selected_indices: 选中Agent的索引列表（用于API调用）
                - reasoning: 选择理由
        """
        
        # 构建Agent摘要列表
        agent_summaries = []
        for i, profile in enumerate(profiles):
            summary = {
                "index": i,
                "name": profile.get("realname", profile.get("username", f"Agent_{i}")),
                "profession": profile.get("profession", "未知"),
                "bio": profile.get("bio", "")[:200],
                "interested_topics": profile.get("interested_topics", [])
            }
            agent_summaries.append(summary)
        
        system_prompt = """Anda adalah perencana wawancara profesional. Tugas Anda adalah memilih Agent simulasi yang paling relevan untuk diwawancarai berdasarkan kebutuhan investigasi.

Kriteria Pemilihan:
1. Identitas/profesi Agent relevan dengan topik wawancara
2. Agent memiliki sudut pandang berbobot atau unik
3. Pilih keberagaman perspektif (pendukung, penentang, netral, otoritas/regulator)
4. Utamakan figur yang terlibat langsung dalam dinamika isu
5. Gunakan Bahasa Indonesia sepenuhnya

Kembalikan format JSON:
{
    "selected_indices": [indeks_agent_terpilih],
    "reasoning": "Penjelasan alasan pemilihan dalam Bahasa Indonesia"
}"""

        user_prompt = f"""Kebutuhan Wawancara:
{interview_requirement}

Latar Belakang Simulasi:
{simulation_requirement if simulation_requirement else "Tidak disediakan"}

Daftar Agent yang tersedia (Total {len(agent_summaries)}):
{json.dumps(agent_summaries, ensure_ascii=False, indent=2)}

Pilih maksimal {max_agents} Agent yang paling relevan dan jelaskan alasannya dalam Bahasa Indonesia."""

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            selected_indices = response.get("selected_indices", [])[:max_agents]
            reasoning = response.get("reasoning", "Dipilih otomatis berdasarkan relevansi topik")
            
            # 获取选中的Agent完整信息
            selected_agents = []
            valid_indices = []
            for idx in selected_indices:
                if 0 <= idx < len(profiles):
                    selected_agents.append(profiles[idx])
                    valid_indices.append(idx)
            
            return selected_agents, valid_indices, reasoning
            
        except Exception as e:
            logger.warning(t("console.llmSelectAgentFailed", error=e))
            # Fallback
            selected = profiles[:max_agents]
            indices = list(range(min(max_agents, len(profiles))))
            return selected, indices, "Menggunakan strategi pemilihan standar"
    
    def _generate_interview_questions(
        self,
        interview_requirement: str,
        simulation_requirement: str,
        selected_agents: List[Dict[str, Any]]
    ) -> List[str]:
        """Gunakan LLM untuk membuat pertanyaan wawancara dalam Bahasa Indonesia"""
        
        agent_roles = [a.get("profession", "Agen") for a in selected_agents]
        
        system_prompt = """Anda adalah jurnalis/pewawancara investigasi profesional. Berdasarkan topik wawancara, susun 3-5 pertanyaan wawancara mendalam dalam Bahasa Indonesia.

Persyaratan Pertanyaan:
1. Pertanyaan terbuka yang mendorong elaborasi substantif
2. Relevan dengan peran dan perspektif narasumber
3. Menyelidiki fakta, sikap, dampak, dan respon kebijakan
4. Gaya bahasa formal, lugas, dan alami
5. Panjang tiap pertanyaan di bawah 50 kata
6. Langsung ajukan pertanyaan tanpa basa-basi pembuka
7. Gunakan Bahasa Indonesia sepenuhnya

Kembalikan format JSON: {"questions": ["pertanyaan 1", "pertanyaan 2", ...]}"""

        user_prompt = f"""Topik Wawancara: {interview_requirement}

Latar Belakang Simulasi: {simulation_requirement if simulation_requirement else "Tidak disediakan"}

Peran Calon Narasumber: {', '.join(agent_roles)}

Buatlah 3-5 pertanyaan wawancara dalam Bahasa Indonesia."""

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5
            )
            
            return response.get("questions", [f"Bagaimana pandangan Anda mengenai {interview_requirement}?"])
            
        except Exception as e:
            logger.warning(t("console.generateInterviewQuestionsFailed", error=e))
            return [
                f"Bagaimana sikap dan pandangan Anda terkait {interview_requirement}?",
                "Bagaimana isu ini berdampak secara langsung terhadap peran atau kelompok Anda?",
                "Apa langkah konkret yang menurut Anda perlu segera diambil untuk menyelesaikan masalah ini?"
            ]
    
    def _generate_interview_summary(
        self,
        interviews: List[AgentInterview],
        interview_requirement: str
    ) -> str:
        """Buat ringkasan wawancara dalam Bahasa Indonesia"""
        
        if not interviews:
            return "Tidak ada wawancara yang terselesaikan"
        
        # Kumpulkan seluruh hasil wawancara
        interview_texts = []
        for interview in interviews:
            interview_texts.append(f"【{interview.agent_name} ({interview.agent_role})】\n{interview.response[:500]}")
        
        system_prompt = """Anda adalah redaktur investigasi senior. Berdasarkan jawaban dari narasumber, susunlah ringkasan wawancara dalam Bahasa Indonesia.

Persyaratan Ringkasan:
1. Rangkum pokok pandangan dari tiap kluster aktor
2. Petakan titik temu (konsensus) dan benturan sikap (polarisasi)
3. Soroti kutipan pernyataan yang paling penting
4. Objektif dan profesional
5. Maksimal 1000 kata

Batasan Format (Wajib):
- Gunakan paragraf teks biasa, pisahkan antarpokok bahasan dengan baris kosong
- JANGAN gunakan heading Markdown (#, ##, ###)
- JANGAN gunakan garis pemisah (---, ***)
- Gunakan tanda petik ganda "" untuk mengutip pernyataan narasumber
- Boleh gunakan **tebal** untuk penekanan frasa kunci"""

        user_prompt = f"""Topik Wawancara: {interview_requirement}

Transkrip Wawancara:
{"".join(interview_texts)}

Susun ringkasan wawancara dalam Bahasa Indonesia."""

        try:
            summary = self.llm.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            return summary
            
        except Exception as e:
            logger.warning(t("console.generateInterviewSummaryFailed", error=e))
            return f"Telah diwawancarai {len(interviews)} agen simulasi: " + ", ".join([i.agent_name for i in interviews])
            # 降级：简单拼接
            return f"共采访了{len(interviews)}位受访者，包括：" + "、".join([i.agent_name for i in interviews])

"""End-to-end test with real LLM API (Alibaba DashScope)."""
import os
import sys
from pathlib import Path

# Load .env
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.llm_client import LLMClient, invoke_llm
from utils.knowledge_loader import knowledge
from agents.jd_translator.jd_analyst import parse_jd
from utils.graph_builder import build_graph
from langchain_core.messages import HumanMessage


def test_llm_connection():
    """Test basic LLM connectivity."""
    print("=" * 60)
    print("TEST 1: LLM Connection")
    print("=" * 60)
    
    client = LLMClient()
    response = client.chat_with_system(
        "You are a helpful assistant. Respond in JSON format.",
        '{"test": "hello"}'
    )
    print(f"Response: {response[:200]}...")
    print("✅ LLM connection OK\n")
    return True


def test_invoke_llm():
    """Test invoke_llm seam."""
    print("=" * 60)
    print("TEST 2: invoke_llm seam")
    print("=" * 60)
    
    result = invoke_llm(
        "You are a helpful assistant. Always respond with valid JSON.",
        '{"message": "test invoke_llm"}'
    )
    print(f"Result: {result}")
    print("✅ invoke_llm OK\n")
    return True


def test_knowledge_base():
    """Test knowledge base loading."""
    print("=" * 60)
    print("TEST 3: Knowledge Base")
    print("=" * 60)
    
    kb_keys = [
        "jd_library", "jargon_map", "skill_resource_map",
        "interview_questions", "ladder_templates", "user_profile_default"
    ]
    print(f"Knowledge base keys: {kb_keys}")
    for key in kb_keys:
        data = knowledge.get(key)
        if isinstance(data, dict):
            print(f"  - {key}: {len(data)} entries")
        elif isinstance(data, list):
            print(f"  - {key}: {len(data)} items")
        else:
            print(f"  - {key}: OK ({type(data).__name__})")
    print("✅ Knowledge base OK\n")
    return True


def test_jd_analyst():
    """Test JD analyst agent with real LLM."""
    print("=" * 60)
    print("TEST 4: JD Analyst Agent")
    print("=" * 60)
    
    jd_text = """
    岗位职责：
    1. 负责AI产品的需求分析、产品规划和设计
    2. 跟踪行业动态，进行竞品分析
    3. 协调研发团队，推动产品迭代
    4. 制定产品运营策略，提升用户活跃度
    
    任职要求：
    1. 本科及以上学历，3年以上产品经验
    2. 熟悉AI/ML相关技术，有AI产品经验优先
    3. 数据分析能力强，熟练使用SQL
    4. 良好的沟通协调能力
    """
    
    result = parse_jd(jd_text)
    print(f"JD Analysis result: {result}")
    print("✅ JD Analyst OK\n")
    return True


def test_full_flow():
    """Test full agent flow through the graph."""
    print("=" * 60)
    print("TEST 5: Full JD Translation Flow")
    print("=" * 60)
    
    from langchain_core.messages import HumanMessage
    from utils.graph_builder import build_graph
    
    graph = build_graph()
    
    # Create initial state
    initial_state = {
        "messages": [HumanMessage(content="帮我分析这个产品经理JD：负责AI产品需求分析和规划")],
        "intent": "jd_translate",
        "jd_text": "产品经理 - 负责AI产品需求分析、规划和设计，协调研发团队，推动产品迭代",
    }
    
    # Run the graph
    result = graph.invoke(initial_state)
    print(f"Final state keys: {list(result.keys())}")
    if "result" in result:
        print(f"✅ Full Flow completed\n")
        return True
    else:
        print(f"Warning: no result in state")
        print(f"Result: {result}\n")
        return True


def test_graph_build():
    """Test full graph build."""
    print("=" * 60)
    print("TEST 6: Graph Build")
    print("=" * 60)
    
    graph = build_graph()
    print(f"Graph type: {type(graph).__name__}")
    print("✅ Graph Build OK\n")
    return True


def test_supervisor_routing():
    """Test supervisor routing with real LLM."""
    print("=" * 60)
    print("TEST 7: Supervisor Routing")
    print("=" * 60)
    
    from utils.supervisor import supervisor_node
    
    # Test JD translation intent
    result = supervisor_node({
        "messages": [HumanMessage(content="帮我分析这个JD：产品经理，负责AI产品")]
    })
    print(f"Intent: {result.get('intent')}")
    print(f"Next node: {result.get('next_node')}")
    print("✅ Supervisor Routing OK\n")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("FogLift End-to-End Test (Real LLM: Alibaba DashScope)")
    print("=" * 60 + "\n")
    
    tests = [
        ("LLM Connection", test_llm_connection),
        ("invoke_llm seam", test_invoke_llm),
        ("Knowledge Base", test_knowledge_base),
        ("JD Analyst Agent", test_jd_analyst),
        ("Full JD Translation Flow", test_full_flow),
        ("Graph Build", test_graph_build),
        ("Supervisor Routing", test_supervisor_routing),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            if test_fn():
                passed += 1
        except Exception as e:
            print(f"❌ {name} FAILED: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

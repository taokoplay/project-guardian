#!/usr/bin/env python3
"""
Project Guardian - Intelligent Trigger Detector

Detects when to activate Project Guardian based on:
- Multi-language trigger words (Chinese and English)
- Context awareness (current file, conversation history)
- Intent classification (query, record, update, analyze)
- Confidence scoring
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class TriggerDetector:
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path).resolve() if project_path else None
        self.kb_path = self.project_path / ".project-ai" if self.project_path else None

        # Multi-language trigger patterns
        self.trigger_patterns = {
            # Query intents
            "query": {
                "en": [
                    r"\b(find|search|look\s+for|show|list|get)\b.*\b(bug|issue|error|problem|requirement|decision|adr)\b",
                    r"\b(what|which|where|when|how)\b.*\b(bug|issue|error|requirement|decision)\b",
                    r"\b(similar|related|duplicate)\b.*\b(bug|issue|problem)\b",
                    r"\b(check|verify|validate)\b.*\b(knowledge\s+base|project\s+guardian)\b",
                ],
                "zh": [
                    r"(查找|搜索|寻找|显示|列出|获取).*(bug|问题|错误|需求|决策|架构)",
                    r"(什么|哪个|哪里|什么时候|如何).*(bug|问题|错误|需求|决策)",
                    r"(相似|相关|重复).*(bug|问题|错误)",
                    r"(检查|验证|确认).*(知识库|项目守护)",
                ]
            },

            # Record intents
            "record": {
                "en": [
                    r"\b(record|add|create|log|save|document)\b.*\b(bug|issue|error|problem|requirement|decision|adr)\b",
                    r"\b(new|found|discovered)\b.*\b(bug|issue|error|problem)\b",
                    r"\b(track|register|note)\b.*\b(requirement|decision|bug)\b",
                ],
                "zh": [
                    r"(记录|添加|创建|保存|文档化).*(bug|问题|错误|需求|决策|架构)",
                    r"(新|发现|遇到).*(bug|问题|错误)",
                    r"(跟踪|注册|记下).*(需求|决策|bug)",
                ]
            },

            # Update intents
            "update": {
                "en": [
                    r"\b(update|modify|change|edit|fix)\b.*\b(bug|requirement|decision|knowledge\s+base)\b",
                    r"\b(mark|set)\b.*\b(resolved|fixed|completed|closed)\b",
                    r"\b(incremental|refresh|sync)\b.*\b(update|scan)\b",
                ],
                "zh": [
                    r"(更新|修改|改变|编辑|修复).*(bug|需求|决策|知识库)",
                    r"(标记|设置).*(已解决|已修复|已完成|已关闭)",
                    r"(增量|刷新|同步).*(更新|扫描)",
                ]
            },

            # Analyze intents
            "analyze": {
                "en": [
                    r"\b(analyze|check|review|inspect|examine)\b.*\b(health|quality|pattern|usage)\b",
                    r"\b(show|display|view)\b.*\b(stats|statistics|metrics|report)\b",
                    r"\b(knowledge\s+gap|frequent\s+question|popular\s+module)\b",
                ],
                "zh": [
                    r"(分析|检查|审查|检验|检测).*(健康|质量|模式|使用)",
                    r"(显示|展示|查看).*(统计|指标|报告)",
                    r"(知识缺口|常见问题|热门模块)",
                ]
            },

            # Initialize intents
            "initialize": {
                "en": [
                    r"\b(initialize|init|setup|scan|create)\b.*\b(project|knowledge\s+base|guardian)\b",
                    r"\b(start|begin)\b.*\b(tracking|monitoring)\b",
                ],
                "zh": [
                    r"(初始化|初始|设置|扫描|创建).*(项目|知识库|守护)",
                    r"(开始|启动).*(跟踪|监控)",
                ]
            }
        }

        # Context keywords that boost confidence
        self.context_keywords = {
            "bug": ["bug", "issue", "error", "problem", "crash", "fail", "exception", "问题", "错误", "崩溃", "失败", "异常"],
            "requirement": ["requirement", "feature", "spec", "story", "需求", "功能", "规格", "用户故事"],
            "decision": ["decision", "adr", "architecture", "design", "choice", "决策", "架构", "设计", "选择"],
            "project": ["project", "codebase", "repository", "repo", "项目", "代码库", "仓库"],
        }

        # File context patterns
        self.file_patterns = {
            "bug_related": [r".*bug.*", r".*issue.*", r".*error.*", r".*fix.*"],
            "feature_related": [r".*feature.*", r".*requirement.*", r".*spec.*"],
            "architecture_related": [r".*architecture.*", r".*design.*", r".*adr.*"],
        }

    def detect(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Detect if Project Guardian should be triggered

        Returns:
            {
                "should_trigger": bool,
                "confidence": float (0-1),
                "intent": str,
                "matched_patterns": List[str],
                "suggestions": List[str]
            }
        """
        text_lower = text.lower()

        # Check all intent patterns
        intent_scores = {}
        matched_patterns = []

        for intent, languages in self.trigger_patterns.items():
            score = 0
            for lang, patterns in languages.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        score += 1
                        matched_patterns.append(f"{intent}:{lang}:{pattern[:30]}...")

            intent_scores[intent] = score

        # Get top intent
        if not intent_scores or max(intent_scores.values()) == 0:
            return {
                "should_trigger": False,
                "confidence": 0.0,
                "intent": None,
                "matched_patterns": [],
                "suggestions": []
            }

        top_intent = max(intent_scores, key=intent_scores.get)
        base_confidence = min(intent_scores[top_intent] * 0.3, 1.0)

        # Boost confidence with context
        context_boost = self._calculate_context_boost(text_lower, context)
        final_confidence = min(base_confidence + context_boost, 1.0)

        # Generate suggestions
        suggestions = self._generate_suggestions(top_intent, text, context)

        return {
            "should_trigger": final_confidence >= 0.5,
            "confidence": round(final_confidence, 2),
            "intent": top_intent,
            "matched_patterns": matched_patterns,
            "suggestions": suggestions
        }

    def _calculate_context_boost(self, text: str, context: Optional[Dict[str, Any]]) -> float:
        """Calculate confidence boost from context"""
        boost = 0.0

        # Check for context keywords
        for category, keywords in self.context_keywords.items():
            if any(kw in text for kw in keywords):
                boost += 0.1

        if not context:
            return boost

        # Check current file context
        current_file = context.get("current_file", "")
        if current_file:
            for category, patterns in self.file_patterns.items():
                if any(re.match(pattern, current_file, re.IGNORECASE) for pattern in patterns):
                    boost += 0.15

        # Check if knowledge base exists
        if self.kb_path and self.kb_path.exists():
            boost += 0.1

        # Check conversation history
        history = context.get("conversation_history", [])
        if history:
            # Check if Project Guardian was mentioned recently
            recent_mentions = sum(1 for msg in history[-5:] if "project guardian" in msg.lower())
            boost += min(recent_mentions * 0.05, 0.15)

        return boost

    def _generate_suggestions(self, intent: str, text: str, context: Optional[Dict[str, Any]]) -> List[str]:
        """Generate action suggestions based on intent"""
        suggestions = []

        if intent == "query":
            suggestions.append("Use search_similar.py to find related records")
            if "semantic" in text.lower():
                suggestions.append("Consider using --semantic flag for AI-powered search")

        elif intent == "record":
            if "bug" in text.lower():
                suggestions.append("Use update_knowledge.py --quick-bug for fast recording")
            elif "requirement" in text.lower():
                suggestions.append("Use update_knowledge.py --quick-req for fast recording")
            elif "decision" in text.lower():
                suggestions.append("Use update_knowledge.py --quick-decision for fast recording")

        elif intent == "update":
            if "incremental" in text.lower() or "refresh" in text.lower():
                suggestions.append("Use incremental_update.py for fast updates")
            else:
                suggestions.append("Use update_knowledge.py to modify records")

        elif intent == "analyze":
            if "health" in text.lower():
                suggestions.append("Use health_checker.py to check knowledge base quality")
            elif "pattern" in text.lower() or "usage" in text.lower():
                suggestions.append("Use pattern_analyzer.py to analyze query patterns")
            elif "stats" in text.lower():
                suggestions.append("Use query_logger.py --stats for query statistics")

        elif intent == "initialize":
            if not self.kb_path or not self.kb_path.exists():
                suggestions.append("Run scan_project.py to initialize knowledge base")
            else:
                suggestions.append("Knowledge base already exists. Use incremental_update.py to refresh.")

        return suggestions

    def should_auto_initialize(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if auto-initialization should be suggested"""
        if not self.project_path:
            return False

        # Check if knowledge base exists
        if self.kb_path and self.kb_path.exists():
            return False

        # Check if this looks like a project directory
        project_indicators = [
            "package.json",
            "requirements.txt",
            "go.mod",
            "Cargo.toml",
            "pom.xml",
            "build.gradle",
            ".git"
        ]

        has_indicators = any((self.project_path / indicator).exists() for indicator in project_indicators)

        return has_indicators

    def get_trigger_stats(self) -> Dict[str, Any]:
        """Get trigger detection statistics"""
        if not self.kb_path or not self.kb_path.exists():
            return {"error": "Knowledge base not found"}

        queries_dir = self.kb_path / "history" / "queries"
        if not queries_dir.exists():
            return {"total_triggers": 0, "by_intent": {}}

        query_files = list(queries_dir.glob("QUERY-*.json"))

        intent_counts = {}
        for query_file in query_files:
            try:
                with open(query_file, 'r') as f:
                    query = json.load(f)
                    intent = query.get("context", {}).get("intent", "unknown")
                    intent_counts[intent] = intent_counts.get(intent, 0) + 1
            except Exception:
                continue

        return {
            "total_triggers": len(query_files),
            "by_intent": intent_counts
        }


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Detect trigger:        python trigger_detector.py '<text>' [--project <path>] [--context <context.json>]")
        print("  Check auto-init:       python trigger_detector.py --check-init <project_path>")
        print("  Get stats:             python trigger_detector.py --stats <project_path>")
        print()
        print("Examples:")
        print("  python trigger_detector.py 'find similar bugs about authentication'")
        print("  python trigger_detector.py '记录一个新的bug' --project /path/to/project")
        print("  python trigger_detector.py --check-init /path/to/project")
        sys.exit(1)

    if "--check-init" in sys.argv:
        project_path = sys.argv[sys.argv.index("--check-init") + 1]
        detector = TriggerDetector(project_path)

        should_init = detector.should_auto_initialize()
        print(json.dumps({
            "should_auto_initialize": should_init,
            "project_path": str(detector.project_path),
            "kb_exists": detector.kb_path.exists() if detector.kb_path else False
        }, indent=2))

    elif "--stats" in sys.argv:
        project_path = sys.argv[sys.argv.index("--stats") + 1]
        detector = TriggerDetector(project_path)

        stats = detector.get_trigger_stats()
        print("📊 Trigger Statistics:")
        print(json.dumps(stats, indent=2))

    else:
        text = sys.argv[1]

        project_path = None
        if "--project" in sys.argv:
            project_idx = sys.argv.index("--project")
            project_path = sys.argv[project_idx + 1]

        context = None
        if "--context" in sys.argv:
            context_idx = sys.argv.index("--context")
            context_file = sys.argv[context_idx + 1]
            with open(context_file, 'r') as f:
                context = json.load(f)

        detector = TriggerDetector(project_path)
        result = detector.detect(text, context)

        print("🎯 Trigger Detection Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if result["should_trigger"]:
            print(f"\n✅ Should trigger Project Guardian (confidence: {result['confidence']})")
            print(f"   Intent: {result['intent']}")
            if result["suggestions"]:
                print("\n💡 Suggestions:")
                for suggestion in result["suggestions"]:
                    print(f"   - {suggestion}")
        else:
            print(f"\n❌ Should not trigger (confidence: {result['confidence']})")


if __name__ == "__main__":
    main()

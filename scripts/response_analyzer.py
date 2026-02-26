#!/usr/bin/env python3
"""
Project Guardian - Response Analyzer

Intelligently analyzes conversation responses to determine if they should be recorded:
- Bug discoveries and solutions
- Architecture decisions and rationale
- Important requirements and clarifications
- Code conventions and best practices
- Performance insights and optimizations
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class ResponseAnalyzer:
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path).resolve() if project_path else None
        self.kb_path = self.project_path / ".project-ai" if self.project_path else None

        # Patterns that indicate recordable content
        self.recordable_patterns = {
            "bug": {
                "indicators": [
                    r"\b(bug|issue|error|exception|crash|fail)\b.*\b(found|discovered|encountered|fixed|resolved)\b",
                    r"\b(root\s+cause|caused\s+by|due\s+to)\b",
                    r"\b(solution|fix|workaround|patch)\b.*\b(is|was|should)\b",
                    r"\b(reproduce|reproduction\s+steps)\b",
                    r"\b(stack\s+trace|error\s+message)\b",
                ],
                "chinese": [
                    r"(发现|遇到|修复|解决).*(bug|问题|错误|异常|崩溃)",
                    r"(根本原因|原因是|由于)",
                    r"(解决方案|修复方法|临时方案)",
                    r"(复现|重现步骤)",
                ]
            },
            "decision": {
                "indicators": [
                    r"\b(decided|chose|selected|opted\s+for)\b.*\b(because|since|as|due\s+to)\b",
                    r"\b(architecture|design|approach|strategy)\b.*\b(decision|choice)\b",
                    r"\b(trade-?off|pros?\s+and\s+cons?|advantage|disadvantage)\b",
                    r"\b(alternative|option|considered)\b.*\b(rejected|dismissed|not\s+chosen)\b",
                    r"\b(rationale|reasoning|justification)\b",
                ],
                "chinese": [
                    r"(决定|选择|采用).*(因为|由于|考虑到)",
                    r"(架构|设计|方案|策略).*(决策|选择)",
                    r"(权衡|优缺点|优势|劣势)",
                    r"(替代方案|备选|考虑过).*(放弃|不采用)",
                ]
            },
            "requirement": {
                "indicators": [
                    r"\b(requirement|feature|functionality|capability)\b.*\b(should|must|need|require)\b",
                    r"\b(user\s+story|use\s+case|scenario)\b",
                    r"\b(acceptance\s+criteria|definition\s+of\s+done)\b",
                    r"\b(priority|critical|important|essential)\b",
                    r"\b(constraint|limitation|restriction)\b",
                ],
                "chinese": [
                    r"(需求|功能|特性).*(应该|必须|需要|要求)",
                    r"(用户故事|使用场景|场景)",
                    r"(验收标准|完成定义)",
                    r"(优先级|关键|重要|必要)",
                    r"(约束|限制)",
                ]
            },
            "convention": {
                "indicators": [
                    r"\b(convention|standard|guideline|best\s+practice)\b",
                    r"\b(naming\s+convention|code\s+style|pattern)\b",
                    r"\b(always|never|should\s+always|should\s+never)\b.*\b(use|do|implement)\b",
                    r"\b(consistent|consistency|uniformly)\b",
                    r"\b(team\s+agreed|team\s+decided|we\s+use)\b",
                ],
                "chinese": [
                    r"(约定|规范|标准|最佳实践)",
                    r"(命名规范|代码风格|模式)",
                    r"(总是|永远|应该总是|不应该).*(使用|做|实现)",
                    r"(一致|统一)",
                    r"(团队约定|团队决定|我们使用)",
                ]
            },
            "performance": {
                "indicators": [
                    r"\b(performance|optimization|optimize|faster|slower)\b",
                    r"\b(bottleneck|slow|latency|throughput)\b",
                    r"\b(cache|caching|memoize|lazy\s+load)\b",
                    r"\b(memory\s+leak|memory\s+usage|cpu\s+usage)\b",
                    r"\b(benchmark|profiling|measurement)\b",
                ],
                "chinese": [
                    r"(性能|优化|更快|更慢)",
                    r"(瓶颈|慢|延迟|吞吐量)",
                    r"(缓存|懒加载)",
                    r"(内存泄漏|内存占用|CPU占用)",
                    r"(基准测试|性能分析|测量)",
                ]
            }
        }

        # Negative patterns (content that should NOT be recorded)
        self.skip_patterns = [
            r"^\s*(hi|hello|hey|thanks|thank\s+you|ok|okay|yes|no|sure)\s*$",
            r"^\s*[?!.]+\s*$",
            r"\b(how\s+are\s+you|what'?s\s+up|good\s+morning|good\s+night)\b",
            r"^\s*(你好|谢谢|好的|是的|不是)\s*$",
        ]

    def analyze(self, user_message: str, assistant_response: str,
                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze conversation to determine if it should be recorded

        Returns:
            {
                "should_record": bool,
                "record_type": str,  # bug, decision, requirement, convention, performance
                "confidence": float,  # 0-1
                "extracted_info": Dict,
                "suggestions": List[str]
            }
        """
        # Combine messages for analysis
        full_text = f"{user_message}\n\n{assistant_response}"

        # Check skip patterns first
        if self._should_skip(full_text):
            return {
                "should_record": False,
                "record_type": None,
                "confidence": 0.0,
                "extracted_info": {},
                "suggestions": []
            }

        # Score each record type
        type_scores = {}
        for record_type, patterns in self.recordable_patterns.items():
            score = self._calculate_score(full_text, patterns)
            if score > 0:
                type_scores[record_type] = score

        # No recordable content found
        if not type_scores:
            return {
                "should_record": False,
                "record_type": None,
                "confidence": 0.0,
                "extracted_info": {},
                "suggestions": []
            }

        # Get top scoring type
        top_type = max(type_scores, key=type_scores.get)
        confidence = min(type_scores[top_type] * 0.2, 1.0)  # Scale to 0-1

        # Extract information based on type
        extracted_info = self._extract_info(full_text, top_type, context)

        # Generate suggestions
        suggestions = self._generate_suggestions(top_type, extracted_info)

        return {
            "should_record": confidence >= 0.5,
            "record_type": top_type,
            "confidence": round(confidence, 2),
            "extracted_info": extracted_info,
            "suggestions": suggestions
        }

    def _should_skip(self, text: str) -> bool:
        """Check if content should be skipped"""
        text_lower = text.lower().strip()

        # Too short
        if len(text_lower) < 20:
            return True

        # Matches skip patterns
        for pattern in self.skip_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

        return False

    def _calculate_score(self, text: str, patterns: Dict[str, List[str]]) -> int:
        """Calculate score for a record type"""
        score = 0
        text_lower = text.lower()

        # Check English patterns
        for pattern in patterns.get("indicators", []):
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 1

        # Check Chinese patterns
        for pattern in patterns.get("chinese", []):
            if re.search(pattern, text, re.IGNORECASE):
                score += 1

        return score

    def _extract_info(self, text: str, record_type: str,
                     context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract structured information based on record type"""
        info = {
            "timestamp": datetime.now().isoformat(),
            "raw_text": text[:500],  # First 500 chars
        }

        if context:
            info["context"] = {
                "current_file": context.get("current_file"),
                "module": context.get("module"),
            }

        if record_type == "bug":
            info.update(self._extract_bug_info(text))
        elif record_type == "decision":
            info.update(self._extract_decision_info(text))
        elif record_type == "requirement":
            info.update(self._extract_requirement_info(text))
        elif record_type == "convention":
            info.update(self._extract_convention_info(text))
        elif record_type == "performance":
            info.update(self._extract_performance_info(text))

        return info

    def _extract_bug_info(self, text: str) -> Dict[str, Any]:
        """Extract bug-related information"""
        info = {}

        # Extract error messages
        error_patterns = [
            r"error[:\s]+([^\n]+)",
            r"exception[:\s]+([^\n]+)",
            r"错误[：\s]+([^\n]+)",
        ]
        for pattern in error_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["error_message"] = match.group(1).strip()
                break

        # Extract root cause
        cause_patterns = [
            r"(?:root\s+cause|caused\s+by|due\s+to)[:\s]+([^\n]+)",
            r"(?:根本原因|原因是|由于)[：\s]+([^\n]+)",
        ]
        for pattern in cause_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["root_cause"] = match.group(1).strip()
                break

        # Extract solution
        solution_patterns = [
            r"(?:solution|fix|workaround)[:\s]+([^\n]+)",
            r"(?:解决方案|修复方法)[：\s]+([^\n]+)",
        ]
        for pattern in solution_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["solution"] = match.group(1).strip()
                break

        return info

    def _extract_decision_info(self, text: str) -> Dict[str, Any]:
        """Extract architecture decision information"""
        info = {}

        # Extract decision
        decision_patterns = [
            r"(?:decided|chose|selected)[:\s]+([^\n]+)",
            r"(?:决定|选择|采用)[：\s]+([^\n]+)",
        ]
        for pattern in decision_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["decision"] = match.group(1).strip()
                break

        # Extract rationale
        rationale_patterns = [
            r"(?:because|since|rationale)[:\s]+([^\n]+)",
            r"(?:因为|由于|理由)[：\s]+([^\n]+)",
        ]
        for pattern in rationale_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["rationale"] = match.group(1).strip()
                break

        return info

    def _extract_requirement_info(self, text: str) -> Dict[str, Any]:
        """Extract requirement information"""
        info = {}

        # Extract requirement description
        req_patterns = [
            r"(?:requirement|feature)[:\s]+([^\n]+)",
            r"(?:需求|功能)[：\s]+([^\n]+)",
        ]
        for pattern in req_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["description"] = match.group(1).strip()
                break

        # Extract priority
        if re.search(r"\b(critical|high\s+priority|urgent|关键|高优先级|紧急)\b", text, re.IGNORECASE):
            info["priority"] = "high"
        elif re.search(r"\b(low\s+priority|nice\s+to\s+have|低优先级)\b", text, re.IGNORECASE):
            info["priority"] = "low"
        else:
            info["priority"] = "medium"

        return info

    def _extract_convention_info(self, text: str) -> Dict[str, Any]:
        """Extract coding convention information"""
        info = {}

        # Extract convention rule
        convention_patterns = [
            r"(?:always|never|should)[:\s]+([^\n]+)",
            r"(?:总是|永远|应该)[：\s]+([^\n]+)",
        ]
        for pattern in convention_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["rule"] = match.group(1).strip()
                break

        return info

    def _extract_performance_info(self, text: str) -> Dict[str, Any]:
        """Extract performance-related information"""
        info = {}

        # Extract performance issue
        perf_patterns = [
            r"(?:bottleneck|slow|performance\s+issue)[:\s]+([^\n]+)",
            r"(?:瓶颈|慢|性能问题)[：\s]+([^\n]+)",
        ]
        for pattern in perf_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["issue"] = match.group(1).strip()
                break

        # Extract optimization
        opt_patterns = [
            r"(?:optimization|optimized|improved)[:\s]+([^\n]+)",
            r"(?:优化|改进)[：\s]+([^\n]+)",
        ]
        for pattern in opt_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["optimization"] = match.group(1).strip()
                break

        return info

    def _generate_suggestions(self, record_type: str,
                            extracted_info: Dict[str, Any]) -> List[str]:
        """Generate action suggestions"""
        suggestions = []

        if record_type == "bug":
            if "error_message" in extracted_info:
                suggestions.append(f"Record bug with error: {extracted_info['error_message'][:50]}...")
            if "solution" in extracted_info:
                suggestions.append("Include solution in bug record")
            suggestions.append("Use: python update_knowledge.py . --quick-bug")

        elif record_type == "decision":
            suggestions.append("Record as Architecture Decision Record (ADR)")
            suggestions.append("Use: python update_knowledge.py . --quick-decision")

        elif record_type == "requirement":
            priority = extracted_info.get("priority", "medium")
            suggestions.append(f"Record requirement with {priority} priority")
            suggestions.append("Use: python update_knowledge.py . --quick-req")

        elif record_type == "convention":
            suggestions.append("Add to project conventions")
            suggestions.append("Update: .project-ai/core/conventions.json")

        elif record_type == "performance":
            suggestions.append("Record performance insight")
            suggestions.append("Consider adding benchmark data")

        return suggestions

    def auto_record(self, analysis_result: Dict[str, Any]) -> Optional[str]:
        """Automatically record if confidence is high enough"""
        if not analysis_result["should_record"]:
            return None

        if not self.kb_path or not self.kb_path.exists():
            return None

        record_type = analysis_result["record_type"]
        extracted_info = analysis_result["extracted_info"]

        # Only auto-record if confidence is very high (>0.8)
        if analysis_result["confidence"] < 0.8:
            return None

        # Create record based on type
        if record_type == "bug":
            return self._auto_record_bug(extracted_info)
        elif record_type == "decision":
            return self._auto_record_decision(extracted_info)
        # Add more auto-record handlers as needed

        return None

    def _auto_record_bug(self, info: Dict[str, Any]) -> Optional[str]:
        """Auto-record a bug"""
        # This would call update_knowledge.py
        # For now, just return the command that should be run
        error_msg = info.get("error_message", "Unknown error")
        return f"python update_knowledge.py . --quick-bug --title '{error_msg[:50]}' --description '{info.get('raw_text', '')[:200]}'"

    def _auto_record_decision(self, info: Dict[str, Any]) -> Optional[str]:
        """Auto-record a decision"""
        decision = info.get("decision", "Architecture decision")
        return f"python update_knowledge.py . --quick-decision --title '{decision[:50]}' --description '{info.get('raw_text', '')[:200]}'"


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Analyze conversation:")
        print("    python response_analyzer.py <project_path> --user '<user_msg>' --assistant '<assistant_msg>'")
        print()
        print("  Analyze from JSON:")
        print("    python response_analyzer.py <project_path> --json <conversation.json>")
        print()
        print("  Auto-record if confidence high:")
        print("    python response_analyzer.py <project_path> --user '<msg>' --assistant '<msg>' --auto-record")
        sys.exit(1)

    project_path = sys.argv[1] if sys.argv[1] != "--help" else None

    try:
        analyzer = ResponseAnalyzer(project_path)

        if "--json" in sys.argv:
            json_idx = sys.argv.index("--json")
            json_file = sys.argv[json_idx + 1]
            with open(json_file, 'r') as f:
                data = json.load(f)
            user_msg = data.get("user_message", "")
            assistant_msg = data.get("assistant_response", "")
            context = data.get("context")
        else:
            user_idx = sys.argv.index("--user")
            assistant_idx = sys.argv.index("--assistant")
            user_msg = sys.argv[user_idx + 1]
            assistant_msg = sys.argv[assistant_idx + 1]
            context = None

        # Analyze
        result = analyzer.analyze(user_msg, assistant_msg, context)

        print("🔍 Response Analysis Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if result["should_record"]:
            print(f"\n✅ Should record as: {result['record_type']} (confidence: {result['confidence']})")
            print("\n💡 Suggestions:")
            for suggestion in result["suggestions"]:
                print(f"   - {suggestion}")

            # Auto-record if requested
            if "--auto-record" in sys.argv:
                command = analyzer.auto_record(result)
                if command:
                    print(f"\n🤖 Auto-record command:")
                    print(f"   {command}")
        else:
            print(f"\n❌ Should not record (confidence: {result['confidence']})")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

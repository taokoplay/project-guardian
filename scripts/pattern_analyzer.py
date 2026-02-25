#!/usr/bin/env python3
"""
Project Guardian - Pattern Analyzer

Analyzes query patterns to identify:
- Frequently asked questions
- Knowledge gaps (queries without results)
- Popular modules and topics
- Optimization opportunities
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import Counter


class PatternAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.kb_path = self.project_path / ".project-ai"

        if not self.kb_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.kb_path}. "
                "Run scan_project.py first to initialize."
            )

        self.queries_dir = self.kb_path / "history" / "queries"

    def _load_json(self, file_path: Path) -> Any:
        """Load JSON file safely"""
        if not file_path.exists():
            return {}
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _load_all_queries(self) -> List[Dict[str, Any]]:
        """Load all query records"""
        if not self.queries_dir.exists():
            return []

        queries = []
        for query_file in self.queries_dir.glob("QUERY-*.json"):
            query = self._load_json(query_file)
            if query:
                queries.append(query)

        return queries

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        import re

        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'when', 'where', 'why', 'how', 'work', 'works', 'working'
        }

        # Tokenize and filter
        words = re.findall(r'\w+', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords

    def analyze_frequent_questions(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Find most frequently asked questions"""
        queries = self._load_all_queries()

        # Count similar queries (by keywords)
        query_patterns = Counter()

        for query in queries:
            query_text = query.get("query", "")
            keywords = tuple(sorted(self._extract_keywords(query_text)[:5]))  # Top 5 keywords
            if keywords:
                query_patterns[keywords] += 1

        # Get top patterns
        top_patterns = query_patterns.most_common(limit)

        # Convert back to readable format
        result = []
        for keywords, count in top_patterns:
            pattern = " + ".join(keywords)
            result.append((pattern, count))

        return result

    def identify_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """Identify queries that didn't find results (knowledge gaps)"""
        queries = self._load_all_queries()

        knowledge_gaps = []

        for query in queries:
            results = query.get("results", {})
            has_results = bool(
                results.get("found_bugs") or
                results.get("found_requirements") or
                results.get("found_decisions")
            )

            if not has_results:
                knowledge_gaps.append({
                    "query": query.get("query", ""),
                    "timestamp": query.get("timestamp", ""),
                    "keywords": self._extract_keywords(query.get("query", ""))
                })

        return knowledge_gaps

    def analyze_popular_modules(self) -> List[Tuple[str, int]]:
        """Identify most queried modules"""
        queries = self._load_all_queries()

        module_keywords = {
            "auth": ["auth", "login", "oauth", "session", "user", "password", "token", "authentication"],
            "api": ["api", "endpoint", "route", "request", "response", "http", "rest"],
            "database": ["database", "db", "sql", "query", "model", "schema", "table"],
            "ui": ["ui", "component", "view", "page", "render", "display", "frontend"],
            "config": ["config", "setting", "environment", "env", "configuration"],
            "payment": ["payment", "stripe", "checkout", "billing", "subscription"],
            "notification": ["notification", "email", "sms", "push", "alert"],
            "search": ["search", "filter", "find", "lookup", "query"],
            "file": ["file", "upload", "download", "storage", "s3", "blob"],
            "cache": ["cache", "redis", "memcache", "caching"]
        }

        module_counts = Counter()

        for query in queries:
            query_text = query.get("query", "").lower()
            keywords = self._extract_keywords(query_text)

            for module, module_kws in module_keywords.items():
                if any(kw in keywords for kw in module_kws):
                    module_counts[module] += 1

        return module_counts.most_common(10)

    def analyze_time_patterns(self) -> Dict[str, Any]:
        """Analyze query patterns over time"""
        queries = self._load_all_queries()

        if not queries:
            return {"error": "No queries found"}

        # Parse timestamps
        timestamps = []
        for query in queries:
            try:
                ts = datetime.fromisoformat(query.get("timestamp", ""))
                timestamps.append(ts)
            except ValueError:
                continue

        if not timestamps:
            return {"error": "No valid timestamps"}

        # Calculate statistics
        timestamps.sort()
        first_query = timestamps[0]
        last_query = timestamps[-1]
        total_days = (last_query - first_query).days + 1

        # Queries per day
        queries_per_day = len(timestamps) / total_days if total_days > 0 else 0

        # Recent activity (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_queries = [ts for ts in timestamps if ts > seven_days_ago]

        # Peak hours (if enough data)
        hour_counts = Counter([ts.hour for ts in timestamps])
        peak_hour = hour_counts.most_common(1)[0] if hour_counts else (0, 0)

        return {
            "first_query": first_query.isoformat(),
            "last_query": last_query.isoformat(),
            "total_days": total_days,
            "total_queries": len(timestamps),
            "queries_per_day": round(queries_per_day, 2),
            "recent_queries_7d": len(recent_queries),
            "peak_hour": peak_hour[0],
            "peak_hour_count": peak_hour[1]
        }

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Analyze knowledge gaps
        gaps = self.identify_knowledge_gaps()
        if len(gaps) > 5:
            recommendations.append(
                f"📝 Found {len(gaps)} queries without results. Consider documenting these topics:"
            )
            # Group by common keywords
            gap_keywords = Counter()
            for gap in gaps:
                for keyword in gap["keywords"][:3]:
                    gap_keywords[keyword] += 1

            top_gaps = gap_keywords.most_common(5)
            for keyword, count in top_gaps:
                recommendations.append(f"   - {keyword} ({count} queries)")

        # Analyze popular modules
        popular = self.analyze_popular_modules()
        if popular:
            top_module = popular[0]
            recommendations.append(
                f"🔥 Most queried module: {top_module[0]} ({top_module[1]} queries). "
                f"Consider adding more documentation."
            )

        # Analyze time patterns
        time_patterns = self.analyze_time_patterns()
        if "queries_per_day" in time_patterns:
            qpd = time_patterns["queries_per_day"]
            if qpd < 0.5:
                recommendations.append(
                    f"📉 Low usage ({qpd:.1f} queries/day). Consider promoting the knowledge base."
                )
            elif qpd > 5:
                recommendations.append(
                    f"📈 High usage ({qpd:.1f} queries/day). Knowledge base is actively used!"
                )

        if not recommendations:
            recommendations.append("✨ No specific recommendations at this time.")

        return recommendations

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        print("📊 Analyzing query patterns...\n")

        report = {
            "timestamp": datetime.now().isoformat(),
            "frequent_questions": self.analyze_frequent_questions(),
            "knowledge_gaps": self.identify_knowledge_gaps(),
            "popular_modules": self.analyze_popular_modules(),
            "time_patterns": self.analyze_time_patterns(),
            "recommendations": self.generate_recommendations()
        }

        return report


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Full analysis:     python pattern_analyzer.py <project_path>")
        print("  Frequent questions: python pattern_analyzer.py <project_path> --frequent [limit]")
        print("  Knowledge gaps:    python pattern_analyzer.py <project_path> --gaps")
        print("  Popular modules:   python pattern_analyzer.py <project_path> --modules")
        print("  Time patterns:     python pattern_analyzer.py <project_path> --time")
        print("  Recommendations:   python pattern_analyzer.py <project_path> --recommend")
        sys.exit(1)

    project_path = sys.argv[1]

    try:
        analyzer = PatternAnalyzer(project_path)

        if "--frequent" in sys.argv:
            limit = 10
            if len(sys.argv) > sys.argv.index("--frequent") + 1:
                try:
                    limit = int(sys.argv[sys.argv.index("--frequent") + 1])
                except ValueError:
                    pass

            patterns = analyzer.analyze_frequent_questions(limit)
            print("🔥 Most Frequent Question Patterns:")
            for i, (pattern, count) in enumerate(patterns, 1):
                print(f"  {i}. {pattern} ({count} times)")

        elif "--gaps" in sys.argv:
            gaps = analyzer.identify_knowledge_gaps()
            print(f"📝 Knowledge Gaps ({len(gaps)} queries without results):")
            for gap in gaps[:10]:
                print(f"  - {gap['query'][:80]}")
                print(f"    Keywords: {', '.join(gap['keywords'][:5])}")

        elif "--modules" in sys.argv:
            modules = analyzer.analyze_popular_modules()
            print("📦 Most Queried Modules:")
            for i, (module, count) in enumerate(modules, 1):
                print(f"  {i}. {module}: {count} queries")

        elif "--time" in sys.argv:
            patterns = analyzer.analyze_time_patterns()
            print("⏰ Time Patterns:")
            for key, value in patterns.items():
                print(f"  {key}: {value}")

        elif "--recommend" in sys.argv:
            recommendations = analyzer.generate_recommendations()
            print("💡 Recommendations:")
            for rec in recommendations:
                print(f"  {rec}")

        else:
            # Full report
            report = analyzer.generate_report()

            print("="*60)
            print("📊 QUERY PATTERN ANALYSIS REPORT")
            print("="*60)

            print("\n🔥 Top 5 Frequent Question Patterns:")
            for i, (pattern, count) in enumerate(report["frequent_questions"][:5], 1):
                print(f"  {i}. {pattern} ({count} times)")

            print(f"\n📝 Knowledge Gaps: {len(report['knowledge_gaps'])} queries without results")
            if report["knowledge_gaps"]:
                print("  Recent examples:")
                for gap in report["knowledge_gaps"][:3]:
                    print(f"    - {gap['query'][:60]}...")

            print("\n📦 Top 5 Popular Modules:")
            for i, (module, count) in enumerate(report["popular_modules"][:5], 1):
                print(f"  {i}. {module}: {count} queries")

            print("\n⏰ Time Patterns:")
            time_patterns = report["time_patterns"]
            if "error" not in time_patterns:
                print(f"  Total queries: {time_patterns['total_queries']}")
                print(f"  Queries per day: {time_patterns['queries_per_day']}")
                print(f"  Recent (7 days): {time_patterns['recent_queries_7d']}")

            print("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"  {rec}")

            print("\n" + "="*60)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

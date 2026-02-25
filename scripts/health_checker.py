#!/usr/bin/env python3
"""
Project Guardian - Knowledge Base Health Checker

Monitors knowledge base quality, completeness, and freshness.
Provides actionable recommendations for maintenance.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple


class HealthChecker:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.kb_path = self.project_path / ".project-ai"

        if not self.kb_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.kb_path}. "
                "Run scan_project.py first to initialize."
            )

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file safely"""
        if not file_path.exists():
            return {}
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _count_files(self, directory: Path, pattern: str = "*.json") -> int:
        """Count files in a directory"""
        if not directory.exists():
            return 0
        return len(list(directory.glob(pattern)))

    def check_freshness(self) -> Tuple[int, List[str]]:
        """Check if knowledge base is up to date"""
        score = 100
        issues = []

        profile = self._load_json(self.kb_path / "core" / "profile.json")
        last_updated = profile.get("last_updated")

        if not last_updated:
            score -= 30
            issues.append("⚠️  No last_updated timestamp found")
            return score, issues

        try:
            last_update_date = datetime.fromisoformat(last_updated)
            days_old = (datetime.now() - last_update_date).days

            if days_old > 90:
                score -= 40
                issues.append(f"🔴 Knowledge base is {days_old} days old (very stale)")
            elif days_old > 30:
                score -= 20
                issues.append(f"🟡 Knowledge base is {days_old} days old (stale)")
            elif days_old > 7:
                score -= 5
                issues.append(f"🟢 Knowledge base is {days_old} days old (slightly stale)")
            else:
                issues.append(f"✅ Knowledge base is {days_old} days old (fresh)")

        except ValueError:
            score -= 20
            issues.append("⚠️  Invalid last_updated timestamp format")

        return score, issues

    def check_completeness(self) -> Tuple[int, List[str]]:
        """Check if all required files exist"""
        score = 100
        issues = []

        # Check core files
        core_files = {
            "profile.json": "Project profile",
            "tech-stack.json": "Tech stack information",
            "conventions.json": "Code conventions"
        }

        missing_core = []
        for file, desc in core_files.items():
            if not (self.kb_path / "core" / file).exists():
                missing_core.append(desc)

        if missing_core:
            score -= 30
            issues.append(f"🔴 Missing core files: {', '.join(missing_core)}")

        # Check indexed files
        indexed_files = {
            "architecture.json": "Architecture documentation",
            "modules.json": "Module descriptions",
            "tools.json": "Development tools",
            "structure.json": "Project structure"
        }

        missing_indexed = []
        for file, desc in indexed_files.items():
            if not (self.kb_path / "indexed" / file).exists():
                missing_indexed.append(desc)

        if missing_indexed:
            score -= 10
            issues.append(f"🟡 Missing indexed files: {', '.join(missing_indexed)}")

        # Check history directories
        history_dirs = ["bugs", "requirements", "decisions"]
        missing_history = []

        for dir_name in history_dirs:
            if not (self.kb_path / "history" / dir_name).exists():
                missing_history.append(dir_name)

        if missing_history:
            score -= 10
            issues.append(f"🟡 Missing history directories: {', '.join(missing_history)}")

        if not missing_core and not missing_indexed and not missing_history:
            issues.append("✅ All required files and directories exist")

        return score, issues

    def check_bug_quality(self) -> Tuple[int, List[str]]:
        """Check quality of bug records"""
        score = 100
        issues = []

        bugs_dir = self.kb_path / "history" / "bugs"
        if not bugs_dir.exists():
            return score, ["ℹ️  No bugs directory found"]

        bug_files = list(bugs_dir.glob("*.json"))
        if not bug_files:
            return score, ["ℹ️  No bugs recorded yet"]

        total_bugs = len(bug_files)
        bugs_without_solution = 0
        bugs_without_root_cause = 0
        bugs_without_tags = 0

        for bug_file in bug_files:
            bug = self._load_json(bug_file)
            if not bug:
                continue

            if not bug.get("solution"):
                bugs_without_solution += 1

            if not bug.get("root_cause"):
                bugs_without_root_cause += 1

            if not bug.get("tags"):
                bugs_without_tags += 1

        # Calculate penalties
        if bugs_without_solution > 0:
            penalty = min(30, (bugs_without_solution / total_bugs) * 50)
            score -= penalty
            issues.append(f"🟡 {bugs_without_solution}/{total_bugs} bugs missing solution")

        if bugs_without_root_cause > 0:
            penalty = min(20, (bugs_without_root_cause / total_bugs) * 40)
            score -= penalty
            issues.append(f"🟡 {bugs_without_root_cause}/{total_bugs} bugs missing root cause")

        if bugs_without_tags > 0:
            penalty = min(10, (bugs_without_tags / total_bugs) * 20)
            score -= penalty
            issues.append(f"ℹ️  {bugs_without_tags}/{total_bugs} bugs missing tags")

        if score == 100:
            issues.append(f"✅ All {total_bugs} bugs have complete information")

        return score, issues

    def check_size(self) -> Tuple[int, List[str]]:
        """Check knowledge base size"""
        score = 100
        issues = []

        # Count records
        bugs_count = self._count_files(self.kb_path / "history" / "bugs")
        reqs_count = self._count_files(self.kb_path / "history" / "requirements")
        decisions_count = self._count_files(self.kb_path / "history" / "decisions")

        total_records = bugs_count + reqs_count + decisions_count

        issues.append(f"📊 Total records: {total_records} ({bugs_count} bugs, {reqs_count} requirements, {decisions_count} decisions)")

        # Check if too large (might need compression)
        if total_records > 500:
            score -= 20
            issues.append("🟡 Knowledge base is large (>500 records), consider compression")
        elif total_records > 1000:
            score -= 40
            issues.append("🔴 Knowledge base is very large (>1000 records), compression recommended")

        # Check if too small (might not be used)
        if total_records == 0:
            score -= 10
            issues.append("ℹ️  No records yet, start using the knowledge base!")

        return score, issues

    def check_usage_patterns(self) -> Tuple[int, List[str]]:
        """Check if knowledge base is being actively used"""
        score = 100
        issues = []

        bugs_dir = self.kb_path / "history" / "bugs"
        if not bugs_dir.exists():
            return score, ["ℹ️  No usage data available"]

        # Check recent activity (last 30 days)
        recent_bugs = 0
        thirty_days_ago = datetime.now() - timedelta(days=30)

        for bug_file in bugs_dir.glob("*.json"):
            bug = self._load_json(bug_file)
            if not bug:
                continue

            recorded_at = bug.get("recorded_at")
            if recorded_at:
                try:
                    record_date = datetime.fromisoformat(recorded_at)
                    if record_date > thirty_days_ago:
                        recent_bugs += 1
                except ValueError:
                    pass

        if recent_bugs == 0:
            score -= 20
            issues.append("🟡 No bugs recorded in the last 30 days (inactive)")
        elif recent_bugs < 3:
            issues.append(f"ℹ️  {recent_bugs} bugs recorded in the last 30 days (low activity)")
        else:
            issues.append(f"✅ {recent_bugs} bugs recorded in the last 30 days (active)")

        return score, issues

    def generate_recommendations(self, all_issues: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Analyze issues and provide recommendations
        issue_text = " ".join(all_issues)

        if "stale" in issue_text or "days old" in issue_text:
            recommendations.append("🔄 Run incremental update: python scripts/incremental_update.py .")

        if "Missing" in issue_text:
            recommendations.append("🔍 Run full scan to regenerate missing files: python scripts/scan_project.py .")

        if "missing solution" in issue_text:
            recommendations.append("📝 Review and update bug records with solutions")

        if "missing root cause" in issue_text:
            recommendations.append("🔎 Analyze bugs and document root causes")

        if "compression" in issue_text:
            recommendations.append("🗜️  Consider archiving old records or implementing compression")

        if "inactive" in issue_text or "No bugs recorded" in issue_text:
            recommendations.append("💡 Start using the knowledge base to track bugs and requirements")

        if not recommendations:
            recommendations.append("✨ Knowledge base is in good health! Keep up the good work.")

        return recommendations

    def run_health_check(self) -> Dict[str, Any]:
        """Run complete health check"""
        print("🏥 Running knowledge base health check...\n")

        all_issues = []
        scores = {}

        # Run all checks
        checks = [
            ("Freshness", self.check_freshness),
            ("Completeness", self.check_completeness),
            ("Bug Quality", self.check_bug_quality),
            ("Size", self.check_size),
            ("Usage", self.check_usage_patterns)
        ]

        for check_name, check_func in checks:
            print(f"Checking {check_name}...")
            score, issues = check_func()
            scores[check_name] = score
            all_issues.extend(issues)

            for issue in issues:
                print(f"  {issue}")
            print()

        # Calculate overall score
        overall_score = sum(scores.values()) // len(scores)

        # Determine health status
        if overall_score >= 90:
            status = "🟢 Excellent"
        elif overall_score >= 75:
            status = "🟡 Good"
        elif overall_score >= 60:
            status = "🟠 Fair"
        else:
            status = "🔴 Needs Attention"

        # Generate recommendations
        recommendations = self.generate_recommendations(all_issues)

        result = {
            "overall_score": overall_score,
            "status": status,
            "scores": scores,
            "issues": all_issues,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }

        return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python health_checker.py <project_path> [--json]")
        sys.exit(1)

    project_path = sys.argv[1]
    output_json = "--json" in sys.argv

    try:
        checker = HealthChecker(project_path)
        result = checker.run_health_check()

        if output_json:
            print(json.dumps(result, indent=2))
        else:
            print("="*60)
            print(f"📊 HEALTH CHECK RESULTS")
            print("="*60)
            print(f"\n🎯 Overall Score: {result['overall_score']}/100")
            print(f"📈 Status: {result['status']}\n")

            print("📋 Detailed Scores:")
            for check_name, score in result['scores'].items():
                print(f"  {check_name}: {score}/100")

            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")

            print(f"\n⏰ Checked at: {result['timestamp']}")
            print("="*60)

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

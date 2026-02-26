#!/usr/bin/env python3
"""
Project Guardian - Conversation Hook

Hook script to be called after each conversation turn.
Analyzes responses and suggests/auto-records important information.

Usage in Claude Code:
  After each assistant response, call this script to analyze if content should be recorded.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Import response analyzer
try:
    from response_analyzer import ResponseAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False


class ConversationHook:
    def __init__(self, project_path: str, config: Optional[Dict[str, Any]] = None):
        self.project_path = Path(project_path).resolve()
        self.kb_path = self.project_path / ".project-ai"
        self.config = config or self._load_config()

        if ANALYZER_AVAILABLE:
            self.analyzer = ResponseAnalyzer(project_path)
        else:
            self.analyzer = None

    def _load_config(self) -> Dict[str, Any]:
        """Load hook configuration"""
        config_file = self.kb_path / "config" / "conversation_hook.json"

        default_config = {
            "enabled": True,
            "auto_record_threshold": 0.8,  # Auto-record if confidence >= 0.8
            "suggest_threshold": 0.5,      # Suggest if confidence >= 0.5
            "record_types": ["bug", "decision", "requirement", "convention", "performance"],
            "notification_style": "inline",  # inline, summary, silent
        }

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception:
                pass

        return default_config

    def process_conversation(self, user_message: str, assistant_response: str,
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a conversation turn

        Returns:
            {
                "analysis": Dict,
                "action_taken": str,  # none, suggested, recorded
                "notification": str,
                "commands": List[str]
            }
        """
        if not self.config["enabled"] or not self.analyzer:
            return {
                "analysis": None,
                "action_taken": "none",
                "notification": "",
                "commands": []
            }

        # Analyze conversation
        analysis = self.analyzer.analyze(user_message, assistant_response, context)

        # Determine action
        action_taken = "none"
        notification = ""
        commands = []

        if analysis["should_record"]:
            confidence = analysis["confidence"]
            record_type = analysis["record_type"]

            # Auto-record if confidence is high enough
            if confidence >= self.config["auto_record_threshold"]:
                command = self.analyzer.auto_record(analysis)
                if command:
                    action_taken = "recorded"
                    notification = self._format_notification(
                        "recorded", record_type, confidence, analysis["suggestions"]
                    )
                    commands.append(command)

            # Suggest recording if confidence is medium
            elif confidence >= self.config["suggest_threshold"]:
                action_taken = "suggested"
                notification = self._format_notification(
                    "suggested", record_type, confidence, analysis["suggestions"]
                )
                commands = [f"# {s}" for s in analysis["suggestions"]]

        return {
            "analysis": analysis,
            "action_taken": action_taken,
            "notification": notification,
            "commands": commands
        }

    def _format_notification(self, action: str, record_type: str,
                           confidence: float, suggestions: List[str]) -> str:
        """Format notification message"""
        style = self.config["notification_style"]

        if style == "silent":
            return ""

        if style == "inline":
            if action == "recorded":
                return f"🤖 [Project Guardian] Auto-recorded {record_type} (confidence: {confidence})"
            elif action == "suggested":
                return f"💡 [Project Guardian] Consider recording as {record_type} (confidence: {confidence})"

        elif style == "summary":
            lines = []
            if action == "recorded":
                lines.append(f"🤖 [Project Guardian] Auto-recorded {record_type}")
            elif action == "suggested":
                lines.append(f"💡 [Project Guardian] Recordable content detected:")
                lines.append(f"   Type: {record_type}")
                lines.append(f"   Confidence: {confidence}")
                if suggestions:
                    lines.append("   Suggestions:")
                    for suggestion in suggestions[:3]:
                        lines.append(f"     - {suggestion}")

            return "\n".join(lines)

        return ""

    def get_stats(self) -> Dict[str, Any]:
        """Get conversation hook statistics"""
        stats_file = self.kb_path / "history" / "conversation_stats.json"

        if not stats_file.exists():
            return {
                "total_conversations": 0,
                "auto_recorded": 0,
                "suggested": 0,
                "by_type": {}
            }

        try:
            with open(stats_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def update_stats(self, action: str, record_type: str):
        """Update conversation statistics"""
        stats_file = self.kb_path / "history" / "conversation_stats.json"
        stats_file.parent.mkdir(parents=True, exist_ok=True)

        stats = self.get_stats()

        stats["total_conversations"] = stats.get("total_conversations", 0) + 1

        if action == "recorded":
            stats["auto_recorded"] = stats.get("auto_recorded", 0) + 1
        elif action == "suggested":
            stats["suggested"] = stats.get("suggested", 0) + 1

        if record_type:
            by_type = stats.get("by_type", {})
            by_type[record_type] = by_type.get(record_type, 0) + 1
            stats["by_type"] = by_type

        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Process conversation:")
        print("    python conversation_hook.py <project_path> --user '<msg>' --assistant '<msg>'")
        print()
        print("  From JSON file:")
        print("    python conversation_hook.py <project_path> --json <conversation.json>")
        print()
        print("  Get statistics:")
        print("    python conversation_hook.py <project_path> --stats")
        print()
        print("  Configure:")
        print("    python conversation_hook.py <project_path> --config <config.json>")
        print()
        print("Options:")
        print("  --context <context.json>    Additional context (current file, module, etc.)")
        print("  --silent                    Suppress notifications")
        sys.exit(1)

    project_path = sys.argv[1]

    try:
        hook = ConversationHook(project_path)

        if "--stats" in sys.argv:
            stats = hook.get_stats()
            print("📊 Conversation Hook Statistics:")
            print(json.dumps(stats, indent=2))
            sys.exit(0)

        if "--config" in sys.argv:
            config_idx = sys.argv.index("--config")
            config_file = sys.argv[config_idx + 1]
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Save config
            config_path = hook.kb_path / "config" / "conversation_hook.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            print("✅ Configuration saved")
            sys.exit(0)

        # Load conversation
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
            if "--context" in sys.argv:
                context_idx = sys.argv.index("--context")
                context_file = sys.argv[context_idx + 1]
                with open(context_file, 'r') as f:
                    context = json.load(f)

        # Override notification style if silent
        if "--silent" in sys.argv:
            hook.config["notification_style"] = "silent"

        # Process conversation
        result = hook.process_conversation(user_msg, assistant_msg, context)

        # Update statistics
        if result["action_taken"] != "none":
            hook.update_stats(
                result["action_taken"],
                result["analysis"]["record_type"]
            )

        # Output result
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Print notification if not silent
        if result["notification"]:
            print("\n" + "="*60)
            print(result["notification"])

        # Print commands if any
        if result["commands"]:
            print("\n" + "="*60)
            print("📝 Suggested commands:")
            for cmd in result["commands"]:
                print(f"  {cmd}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Project Guardian - Initial Project Scanner

Automatically detects project type, tech stack, tools, and conventions.
Creates a lightweight knowledge base at <project-root>/.project-ai/
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ProjectScanner:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.knowledge_base_path = self.project_path / ".project-ai"

    def scan(self) -> Dict[str, Any]:
        """Main scanning entry point"""
        print(f"🔍 Scanning project: {self.project_path}")

        result = {
            "scanned_at": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "project_type": self._detect_project_type(),
            "tech_stack": self._detect_tech_stack(),
            "tools": self._detect_tools(),
            "conventions": self._detect_conventions(),
            "structure": self._analyze_structure(),
        }

        return result

    def _detect_project_type(self) -> str:
        """Detect project type based on files and structure"""
        indicators = {
            "web-frontend": ["package.json", "src/App.tsx", "src/App.jsx", "vite.config", "webpack.config"],
            "web-backend": ["server.js", "app.js", "main.go", "src/main/java", "requirements.txt"],
            "full-stack": ["package.json", "server", "client", "frontend", "backend"],
            "mobile-ios": ["*.xcodeproj", "*.xcworkspace", "Podfile", "Package.swift"],
            "mobile-android": ["build.gradle", "app/src/main/java", "AndroidManifest.xml"],
            "library": ["setup.py", "Cargo.toml", "go.mod", "pom.xml"],
            "cli-tool": ["bin/", "cmd/", "cli.py", "main.rs"],
        }

        scores = {ptype: 0 for ptype in indicators}

        for ptype, patterns in indicators.items():
            for pattern in patterns:
                if self._file_exists_pattern(pattern):
                    scores[ptype] += 1

        # Return type with highest score, default to "general"
        max_score = max(scores.values())
        if max_score == 0:
            return "general"

        return max(scores, key=scores.get)

    def _detect_tech_stack(self) -> Dict[str, List[str]]:
        """Detect languages, frameworks, and libraries"""
        stack = {
            "languages": [],
            "frameworks": [],
            "libraries": [],
            "runtime": []
        }

        # Check package.json for Node.js projects
        pkg_json = self._read_json("package.json")
        if pkg_json:
            deps = {**pkg_json.get("dependencies", {}), **pkg_json.get("devDependencies", {})}

            # Detect frameworks
            if "react" in deps:
                stack["frameworks"].append(f"React {deps['react'].strip('^~')}")
            if "vue" in deps:
                stack["frameworks"].append(f"Vue {deps['vue'].strip('^~')}")
            if "next" in deps:
                stack["frameworks"].append(f"Next.js {deps['next'].strip('^~')}")
            if "express" in deps:
                stack["frameworks"].append(f"Express {deps['express'].strip('^~')}")
            if "@nestjs/core" in deps:
                stack["frameworks"].append("NestJS")

            # Detect key libraries
            if "typescript" in deps:
                stack["languages"].append("TypeScript")
            else:
                stack["languages"].append("JavaScript")

            if "tailwindcss" in deps:
                stack["libraries"].append("Tailwind CSS")
            if "axios" in deps:
                stack["libraries"].append("Axios")

            stack["runtime"].append(f"Node.js")

        # Check for Python
        if self._file_exists("requirements.txt") or self._file_exists("pyproject.toml"):
            stack["languages"].append("Python")

            requirements = self._read_file("requirements.txt")
            if requirements:
                if "django" in requirements.lower():
                    stack["frameworks"].append("Django")
                if "flask" in requirements.lower():
                    stack["frameworks"].append("Flask")
                if "fastapi" in requirements.lower():
                    stack["frameworks"].append("FastAPI")

        # Check for Go
        if self._file_exists("go.mod"):
            stack["languages"].append("Go")
            stack["runtime"].append("Go")

        # Check for Rust
        if self._file_exists("Cargo.toml"):
            stack["languages"].append("Rust")
            cargo = self._read_file("Cargo.toml")
            if cargo and "actix-web" in cargo:
                stack["frameworks"].append("Actix Web")

        # Check for Java
        if self._file_exists("pom.xml") or self._file_exists("build.gradle"):
            stack["languages"].append("Java")
            if self._file_exists_pattern("**/spring"):
                stack["frameworks"].append("Spring Boot")

        return stack

    def _detect_tools(self) -> Dict[str, Any]:
        """Detect development tools and configurations"""
        tools = {
            "version_control": None,
            "package_manager": None,
            "build_tool": None,
            "linter": [],
            "formatter": [],
            "testing": [],
            "ci_cd": []
        }

        # Version control
        if self._file_exists(".git"):
            tools["version_control"] = "Git"

        # Package managers
        if self._file_exists("package-lock.json"):
            tools["package_manager"] = "npm"
        elif self._file_exists("yarn.lock"):
            tools["package_manager"] = "yarn"
        elif self._file_exists("pnpm-lock.yaml"):
            tools["package_manager"] = "pnpm"
        elif self._file_exists("Pipfile"):
            tools["package_manager"] = "pipenv"
        elif self._file_exists("poetry.lock"):
            tools["package_manager"] = "poetry"

        # Build tools
        if self._file_exists("vite.config.js") or self._file_exists("vite.config.ts"):
            tools["build_tool"] = "Vite"
        elif self._file_exists("webpack.config.js"):
            tools["build_tool"] = "Webpack"
        elif self._file_exists("rollup.config.js"):
            tools["build_tool"] = "Rollup"

        # Linters
        if self._file_exists(".eslintrc.js") or self._file_exists(".eslintrc.json"):
            tools["linter"].append("ESLint")
        if self._file_exists("pylint.rc") or self._file_exists(".pylintrc"):
            tools["linter"].append("Pylint")

        # Formatters
        if self._file_exists(".prettierrc") or self._file_exists("prettier.config.js"):
            tools["formatter"].append("Prettier")
        if self._file_exists(".editorconfig"):
            tools["formatter"].append("EditorConfig")

        # Testing
        pkg_json = self._read_json("package.json")
        if pkg_json:
            deps = {**pkg_json.get("dependencies", {}), **pkg_json.get("devDependencies", {})}
            if "vitest" in deps:
                tools["testing"].append("Vitest")
            elif "jest" in deps:
                tools["testing"].append("Jest")
            if "playwright" in deps:
                tools["testing"].append("Playwright")
            if "cypress" in deps:
                tools["testing"].append("Cypress")

        # CI/CD
        if self._file_exists(".github/workflows"):
            tools["ci_cd"].append("GitHub Actions")
        if self._file_exists(".gitlab-ci.yml"):
            tools["ci_cd"].append("GitLab CI")
        if self._file_exists(".circleci/config.yml"):
            tools["ci_cd"].append("CircleCI")

        return tools

    def _detect_conventions(self) -> Dict[str, Any]:
        """Extract code conventions from config files"""
        conventions = {
            "naming": [],
            "imports": [],
            "formatting": {},
            "testing": []
        }

        # ESLint conventions
        eslint_config = self._read_json(".eslintrc.json") or self._read_js_config(".eslintrc.js")
        if eslint_config:
            rules = eslint_config.get("rules", {})
            if "camelcase" in rules:
                conventions["naming"].append("camelCase for variables")
            if "@typescript-eslint/naming-convention" in rules:
                conventions["naming"].append("TypeScript naming conventions enforced")

        # Prettier conventions
        prettier_config = self._read_json(".prettierrc") or self._read_js_config("prettier.config.js")
        if prettier_config:
            conventions["formatting"] = {
                "semi": prettier_config.get("semi", True),
                "singleQuote": prettier_config.get("singleQuote", False),
                "tabWidth": prettier_config.get("tabWidth", 2),
                "trailingComma": prettier_config.get("trailingComma", "es5")
            }

        # TypeScript path aliases
        tsconfig = self._read_json("tsconfig.json")
        if tsconfig:
            paths = tsconfig.get("compilerOptions", {}).get("paths", {})
            if "@/*" in paths:
                conventions["imports"].append("Use @ alias for absolute imports")

        return conventions

    def _analyze_structure(self) -> Dict[str, Any]:
        """Analyze directory structure"""
        structure = {
            "root_dirs": [],
            "key_files": [],
            "entry_points": []
        }

        # Get top-level directories
        try:
            for item in self.project_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    structure["root_dirs"].append(item.name)
        except PermissionError:
            pass

        # Identify key files
        key_patterns = ["README.md", "package.json", "tsconfig.json", "vite.config.ts",
                       "main.py", "app.py", "main.go", "Cargo.toml"]
        for pattern in key_patterns:
            if self._file_exists(pattern):
                structure["key_files"].append(pattern)

        # Find entry points
        entry_candidates = ["src/main.tsx", "src/main.ts", "src/index.tsx", "src/index.ts",
                          "index.js", "server.js", "app.js", "main.py", "main.go"]
        for candidate in entry_candidates:
            if self._file_exists(candidate):
                structure["entry_points"].append(candidate)

        return structure

    def create_knowledge_base(self, scan_result: Dict[str, Any]) -> None:
        """Create the .project-ai knowledge base structure"""
        print(f"\n📁 Creating knowledge base at: {self.knowledge_base_path}")

        # Create directory structure
        (self.knowledge_base_path / "core").mkdir(parents=True, exist_ok=True)
        (self.knowledge_base_path / "indexed").mkdir(parents=True, exist_ok=True)
        (self.knowledge_base_path / "history" / "bugs").mkdir(parents=True, exist_ok=True)
        (self.knowledge_base_path / "history" / "requirements").mkdir(parents=True, exist_ok=True)
        (self.knowledge_base_path / "history" / "decisions").mkdir(parents=True, exist_ok=True)

        # Write core profile
        profile = {
            "project_name": self.project_path.name,
            "project_type": scan_result["project_type"],
            "scanned_at": scan_result["scanned_at"],
            "last_updated": scan_result["scanned_at"]
        }
        self._write_json(self.knowledge_base_path / "core" / "profile.json", profile)

        # Write tech stack
        self._write_json(self.knowledge_base_path / "core" / "tech-stack.json", scan_result["tech_stack"])

        # Write conventions
        self._write_json(self.knowledge_base_path / "core" / "conventions.json", scan_result["conventions"])

        # Write tools
        self._write_json(self.knowledge_base_path / "indexed" / "tools.json", scan_result["tools"])

        # Write structure
        self._write_json(self.knowledge_base_path / "indexed" / "structure.json", scan_result["structure"])

        # Create README
        readme_content = f"""# Project Guardian Knowledge Base

This directory contains auto-generated project knowledge maintained by Project Guardian.

**Last Updated**: {scan_result['scanned_at']}

## Structure

- `core/` - Always loaded context (<2k tokens)
- `indexed/` - Loaded on demand
- `history/` - Searchable historical records

## Usage

This knowledge base is automatically updated by Project Guardian.
Do not manually edit these files unless you know what you're doing.
"""
        (self.knowledge_base_path / "README.md").write_text(readme_content)

        print("✅ Knowledge base created successfully")

    # Helper methods
    def _file_exists(self, path: str) -> bool:
        return (self.project_path / path).exists()

    def _file_exists_pattern(self, pattern: str) -> bool:
        """Check if any file matching pattern exists"""
        try:
            matches = list(self.project_path.glob(pattern))
            return len(matches) > 0
        except:
            return False

    def _read_file(self, path: str) -> Optional[str]:
        try:
            return (self.project_path / path).read_text()
        except:
            return None

    def _read_json(self, path: str) -> Optional[Dict]:
        try:
            content = (self.project_path / path).read_text()
            return json.loads(content)
        except:
            return None

    def _read_js_config(self, path: str) -> Optional[Dict]:
        """Attempt to extract config from JS file (basic parsing)"""
        content = self._read_file(path)
        if not content:
            return None

        # Very basic extraction - look for module.exports = {...}
        try:
            match = re.search(r'module\.exports\s*=\s*({[\s\S]*})', content)
            if match:
                # This is a hack - would need proper JS parser for production
                return {}
        except:
            pass
        return None

    def _write_json(self, path: Path, data: Any) -> None:
        path.write_text(json.dumps(data, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_project.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]

    if not os.path.isdir(project_path):
        print(f"❌ Error: {project_path} is not a valid directory")
        sys.exit(1)

    scanner = ProjectScanner(project_path)

    # Run scan
    result = scanner.scan()

    # Display results
    print("\n" + "="*60)
    print("📊 SCAN RESULTS")
    print("="*60)
    print(f"\n🏷️  Project Type: {result['project_type']}")
    print(f"\n💻 Tech Stack:")
    for category, items in result['tech_stack'].items():
        if items:
            print(f"  {category}: {', '.join(items)}")

    print(f"\n🛠️  Tools:")
    for tool_type, value in result['tools'].items():
        if value:
            if isinstance(value, list):
                print(f"  {tool_type}: {', '.join(value)}")
            else:
                print(f"  {tool_type}: {value}")

    print(f"\n📐 Conventions:")
    for conv_type, value in result['conventions'].items():
        if value:
            print(f"  {conv_type}: {value}")

    print(f"\n📂 Structure:")
    print(f"  Root dirs: {', '.join(result['structure']['root_dirs'][:5])}")
    print(f"  Entry points: {', '.join(result['structure']['entry_points'])}")

    # Ask for confirmation
    print("\n" + "="*60)
    response = input("\n✅ Create knowledge base with these settings? (y/n): ")

    if response.lower() == 'y':
        scanner.create_knowledge_base(result)
        print(f"\n🎉 Project Guardian initialized successfully!")
        print(f"📁 Knowledge base location: {scanner.knowledge_base_path}")

        # Record initial version
        try:
            from pathlib import Path
            import sys
            version_tracker_path = Path(__file__).parent / "version_tracker.py"
            if version_tracker_path.exists():
                import subprocess
                subprocess.run([
                    sys.executable,
                    str(version_tracker_path),
                    project_path,
                    "--record",
                    "initial_scan"
                ], check=False)
                print("📌 Version recorded")
        except Exception:
            pass  # Version tracking is optional
    else:
        print("\n❌ Cancelled. No files were created.")


if __name__ == "__main__":
    main()

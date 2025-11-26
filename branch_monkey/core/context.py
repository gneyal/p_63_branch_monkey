"""Context Library - Maintains repository context for AI assistants."""

import os
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass


CONTEXT_DIR = ".branch_monkey"
CODEBASE_FILE = "codebase_summary.md"
ARCHITECTURE_FILE = "architecture_summary.md"
PROMPTS_FILE = "prompts_summary.md"


@dataclass
class ContextSummary:
    """Summary of a context file."""
    file_name: str
    last_updated: Optional[datetime]
    exists: bool
    size_bytes: int
    preview: str


class ContextLibrary:
    """
    Manages the .branch_monkey context directory in a repository.

    This creates and maintains three summary files:
    - codebase_summary.md: File structure and key components
    - architecture_summary.md: Architecture overview
    - prompts_summary.md: Summary of prompts used with AI assistants
    """

    def __init__(self, repo_path: Path):
        """
        Initialize the context library.

        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = repo_path
        self.context_dir = repo_path / CONTEXT_DIR

    def ensure_context_dir(self) -> Path:
        """Create the .branch_monkey directory if it doesn't exist."""
        self.context_dir.mkdir(exist_ok=True)

        # Add .gitignore to keep context local by default
        gitignore_path = self.context_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text("# Keep context files local by default\n*\n!.gitignore\n")

        return self.context_dir

    def get_context_path(self, file_name: str) -> Path:
        """Get full path to a context file."""
        return self.context_dir / file_name

    def read_context(self, file_name: str) -> Optional[str]:
        """Read content of a context file."""
        path = self.get_context_path(file_name)
        if path.exists():
            return path.read_text()
        return None

    def write_context(self, file_name: str, content: str) -> Path:
        """Write content to a context file."""
        self.ensure_context_dir()
        path = self.get_context_path(file_name)
        path.write_text(content)
        return path

    def get_status(self) -> Dict[str, ContextSummary]:
        """Get status of all context files."""
        files = [CODEBASE_FILE, ARCHITECTURE_FILE, PROMPTS_FILE]
        status = {}

        for file_name in files:
            path = self.get_context_path(file_name)
            if path.exists():
                stat = path.stat()
                content = path.read_text()
                preview = content[:200] + "..." if len(content) > 200 else content
                status[file_name] = ContextSummary(
                    file_name=file_name,
                    last_updated=datetime.fromtimestamp(stat.st_mtime),
                    exists=True,
                    size_bytes=stat.st_size,
                    preview=preview.split('\n')[0]  # First line only
                )
            else:
                status[file_name] = ContextSummary(
                    file_name=file_name,
                    last_updated=None,
                    exists=False,
                    size_bytes=0,
                    preview=""
                )

        return status

    def generate_codebase_summary(self) -> str:
        """
        Generate a codebase summary.

        This analyzes the repository structure and creates a summary
        of files, directories, and key components.
        """
        lines = [
            f"# Codebase Summary",
            f"",
            f"**Repository:** {self.repo_path.name}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"## File Structure",
            f"",
        ]

        # Collect file stats
        file_count = 0
        dir_count = 0
        extensions: Dict[str, int] = {}
        key_files: List[str] = []

        # Files to look for as "key files"
        key_file_names = {
            'readme.md', 'readme', 'readme.txt',
            'package.json', 'pyproject.toml', 'setup.py', 'cargo.toml',
            'makefile', 'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            'requirements.txt', 'go.mod', 'pom.xml', 'build.gradle',
            '.env.example', 'config.yaml', 'config.json',
        }

        # Directories to skip
        skip_dirs = {
            '.git', 'node_modules', '__pycache__', '.venv', 'venv',
            'env', '.env', 'dist', 'build', '.cache', '.branch_monkey',
            'target', 'vendor', '.idea', '.vscode'
        }

        for root, dirs, files in os.walk(self.repo_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            rel_root = Path(root).relative_to(self.repo_path)

            for d in dirs:
                dir_count += 1

            for f in files:
                file_count += 1
                ext = Path(f).suffix.lower() or '(no extension)'
                extensions[ext] = extensions.get(ext, 0) + 1

                # Check for key files
                if f.lower() in key_file_names:
                    rel_path = rel_root / f if str(rel_root) != '.' else Path(f)
                    key_files.append(str(rel_path))

        lines.append(f"- **Total Files:** {file_count}")
        lines.append(f"- **Total Directories:** {dir_count}")
        lines.append(f"")

        # Top extensions
        lines.append(f"## File Types")
        lines.append(f"")
        sorted_exts = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]
        for ext, count in sorted_exts:
            lines.append(f"- `{ext}`: {count} files")
        lines.append(f"")

        # Key files found
        if key_files:
            lines.append(f"## Key Files")
            lines.append(f"")
            for kf in sorted(key_files):
                lines.append(f"- `{kf}`")
            lines.append(f"")

        # Directory structure (top level)
        lines.append(f"## Top-Level Structure")
        lines.append(f"")
        lines.append("```")
        for item in sorted(self.repo_path.iterdir()):
            if item.name not in skip_dirs and not item.name.startswith('.'):
                if item.is_dir():
                    lines.append(f"{item.name}/")
                else:
                    lines.append(f"{item.name}")
        lines.append("```")
        lines.append(f"")

        return "\n".join(lines)

    def generate_architecture_summary(self) -> str:
        """
        Generate an architecture summary.

        This attempts to identify the project type, main components,
        and architectural patterns used.
        """
        lines = [
            f"# Architecture Summary",
            f"",
            f"**Repository:** {self.repo_path.name}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
        ]

        # Detect project type
        project_types = []

        if (self.repo_path / "package.json").exists():
            project_types.append("Node.js/JavaScript")
            # Check for frameworks
            try:
                import json
                pkg = json.loads((self.repo_path / "package.json").read_text())
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                if 'react' in deps:
                    project_types.append("React")
                if 'vue' in deps:
                    project_types.append("Vue.js")
                if 'svelte' in deps:
                    project_types.append("Svelte")
                if 'next' in deps:
                    project_types.append("Next.js")
                if 'express' in deps:
                    project_types.append("Express.js")
            except:
                pass

        if (self.repo_path / "pyproject.toml").exists() or (self.repo_path / "setup.py").exists():
            project_types.append("Python")
            # Check for frameworks
            if (self.repo_path / "requirements.txt").exists():
                try:
                    reqs = (self.repo_path / "requirements.txt").read_text().lower()
                    if 'django' in reqs:
                        project_types.append("Django")
                    if 'flask' in reqs:
                        project_types.append("Flask")
                    if 'fastapi' in reqs:
                        project_types.append("FastAPI")
                except:
                    pass

        if (self.repo_path / "Cargo.toml").exists():
            project_types.append("Rust")

        if (self.repo_path / "go.mod").exists():
            project_types.append("Go")

        if (self.repo_path / "pom.xml").exists() or (self.repo_path / "build.gradle").exists():
            project_types.append("Java")

        lines.append(f"## Project Type")
        lines.append(f"")
        if project_types:
            lines.append(f"- {', '.join(project_types)}")
        else:
            lines.append(f"- Unknown (no standard project files detected)")
        lines.append(f"")

        # Detect common patterns
        lines.append(f"## Detected Patterns")
        lines.append(f"")

        patterns = []

        # Check for common directory patterns
        dirs = [d.name for d in self.repo_path.iterdir() if d.is_dir()]

        if 'src' in dirs:
            patterns.append("- `src/` directory (source code)")
        if 'lib' in dirs:
            patterns.append("- `lib/` directory (library code)")
        if 'test' in dirs or 'tests' in dirs or '__tests__' in dirs:
            patterns.append("- Test directory found")
        if 'docs' in dirs:
            patterns.append("- Documentation directory")
        if 'scripts' in dirs:
            patterns.append("- Scripts directory")
        if 'config' in dirs or 'configs' in dirs:
            patterns.append("- Configuration directory")
        if 'api' in dirs:
            patterns.append("- API directory")
        if 'frontend' in dirs:
            patterns.append("- Frontend directory (separate frontend)")
        if 'backend' in dirs:
            patterns.append("- Backend directory (separate backend)")
        if 'components' in dirs:
            patterns.append("- Components directory (component-based architecture)")
        if 'services' in dirs:
            patterns.append("- Services directory (service-oriented)")
        if 'models' in dirs:
            patterns.append("- Models directory (MVC/data models)")
        if 'controllers' in dirs:
            patterns.append("- Controllers directory (MVC pattern)")
        if 'views' in dirs:
            patterns.append("- Views directory (MVC pattern)")
        if 'routes' in dirs or 'routing' in dirs:
            patterns.append("- Routes directory")
        if 'middleware' in dirs:
            patterns.append("- Middleware directory")
        if 'utils' in dirs or 'helpers' in dirs:
            patterns.append("- Utilities/Helpers directory")

        if patterns:
            lines.extend(patterns)
        else:
            lines.append("- No common patterns detected")
        lines.append(f"")

        # Check for Docker
        if (self.repo_path / "Dockerfile").exists() or (self.repo_path / "docker-compose.yml").exists():
            lines.append(f"## Containerization")
            lines.append(f"")
            lines.append(f"- Docker configuration found")
            lines.append(f"")

        # Check for CI/CD
        ci_files = []
        if (self.repo_path / ".github" / "workflows").exists():
            ci_files.append("GitHub Actions")
        if (self.repo_path / ".gitlab-ci.yml").exists():
            ci_files.append("GitLab CI")
        if (self.repo_path / "Jenkinsfile").exists():
            ci_files.append("Jenkins")
        if (self.repo_path / ".circleci").exists():
            ci_files.append("CircleCI")
        if (self.repo_path / ".travis.yml").exists():
            ci_files.append("Travis CI")

        if ci_files:
            lines.append(f"## CI/CD")
            lines.append(f"")
            for ci in ci_files:
                lines.append(f"- {ci}")
            lines.append(f"")

        lines.append(f"## Notes")
        lines.append(f"")
        lines.append(f"_Add your architecture notes here..._")
        lines.append(f"")

        return "\n".join(lines)

    def generate_prompts_summary(self, prompts_db_path: Optional[Path] = None) -> str:
        """
        Generate a summary of prompts from the prompts database.

        Args:
            prompts_db_path: Path to the prompts SQLite database.
                           If None, uses ~/.branch_monkey/prompts.db
        """
        if prompts_db_path is None:
            prompts_db_path = Path.home() / ".branch_monkey" / "prompts.db"

        lines = [
            f"# Prompts Summary",
            f"",
            f"**Repository:** {self.repo_path.name}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
        ]

        if not prompts_db_path.exists():
            lines.append(f"_No prompts database found. Save prompts via the web UI to track them here._")
            return "\n".join(lines)

        try:
            conn = sqlite3.connect(prompts_db_path)
            cursor = conn.cursor()

            # Get prompts for this repo
            cursor.execute(
                """
                SELECT sha, prompt, timestamp
                FROM prompts
                WHERE repo_path = ?
                ORDER BY timestamp DESC
                """,
                (str(self.repo_path.resolve()),)
            )
            results = cursor.fetchall()
            conn.close()

            if not results:
                lines.append(f"_No prompts saved for this repository yet._")
                return "\n".join(lines)

            lines.append(f"**Total Prompts:** {len(results)}")
            lines.append(f"")
            lines.append(f"## Recent Prompts")
            lines.append(f"")

            for sha, prompt, timestamp in results[:20]:  # Show last 20
                lines.append(f"### Commit `{sha[:7]}`")
                lines.append(f"")
                lines.append(f"**Saved:** {timestamp}")
                lines.append(f"")
                # Truncate long prompts
                if len(prompt) > 500:
                    lines.append(f"```")
                    lines.append(prompt[:500] + "...")
                    lines.append(f"```")
                else:
                    lines.append(f"```")
                    lines.append(prompt)
                    lines.append(f"```")
                lines.append(f"")

            if len(results) > 20:
                lines.append(f"_... and {len(results) - 20} more prompts_")

        except Exception as e:
            lines.append(f"_Error reading prompts database: {e}_")

        return "\n".join(lines)

    def update_all(self, prompts_db_path: Optional[Path] = None) -> Dict[str, str]:
        """
        Update all context files.

        Args:
            prompts_db_path: Optional path to prompts database

        Returns:
            Dictionary mapping file names to their new content
        """
        results = {}

        # Generate and save codebase summary
        codebase = self.generate_codebase_summary()
        self.write_context(CODEBASE_FILE, codebase)
        results[CODEBASE_FILE] = codebase

        # Generate and save architecture summary
        architecture = self.generate_architecture_summary()
        self.write_context(ARCHITECTURE_FILE, architecture)
        results[ARCHITECTURE_FILE] = architecture

        # Generate and save prompts summary
        prompts = self.generate_prompts_summary(prompts_db_path)
        self.write_context(PROMPTS_FILE, prompts)
        results[PROMPTS_FILE] = prompts

        return results

    def update_codebase(self) -> str:
        """Update just the codebase summary."""
        content = self.generate_codebase_summary()
        self.write_context(CODEBASE_FILE, content)
        return content

    def update_architecture(self) -> str:
        """Update just the architecture summary."""
        content = self.generate_architecture_summary()
        self.write_context(ARCHITECTURE_FILE, content)
        return content

    def update_prompts(self, prompts_db_path: Optional[Path] = None) -> str:
        """Update just the prompts summary."""
        content = self.generate_prompts_summary(prompts_db_path)
        self.write_context(PROMPTS_FILE, content)
        return content

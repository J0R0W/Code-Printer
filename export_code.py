#!/usr/bin/env python3
import os
import sys
import argparse
import fnmatch
import json

# optional YAML support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# File extensions for media (images, videos) to skip
MEDIA_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'ico',
    'mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv', 'webm'
}


def load_gitignore(root_path):
    """Loads patterns from .gitignore in the root directory."""
    patterns = []
    gitignore_path = os.path.join(root_path, '.gitignore')
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                patterns.append(line)
    patterns.append('.git/')  # always ignore .git
    return patterns


def should_skip_tree(name, rel_path, patterns, include_hidden):
    """Skip hidden, gitignored, or media files/directories when building the tree."""
    # Hidden
    if not include_hidden and name.startswith('.'):
        return True
    # Gitignore
    if any(fnmatch.fnmatch(rel_path, pat) for pat in patterns):
        return True
    # Media files
    ext = os.path.splitext(name)[1].lower().lstrip('.')
    if ext in MEDIA_EXTENSIONS:
        return True
    return False


def should_skip_content(name, rel_path, ignore_exts, include_pats, exclude_pats):
    """Skip files when reading contents based on ext-ignores and include/exclude patterns."""
    ext = os.path.splitext(name)[1].lower().lstrip('.')
    # Ignored extensions
    if ext in ignore_exts:
        return True
    # Include patterns
    if include_pats and not any(fnmatch.fnmatch(rel_path, pat) for pat in include_pats):
        return True
    # Exclude patterns
    if exclude_pats and any(fnmatch.fnmatch(rel_path, pat) for pat in exclude_pats):
        return True
    return False


def scan(root_path, patterns, include_hidden, ignore_exts, include_pats, exclude_pats, max_depth):
    """Scans directory and returns a tree and contents dict."""
    contents = {}

    def _scan(current_path, rel_base, depth):
        if max_depth is not None and depth > max_depth:
            return []
        entries = []
        try:
            names = sorted(os.listdir(current_path))
        except PermissionError:
            return entries
        for name in names:
            full = os.path.join(current_path, name)
            rel = os.path.join(rel_base, name) if rel_base else name
            is_dir = os.path.isdir(full)
            # Skip for tree building
            if should_skip_tree(name, rel, patterns, include_hidden):
                continue
            if is_dir:
                children = _scan(full, rel, depth + 1)
                entries.append({'type': 'dir', 'name': name, 'children': children})
            else:
                entries.append({'type': 'file', 'name': name, 'path': rel})
                # Only read content if not excluded
                if not should_skip_content(name, rel, ignore_exts, include_pats, exclude_pats):
                    try:
                        with open(full, 'r', encoding='utf-8') as f:
                            contents[rel] = f.read()
                    except Exception:
                        contents[rel] = None
        return entries

    tree = _scan(root_path, '', 0)
    return tree, contents


def render_text(tree, contents, out):
    """Renders in plain text format."""
    def _print_tree(entries, indent):
        for e in entries:
            if e['type'] == 'dir':
                out.write(f"{indent}{e['name']}/\n")
                _print_tree(e['children'], indent + '    ')
            else:
                out.write(f"{indent}{e['name']}\n")
    out.write("Directory structure:\n")
    _print_tree(tree, '')
    out.write("\nFile contents:\n")
    for path, content in contents.items():
        out.write(f"\n=== {path} ===\n```")
        if content is not None:
            out.write(content)
        else:
            out.write("[Binary or unreadable file: skipped]\n")
        out.write("```\n")


def render_markdown(tree, contents, out):
    """Renders in GitHub-flavored Markdown."""
    def _md_tree(entries, indent):
        for e in entries:
            if e['type'] == 'dir':
                out.write(f"{indent}- **{e['name']}/**\n")
                _md_tree(e['children'], indent + '  ')
            else:
                out.write(f"{indent}- `{e['name']}`\n")
    out.write("## Directory structure\n")
    _md_tree(tree, '')
    out.write("\n## File contents\n")
    for path, content in contents.items():
        out.write(f"#### {path}\n```")
        if content is not None:
            out.write(content)
        else:
            out.write("[Binary or unreadable file: skipped]\n")
        out.write("```\n")


def main():
    parser = argparse.ArgumentParser(
        description="Export directory structure and file contents with flexible filtering and output formats.")
    parser.add_argument('root', help='Path to the directory to export')
    parser.add_argument('-o', '--output', help='Path to the output file')
    parser.add_argument('--hidden', '-H', action='store_true', default=False,
                        help='Include hidden files/folders')
    parser.add_argument('--ignore-ext', '-e', nargs='+', default=[],
                        help='File extensions (no dot) to ignore, e.g. html json')
    parser.add_argument('--include', '-i', nargs='+', default=[],
                        help='Glob patterns to include files, e.g. "*.py"')
    parser.add_argument('--exclude', '-x', nargs='+', default=[],
                        help='Glob patterns to exclude files, e.g. "tests/*"')
    parser.add_argument('--max-depth', type=int, default=None,
                        help='Maximum directory depth (0 = root only)')
    parser.add_argument('-f', '--format', choices=['text', 'json', 'yaml', 'markdown'],
                        default='text', help='Output format')
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        print(f"Error: Path '{args.root}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    patterns = load_gitignore(args.root)
    ignore_exts = set(ext.lower() for ext in args.ignore_ext)
    include_pats = args.include
    exclude_pats = args.exclude

    tree, contents = scan(
        args.root, patterns, args.hidden,
        ignore_exts, include_pats, exclude_pats,
        args.max_depth
    )

    out = open(args.output, 'w', encoding='utf-8') if args.output else sys.stdout

    if args.format == 'text':
        render_text(tree, contents, out)
    elif args.format == 'markdown':
        render_markdown(tree, contents, out)
    elif args.format == 'json':
        json.dump({'structure': tree, 'contents': contents}, out, indent=2)
    elif args.format == 'yaml':
        if not YAML_AVAILABLE:
            print("Error: PyYAML not installed; YAML format unavailable.", file=sys.stderr)
            sys.exit(1)
        yaml.dump({'structure': tree, 'contents': contents}, out)

    if args.output:
        out.close()

if __name__ == '__main__':
    main()

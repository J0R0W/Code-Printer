#!/usr/bin/env python3
import os
import sys
import argparse
import fnmatch

# Dateiendungen für Medien (Bilder, Videos) zum Überspringen
MEDIA_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'ico',
    'mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv', 'webm'
}


def load_gitignore(root_path):
    """Lädt Patterns aus .gitignore im Wurzelverzeichnis."""
    patterns = []
    gitignore_path = os.path.join(root_path, '.gitignore')
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                patterns.append(line)
    # Standardmäßig .git Verzeichnis ignorieren
    patterns.append('.git/')
    return patterns


def is_ignored(path, patterns):
    """Prüft, ob ein Pfad (relativ zum Root) einem Gitignore-Pattern entspricht."""
    for pat in patterns:
        if pat.endswith('/'):
            if path.startswith(pat.rstrip('/')):
                return True
        if fnmatch.fnmatch(path, pat):
            return True
    return False


def is_media_file(filename):
    """Überprüft anhand der Dateiendung, ob es sich um eine Mediendatei handelt."""
    ext = filename.lower().rsplit('.', 1)[-1]
    return ext in MEDIA_EXTENSIONS


def is_hidden(name):
    """Prüft, ob ein Datei- oder Verzeichnisname mit einem Punkt beginnt."""
    return name.startswith('.')


def print_tree(root_path, out, patterns, include_hidden, ignore_exts):
    """Gibt die Verzeichnisstruktur aus, filtert Mediendateien, Git-ignorierte, versteckte Dateien und ignorierte Endungen."""
    for dirpath, dirnames, filenames in os.walk(root_path):
        rel_dir = os.path.relpath(dirpath, root_path)
        # Hidden und Git-ignored Verzeichnisse filtern
        dirnames[:] = [d for d in dirnames
                       if (include_hidden or not is_hidden(d))
                       and not is_ignored(os.path.join(rel_dir, d), patterns)]
        depth = 0 if rel_dir == '.' else rel_dir.count(os.sep)
        indent = '    ' * depth
        dir_name = os.path.basename(dirpath) if rel_dir != '.' else os.path.basename(root_path)
        out.write(f"{indent}{dir_name}/\n")
        for fname in sorted(filenames):
            rel_file = os.path.join(rel_dir, fname)
            ext = fname.lower().rsplit('.', 1)[-1] if '.' in fname else ''
            if (is_media_file(fname) or
                is_ignored(rel_file, patterns) or
                (not include_hidden and is_hidden(fname)) or
                ext in ignore_exts):
                continue
            out.write(f"{indent}    {fname}\n")


def print_contents(root_path, out, patterns, include_hidden, ignore_exts):
    """Gibt den Inhalt jeder Nicht-Mediendatei mit Kopfzeile und Code-Fence aus, filtert versteckte, ignorierte Pfade und Endungen."""
    for dirpath, dirnames, filenames in os.walk(root_path):
        rel_dir = os.path.relpath(dirpath, root_path)
        dirnames[:] = [d for d in dirnames
                       if (include_hidden or not is_hidden(d))
                       and not is_ignored(os.path.join(rel_dir, d), patterns)]
        for fname in sorted(filenames):
            rel_file = os.path.join(rel_dir, fname)
            ext = fname.lower().rsplit('.', 1)[-1] if '.' in fname else ''
            if (is_media_file(fname) or
                is_ignored(rel_file, patterns) or
                (not include_hidden and is_hidden(fname)) or
                ext in ignore_exts):
                continue
            file_path = os.path.join(dirpath, fname)
            out.write(f"\n=== {rel_file} ===\n")
            out.write("```\n")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    out.write(f.read())
            except UnicodeDecodeError:
                out.write("[Binary file: übersprungen]\n")
            out.write("```\n")


def main():
    parser = argparse.ArgumentParser(
        description="Exportiere Verzeichnisstruktur und Dateiinhalte ohne Mediendateien, Git-ignorierte, versteckte Dateien oder bestimmte Endungen.")
    parser.add_argument('root', help='Pfad zum Verzeichnis, das exportiert werden soll')
    parser.add_argument('-o', '--output', help='Pfad zur Ausgabedatei.')
    parser.add_argument('--hidden', '-H', action='store_true',
                        help='Versteckte Dateien/Ordner einbeziehen (Standard: aus)', default=False)
    parser.add_argument('--ignore-ext', '-e', nargs='+', default=[],
                        help='Liste von Dateiendungen (ohne Punkt), die ignoriert werden sollen, z.B. html json')
    args = parser.parse_args()

    root = args.root
    if not os.path.exists(root):
        print(f"Fehler: Pfad '{root}' existiert nicht.", file=sys.stderr)
        sys.exit(1)

    patterns = load_gitignore(root)
    ignore_exts = set(ext.lower() for ext in args.ignore_ext)
    out = open(args.output, 'w', encoding='utf-8') if args.output else sys.stdout

    out.write("Verzeichnisstruktur:\n")
    print_tree(root, out, patterns, args.hidden, ignore_exts)
    out.write("\nDateiinhalte:\n")
    print_contents(root, out, patterns, args.hidden, ignore_exts)

    if args.output:
        out.close()

if __name__ == '__main__':
    main()

# Code-Printer

A simple and flexible command-line tool to export a clean snapshot of your codebase’s structure and content — perfect for sharing, reviewing, or feeding into large language models.

## Features

* Prints directory tree and file contents
* Skips media files (images, videos) by default
* Honors `.gitignore` rules and ignores the `.git` directory
* Excludes hidden files/folders by default (use `-H` to include)
* Allows custom exclusion of file extensions (e.g., `html`, `json`)
* Supports glob-based include/exclude filters
* Limits directory depth with a `--max-depth` option
* Multiple output formats: plain text, JSON, YAML (if PyYAML is installed), and Markdown
* Outputs to terminal or to a file via `--output`

## Usage

```bash
# Basic usage: prints to console
python3 export_code.py /path/to/project

# Write output to file
python3 export_code.py /path/to/project -o summary.txt

# Include hidden files and folders
python3 export_code.py /path/to/project -H

# Ignore specific extensions (without dot)
python3 export_code.py /path/to/project -e html json

# Include only Python files and depth-limit
python3 export_code.py /path/to/project -i "*.py" --max-depth 2

# Exclude tests directory and output Markdown
python3 export_code.py /path/to/project -x "tests/*" -f markdown -o tree.md

# Output JSON for programmatic use
python3 export_code.py /path/to/project -f json > structure.json
```

## Options

| Flag                 | Description                                                    |
| -------------------- | -------------------------------------------------------------- |
| `root`               | Path to the directory to export                                |
| `-o`, `--output`     | Path to the output file                                        |
| `-H`, `--hidden`     | Include hidden files/folders (default: off)                    |
| `-e`, `--ignore-ext` | List of file extensions (without dot) to ignore, e.g., `html`  |
| `-i`, `--include`    | Glob patterns to include only matching files, e.g., `"*.py"`   |
| `-x`, `--exclude`    | Glob patterns to exclude matching files, e.g., `"tests/*"`     |
| `--max-depth`        | Maximum directory depth to traverse (0 = root only)            |
| `-f`, `--format`     | Output format: `text` (default), `json`, `yaml`, or `markdown` |
| `-h`, `--help`       | Show help message and exit                                     |

## Contributing

Feel free to open issues or submit pull requests for new features, bug fixes, or improvements. Please include tests and update documentation accordingly.


## License

MIT © J0R0W

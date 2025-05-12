# Code-Printer

A simple and flexible command-line tool to export a clean snapshot of your codebase’s structure and content — perfect for sharing, reviewing, or feeding into large language models.

## Features

* Prints directory tree and file contents
* Skips media files (images, videos) by default
* Honors `.gitignore` rules and ignores the `.git` directory
* Excludes hidden files/folders by default (use `-H` to include)
* Allows custom exclusion of file extensions (e.g., `html`, `json`)
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

# Combine flags
python3 export_code.py /path/to/project -o summary.txt -H -e html json
```

## Options

| Flag                 | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| `root`               | Path to the directory to export                              |
| `-o`, `--output`     | Path to the output file                                      |
| `-H`, `--hidden`     | Include hidden files/folders (default: false)                |
| `-e`, `--ignore-ext` | List of file extensions (without dot) to ignore (e.g., html) |
| `-h`, `--help`       | Show help message and exit                                   |

## Contributing

Feel free to open issues or submit pull requests for new features, bug fixes, or improvements.

## License

MIT © J0R0W

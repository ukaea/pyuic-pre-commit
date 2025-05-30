# pyuic-pre-commit

A [pre-commit](https://pre-commit.com/) hook to run PyQt/PySide's `pyuic` tool
and ensure generated Python files are up-to-date with their `.ui` files.

Supports Python versions 3.9 - 3.13.

## Usage

Add the following to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/ukaea/pyuic-pre-commit.git
    rev: v0.2.0
    hooks:
      - id: check-ui-files
        args: ['--exe-name', 'pyside6-uic', '--pattern', 'ui_{}.py']  # optional
```

You **must** have a `pyuic` tool available and on your path.
The default `pyuic` tool is `pyside6-uic`,
but this can be set using the `--exe-name` argument shown above.
For example, if you're using PyQt5:

```yaml
        args: ['--exe-name', 'pyuic5']
```

### File Matching Patterns

By default, this hook will look for generated Python files
using the pattern `ui_{}.py`,
where `{}` is replaced with the stem of the `.ui` file's name.
For example, given some `.ui` file `src/mygui/mainwindow.ui`,
the hook will look for a generated python file `src/mygui/ui_mainwindow.py`.

You can change the pattern used by passing
`--pattern <mypattern>` into the hook's config.
The pattern may be a relative path,
but it must contain exactly one '`{}`'.
For example, suppose you have a `.ui` file `src/mygui/ui/mainwindow.ui`,
and a corresponding `uic` generated Python file `src/mygui/mainwindow.py`,
you would use:

```yaml
        args: ['--pattern', '../{}.py']
```

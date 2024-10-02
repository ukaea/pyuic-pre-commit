# pyuic-pre-commit

A [pre-commit](https://pre-commit.com/) hook to run PyQt/PySide's `pyuic` tool
and ensure generated Python files are up-to-date with their `.ui` files.

Supports Python versions 3.8 - 3.12.

## Usage

Add the following to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/ukaea/pyuic-pre-commit.git
    rev: v0.1.1
    hooks:
      - id: check-ui-files
        args: ['--exe-name', 'pyside6-uic']  # optional
```

You **must** have a `pyuic` tool available and on your path.
The default `pyuic` tool is `pyside6-uic`,
but this can be set using the `--exe-name` argument shown above.
For example, if you're using PyQt5:

```yaml
        args: ['--exe-name', 'pyuic5']
```

## Assumptions

This hook assumes that each `.ui` and generated Python file pair are
located in the same directory and have a consistent naming pattern.
The generated Python file must have the same name as the `.ui` file
with a `ui_` prefix.

For example, the following is OK:

```text
module/widget.ui -> module/ui_widget.py
```

But these examples are not:

```text
module/ui/widget.ui -> module/ui_widget.py
module/widget.ui -> module/widget.py
```

> *Note:
> If you have requirements that are not supported by these assumptions,
> please let the hook authors know and they can try to help.*

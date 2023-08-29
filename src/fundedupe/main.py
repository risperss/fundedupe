import ast
from collections.abc import Generator
from pathlib import Path

import click
from black import FileMode, format_str
from simhash import Simhash, SimhashIndex


def get_function_defs(path: Path) -> list[ast.FunctionDef]:
    contents = path.read_bytes()
    return [
        ast_obj
        for ast_obj in ast.parse(contents).body
        if isinstance(ast_obj, ast.FunctionDef)
    ]


# TODO: investigate if there is benefit to converting spaces to tabs
def format_function(function_body: str) -> str:
    return format_str(function_body, mode=FileMode())


def get_formatted_function_sources(function_sources: list[str]) -> list[str]:
    return [format_function(function_source) for function_source in function_sources]


def get_simhashes(function_sources: list[str]) -> list[Simhash]:
    return [Simhash(source) for source in function_sources]


def compute_target_hashes(path: Path) -> Generator[int, None, None]:
    source_files = path.glob("**/*.py")
    functions = (
        (f"{str(source_file.parent)}::{function_def.name}", function_def)
        for source_file in source_files
        for function_def in get_function_defs(source_file)
    )
    # NOTE: I know there is a better way to do below, but it confuses my linter
    _ = (name for name, _ in functions)
    function_defs = (function_def for _, function_def in functions)
    function_sources = (ast.unparse(function_def) for function_def in function_defs)
    function_fingerprints = (Simhash(source) for source in function_sources)
    function_fingerprint_values = (
        fingerprint.value for fingerprint in function_fingerprints
    )

    return function_fingerprint_values


@click.command()
@click.option(
    "--target",
    default=".",
    help="path to search for duplicate function code",
)
def dedupe(target):
    path = Path(target)

    if not path.exists():
        click.echo(f"ERROR: invalid target {target}", err=True)
        return

    hashes = list(compute_target_hashes(path))
    print("Functions analyzed: ", len(hashes))


if __name__ == "__main__":
    dedupe()

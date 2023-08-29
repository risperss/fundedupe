import ast
import random
from collections.abc import Generator
from pathlib import Path

import click
from simhash import Simhash, SimhashIndex


def get_function_defs(path: Path) -> list[ast.FunctionDef]:
    contents = path.read_bytes()
    return [
        ast_obj
        for ast_obj in ast.parse(contents).body
        if isinstance(ast_obj, ast.FunctionDef)
    ]


def fingerprint_source_files(path: Path) -> Generator[tuple[str, Simhash], None, None]:
    source_files = path.glob("**/*.py")
    functions = (
        (f"{str(source_file)}::{function_def.name}", function_def)
        for source_file in source_files
        for function_def in get_function_defs(source_file)
    )
    # NOTE: I know there is a better way to do below, but it confuses my linter
    function_names = (name for name, _ in functions)
    function_defs = (function_def for _, function_def in functions)
    function_sources = (ast.unparse(function_def) for function_def in function_defs)
    function_fingerprints = (Simhash(source) for source in function_sources)
    simhash_index_objs = zip(function_names, function_fingerprints)

    return simhash_index_objs


def search_for_duplicates(
    simhash_index_objs: list[tuple[str, Simhash]], samples: int
) -> None:
    count = len(simhash_index_objs)

    for _ in range(samples):
        control = simhash_index_objs.pop(random.randint(0, count - 1))
        control_name, control_simhash = control

        simhash_index = SimhashIndex(simhash_index_objs, k=3)
        near_dups = simhash_index.get_near_dups(control_simhash)

        print(f"Matching {control_name}")
        for dup in near_dups:
            print("\t", dup, sep="")
        print("\tNear dups: ", len(near_dups))
        print("\n\n")

        simhash_index_objs.insert(random.randint(0, count - 1), control)


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

    simhash_index_objs = list(fingerprint_source_files(path))
    search_for_duplicates(simhash_index_objs, 1)


if __name__ == "__main__":
    dedupe()

import ast
from pathlib import Path

from black import FileMode, format_str
from simhash import Simhash, SimhashIndex


def get_function_defs(path: Path) -> list[ast.FunctionDef]:
    contents = path.read_bytes()
    return [
        ast_obj
        for ast_obj in ast.parse(contents).body
        if isinstance(ast_obj, ast.FunctionDef)
    ]


def get_function_sources(function_defs: list[ast.FunctionDef]) -> list[str]:
    return [ast.unparse(function_def) for function_def in function_defs]


# TODO: investigate if there is benefit to converting spaces to tabs
def format_function(function_body: str) -> str:
    return format_str(function_body, mode=FileMode())


def get_formatted_function_sources(function_sources: list[str]) -> list[str]:
    return [format_function(function_source) for function_source in function_sources]


def get_simhashes(function_sources: list[str]) -> list[Simhash]:
    return [Simhash(source) for source in function_sources]


def main():
    test_file = Path("src/fundedupe/dummy.py")
    function_defs = get_function_defs(test_file)
    function_names = [d.name for d in function_defs]
    function_sources = get_function_sources(function_defs)
    formatted_function_sources = get_formatted_function_sources(function_sources)
    simhashes = get_simhashes(formatted_function_sources)

    control_name, control_simhash = function_names.pop(0), simhashes.pop(0)

    simhash_index_objs = list(zip(function_names, simhashes))
    simhash_index = SimhashIndex(simhash_index_objs, k=20)

    for x in simhashes:
        print(x, end="\n\n")

    print(control_name)
    print(simhash_index.get_near_dups(control_simhash))


if __name__ == "__main__":
    main()

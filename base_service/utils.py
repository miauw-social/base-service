import asyncio
import os


def run_async(func) -> None:
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(func)
    except:
        pass


def get_file_paths(folder_path: str, walk_sub_dirs=True):
    """get all files in dir"""
    file_paths: list[str] = []
    for root, directories, files in os.walk(folder_path):
        if not walk_sub_dirs and root != folder_path:
            break
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_paths.append(file_path)
    return file_paths


def build_statement_name_from_path(path: str) -> str:
    return path.replace("/", "_").rstrip(".sql")


def build_prepared_statement(file: str, statement: str):
    """builds a prepared statement based on filename and statement"""
    return f"prepare {build_statement_name_from_path(file)} as {statement}"

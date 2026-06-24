from pathlib import Path

import aiofiles


async def read_file(file_path: str | Path) -> str:
    """Read the contents of a file asynchronously."""
    async with aiofiles.open(file_path) as f:
        contents = await f.read()
    return contents

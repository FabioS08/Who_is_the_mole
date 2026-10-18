from pathlib import Path


def get_project_root() -> Path:

    '''
    It returns the absolute path to the project root directory.

    Outputs
    -------
     root:Path
      The root directory of this repository
    '''

    # src/BE/core/utils.py -> parents[0] = core 
    #                         parents[1] = BE 
    #                         parents[2] = src 
    #                         parents[3] = repo root
    return Path(__file__).resolve().parents[3]


def resolve_project_path(path: str | Path) -> Path:

    '''
    It resolves a path relative to the project root if it is not already an absolute path.

    Parameters
    ----------
     path:str|Path
      The path to resolve (absolute or relative to project root)

    Outputs
    -------
     resolved_path:Path
      The resolved absolute Path
    '''

    target = Path(path)

    if not target.is_absolute():
        return get_project_root() / target
    
    return target


def ensure_file_extension(filename: str | Path, extension: str) -> str:

    '''
    It ensures that a filename ends with the specified extension, appending it if absent.

    Parameters
    ----------
     filename:str|Path
      The input file path or base name

     extension:str
      The required file extension (with or without a leading dot, e.g. '.xlsx' or 'xlsx')

    Outputs
    -------
     resolved_filename:str
      The filename guaranteed to end with the specified extension
    '''

    ext = extension if extension.startswith(".") else f".{extension}"
    target = str(filename)

    if not target.endswith(ext):
        return f"{target}{ext}"

    return target
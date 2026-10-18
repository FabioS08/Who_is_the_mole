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
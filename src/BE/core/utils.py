from typing import Optional, Dict, Any
from datetime import datetime
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


def create_stats(following: Optional[list] = None, followers: Optional[list] = None, non_followers: Optional[list] = None, 
                 new_unfollowers: int | Any = 0) -> Dict[str, Any]:

    '''
    It compiles account metrics into a standardized summary statistics dictionary.

    Parameters
    ----------
     following:Optional[list]
      List of accounts the user follows (default: None)

     followers:Optional[list]
      List of accounts following the user (default: None)

     non_followers:Optional[list]
      List of accounts not following the user back (default: None)

     new_unfollowers:int | Any
      Count of new unfollowers or SnapshotManager/object with new_unfollowers_count attribute (default: 0)

    Outputs
    -------
     stats:Dict[str, Any]
      Summary statistics dictionary containing following, followers, non_followers, new_unfollowers, and timestamps
    '''

    new_unfollowers_count = getattr(new_unfollowers, 'new_unfollowers_count', new_unfollowers)
    now_str = datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")

    return {
                "following": len(following) if following is not None else "N/A",
                "followers": len(followers) if followers is not None else "N/A",
                "non_followers": len(non_followers) if non_followers is not None else 0,
                "new_unfollowers": new_unfollowers_count,
                "last_checked": now_str,
                "generated": now_str,
            }


def create_default_stats(data: Optional[list] = None) -> Dict[str, Any]:

    '''
    It generates a fallback summary statistics dictionary when full stats are not provided.

    Parameters
    ----------
     data:Optional[list]
      List of non-followers data dictionaries (default: None)

    Outputs
    -------
     stats:Dict[str, Any]
      Fallback summary statistics dictionary with N/A counts and current timestamp
    '''

    return create_stats(non_followers = data)


def is_web_url(url: Any) -> bool:

    '''
    It checks whether a given URL string is a web link starting with http:// or https://.

    Parameters
    ----------
     url:Any
      The URL or value to check

    Outputs
    -------
     is_valid:bool
      True if the URL begins with http:// or https://, False otherwise
    '''

    return bool(url) and str(url).startswith(("http://", "https://"))
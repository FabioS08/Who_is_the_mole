from rich.console import Console
from rich.table import Table

from typing import List, Dict


def export_to_terminal(data: List[Dict]) -> None:

    '''
    It renders and prints the non-followers report as a styled table in the terminal.

    Parameters
    ----------
     data:List[Dict]
      The list of dictionaries containing user details and unfollow dates

    Outputs
    -------
     None
    '''

    console = Console()
    
    table = Table(title = "😒 Non-Followers (People you follow who don't follow back)")
    table.add_column("Username", style = "cyan", no_wrap = True)
    table.add_column("Profile URL", style = "blue")
    table.add_column("Unfollow Date", style = "magenta")
    
    for item in data:
        table.add_row(
                        item.get('username', 'N/A'),
                        item.get('url', 'N/A'),
                        item.get('unfollow_date', 'N/A')
                    )
        
    console.print(table)
    console.print(f"\nTotal Non-Followers: {len(data)}", style="bold red")
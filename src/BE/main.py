from core.platforms import InstagramExportChecker, GithubApiChecker, SocialMediaChecker
from core.exporters import export_to_terminal, export_to_pdf, export_to_excel
from core.snapshots_manager import SnapshotManager
from core.utils import create_stats

from typing import Optional, Dict, Any

from rich.console import Console
from rich.align import Align
from rich.panel import Panel
import rich.box as box

import argparse


console = Console()


def create_parser() -> argparse.ArgumentParser:

    '''
    It creates the parser with the required arguments to use in the CLI.

    Parameters
    ----------
     None

    Outputs
    -------
     parser:argparse.ArgumentParser
      The created parser with all the parameters that can be used in the CLI
    '''

    parser = argparse.ArgumentParser(description = "Find who you follow that doesn't follow you back.")

    parser.add_argument("platform", choices = ["github", "instagram"], help = "Platform to analyze")
    parser.add_argument("--username", help = "Profile Username (required for github)")
    parser.add_argument("--path", help = "Path to the extracted data export (required for instagram)")
    parser.add_argument("--github-token", help = "Optional GitHub Personal Access Token to bypass rate limits")
    parser.add_argument("--output", choices = ["terminal", "pdf", "excel"], default = "terminal", help = "Output format")
    parser.add_argument("--file-name", "--filename", dest = "file_name", default = "non_followers_report", help = "Name of the output export file (without extension)")
    
    return parser


def setup_github_checker(args: argparse.Namespace) -> tuple[SocialMediaChecker | None, str | None]:

    '''
    Validates arguments, displays the status panel, and initializes
    the GitHub API checker.

    Parameters
    ----------
     args:argparse.Namespace
      Parsed CLI arguments

    Outputs
    -------
     tuple[SocialMediaChecker | None, str | None]
      The initialized GitHub checker and username, or (None, None) if validation fails
    '''

    if not args.username:
        console.print("[bold red]Error:[/] '--username' parameter is required for GitHub")
        return None, None

    console.print(Panel(renderable = Align.center(f"Fetching data from [cyan]GitHub[/cyan] for user [bold magenta]{args.username}[/bold magenta]..."),
                        box = box.SQUARE,
                        border_style = "cyan"))
    
    return GithubApiChecker(args.username, token=args.github_token), args.username


def setup_instagram_checker(args: argparse.Namespace) -> tuple[SocialMediaChecker | None, str | None]:

    '''
    It validates the arguments, displays the status panel and initializes the Instagram export checker.

    Parameters
    ----------
     args:argparse.Namespace
      Parsed CLI arguments

    Outputs
    -------
     tuple[SocialMediaChecker | None, str | None]
      The initialized Instagram checker and account identifier, or (None, None) if validation fails
    '''

    if not args.path:
        console.print("[bold red]Error:[/] '--path' parameter is required for Instagram (i.e. the path to the extracted zip folder)")
        return None, None

    console.print(Panel(renderable = Align.center(f"Parsing [cyan]Instagram[/cyan] data export at [bold magenta]{args.path}[/bold magenta]..."),
                        box = box.SQUARE,
                        border_style = "magenta"))
    
    return InstagramExportChecker(args.path), "local_export"


def init_checker(args: argparse.Namespace) -> tuple[SocialMediaChecker | None, str | None]:

    '''
    It initializes the appropriate social media checker based on the selected platform.

    Parameters
    ----------
     args:argparse.Namespace
      Parsed CLI arguments

    Outputs
    -------
     tuple[SocialMediaChecker | None, str | None]
      The initialized checker instance and associated account identifier or (None, None) if not 
      a recognized social.
    '''

    if args.platform == "github":
        return setup_github_checker(args)
    
    elif args.platform == "instagram":
        return setup_instagram_checker(args)

    return None, None



def export_results(args: argparse.Namespace, data: list[dict], stats: Optional[Dict[str, Any]] = None) -> None:

    '''
    It exports the non-followers report to the selected output format (terminal, PDF or Excel).

    Parameters
    ----------
     args:argparse.Namespace
      Parsed CLI arguments containing output format preferences

     data:list[dict]
      The enriched list of non-followers to export

     stats:Optional[Dict[str, Any]]
      Summary statistics dictionary containing following, followers, non_followers, new_unfollowers counts

    Outputs
    -------
     None
    '''

    if args.output == "terminal":
        export_to_terminal(data)

    elif args.output == "pdf":
        export_to_pdf(data, args.file_name, stats = stats)

    elif args.output == "excel":
        export_to_excel(data, args.file_name, stats = stats)


def main():
    
    parser = create_parser()
    args = parser.parse_args()
    
    checker, account_id = init_checker(args)
    
    if checker is None or account_id is None:
   
        console.print("[bold red] 🚨 Error:[/] Either the social media platform or the account is not valid.")
        return -1

    try:

        with console.status("[bold green]Analyzing followers & following data...", spinner = "dots"):
            
            followers = checker.get_followers()
            following = checker.get_following()
            non_followers = checker.get_non_followers()
   
    except Exception as e:
   
        console.print(f"[bold red]🚨 Error fetching data:[/] {e}")
        return -1

    # Process snapshots to add 'unfollow_date'
    snapshot_manager = SnapshotManager(args.platform, account_id)
    enriched_non_followers = snapshot_manager.process(followers, non_followers)
    stats = create_stats(following, followers, enriched_non_followers, snapshot_manager)

    export_results(args, enriched_non_followers, stats = stats)


if __name__ == "__main__":
    main()
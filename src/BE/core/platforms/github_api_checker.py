from .social_media_checker import SocialMediaChecker
from typing import List, Dict, Any, Optional
from ..utils import resolve_project_path
from rich.console import Console
from datetime import datetime
from pathlib import Path
import requests
import json

console = Console()


class GithubApiChecker(SocialMediaChecker):

    '''
    It interacts with the GitHub REST API to fetch followers and following lists,
    and identifies users who do not follow back.

    Parameters
    ----------
     username:str
      The GitHub username to analyze
    
     token:str
      Optional GitHub Personal Access Token to bypass rate limits

     base_url:str
      The base URL to which the requests will be forwarded

     checkpoint_dir:str
      Directory where pagination checkpoints are stored for recovery
    '''

    def __init__(self, username: str, token: Optional[str] = None, base_url: str = "https://api.github.com/users", 
                 checkpoint_dir: str = "snapshots/.checkpoints"):

        self.username = username
        self.token = token
        self.base_url = base_url 
        self.checkpoint_dir = resolve_project_path(checkpoint_dir)
        self._followers_cache = None
        self._following_cache = None


    def _build_headers(self) -> Dict[str, str]:

        '''
        It builds the HTTP headers required for GitHub API requests.

        Parameters
        ----------
         None

        Outputs
        -------
         headers:Dict[str, str]
          The dictionary of request headers including authentication if available
        '''

        headers = {
                        'Accept': 'application/vnd.github.v3+json',
                        'User-Agent': 'Who-Is-The-Mole'
                    }

        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"

        return headers


    def _build_url(self, endpoint: str, page: int, per_page: int = 100) -> str:

        '''
        It constructs the paginated GitHub API URL for a specific endpoint.

        Parameters
        ----------
         endpoint:str
          The API endpoint name (e.g. 'followers' or 'following')

         page:int
          The page number to query
         
         per_page:int
          Number of items per page (default is 100)

        Outputs
        -------
         url:str
          The formatted API URL
        '''

        return f"{self.base_url}/{self.username}/{endpoint}?per_page={per_page}&page={page}"


    def _parse_users(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        '''
        It extracts the relevant user fields from the raw GitHub API records.

        Parameters
        ----------
         data:List[Dict[str, Any]]
          The raw user records returned by GitHub

        Outputs
        -------
         users:List[Dict[str, Any]]
          The list of standardized user dictionaries containing 'username' and 'url'
        '''

        return [{'username': item['login'], 'url': item['html_url']} for item in data]


    def _validate_response(self, response: requests.Response, endpoint: str) -> None:

        '''
        It validates the GitHub API response status code and raises descriptive errors for failure cases.

        Parameters
        ----------
         response:requests.Response
          The HTTP response object from the API request
          
         endpoint:str
          The API endpoint name that was queried

        Outputs
        -------
         None

        Raises
        ------
         RuntimeError
          If the response indicates rate limiting, user not found, or any other API error
        '''

        if response.status_code == 200:
            return

        if response.status_code == 403 and "rate limit" in response.text.lower():
            raise RuntimeError(
                                    "GitHub API rate limit exceeded (HTTP 403). "
                                    "Pass '--github-token' with a Personal Access Token to raise your limit from 60 to 5,000 requests/hour."
                                )

        if response.status_code == 404:
            raise RuntimeError(f"GitHub user '{self.username}' not found (HTTP 404).")

        raise RuntimeError(f"GitHub API error for '{endpoint}' (HTTP {response.status_code}): {response.text}")


    def _get_checkpoint_path(self, endpoint: str) -> Path:

        '''
        It returns the checkpoint file path for the given endpoint and user.

        Parameters
        ----------
         endpoint:str
          The API endpoint name (e.g. 'followers' or 'following')

        Outputs
        -------
         path:Path
          The file path to the checkpoint JSON file
        '''

        return self.checkpoint_dir / f"github_{self.username}_{endpoint}.json"


    def _load_checkpoint(self, endpoint: str) -> tuple[int, List[Dict[str, Any]]]:

        '''
        It loads previously saved pagination progress if an interrupted checkpoint exists.

        Parameters
        ----------
         endpoint:str
          The API endpoint name

        Outputs
        -------
         tuple[int, List[Dict[str, Any]]]
          The next page number to query and the list of already-fetched user records
        '''

        checkpoint_file = self._get_checkpoint_path(endpoint)

        if checkpoint_file.exists():
        
            try:
        
                with checkpoint_file.open('r', encoding = 'utf-8') as f:
                    data = json.load(f)

                page = data.get('next_page', 1)
                results = data.get('results', [])
                
                if results and page > 1:
                    console.print(
                                        f"[cyan]Resuming '{endpoint}' from checkpoint:[/] page [bold]{page}[/bold] "
                                        f"([bold]{len(results)}[/bold] records already cached)"
                                    )
                    
                    return page, results
            
            except Exception:
                pass

        return 1, []


    def _save_checkpoint(self, endpoint: str, next_page: int, results: List[Dict[str, Any]]) -> None:

        '''
        It saves pagination progress to a checkpoint file upon error or interruption.

        Parameters
        ----------
         endpoint:str
          The API endpoint name
          
         next_page:int
          The next page number to query when resuming
          
         results:List[Dict[str, Any]]
          The list of user records fetched so far

        Outputs
        -------
         None
        '''

        checkpoint_file = self._get_checkpoint_path(endpoint)

        try:
        
            self.checkpoint_dir.mkdir(parents = True, exist_ok = True)

            with checkpoint_file.open('w', encoding = 'utf-8') as f:

                json.dump({
                                    'username': self.username,
                                    'endpoint': endpoint,
                                    'next_page': next_page,
                                    'results': results,
                                    'updated_at': datetime.now().isoformat()
                                }, f, indent = 4)
                
            console.print(
                                f"[bold yellow]⚠️ Checkpoint saved:[/] [cyan]{len(results)}[/cyan] records saved for '{endpoint}'. "
                                f"Re-running will resume from page {next_page}."
                            )
            
        except Exception as e:
            console.print(f"[dim]Failed to save checkpoint: {e}[/dim]")


    def _clear_checkpoint(self, endpoint: str) -> None:

        '''
        It deletes the checkpoint file once all pages have been completely retrieved.

        Parameters
        ----------
         endpoint:str
          The API endpoint name

        Outputs
        -------
         None
        '''

        checkpoint_file = self._get_checkpoint_path(endpoint)

        if checkpoint_file.exists():
        
            try:
        
                checkpoint_file.unlink()
        
            except Exception:
                pass


    def _fetch_all_pages(self, endpoint: str) -> List[Dict[str, Any]]:

        '''
        It paginates through the specified GitHub API endpoint to retrieve all the user records.

        Parameters
        ----------
         endpoint:str
          The API endpoint name to query (e.g. 'followers' or 'following')

        Outputs
        -------
         results:List[Dict[str, Any]]
          The list of user dictionaries containing 'username' and 'url'
        '''

        page, results = self._load_checkpoint(endpoint)
        headers = self._build_headers()

        try:

            while True:

                url = self._build_url(endpoint, page = page)
                response = requests.get(url, headers = headers)
                self._validate_response(response, endpoint)

                data = response.json()
                if not data:
                    break

                results.extend(self._parse_users(data))
                page += 1

            self._clear_checkpoint(endpoint)
            return results

        except BaseException:
            
            if results:
                self._save_checkpoint(endpoint, next_page = page, results = results)
            
            raise


    def get_followers(self) -> List[Dict[str, Any]]:

        '''
        It retrieves the list of users following the target account, caching the result.

        Parameters
        ----------
         None

        Outputs
        -------
         followers:List[Dict[str, Any]]
          The list of dictionaries containing follower usernames and profile URLs
        '''

        if self._followers_cache is None:
            self._followers_cache = self._fetch_all_pages("followers")

        return self._followers_cache


    def get_following(self) -> List[Dict[str, Any]]:

        '''
        It retrieves the list of users that the target account is following, caching the result.

        Parameters
        ----------
         None

        Outputs
        -------
         following:List[Dict[str, Any]]
          The list of dictionaries containing following usernames and profile URLs
        '''

        if self._following_cache is None:
            self._following_cache = self._fetch_all_pages("following")

        return self._following_cache
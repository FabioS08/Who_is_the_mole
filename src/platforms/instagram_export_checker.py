from .social_media_checker import SocialMediaChecker
from typing import List, Dict, Any, Union, Optional
from rich.console import Console
from datetime import datetime
from pathlib import Path
import json

console = Console()


class InstagramExportChecker(SocialMediaChecker):

    '''
    It parses the exported Instagram JSON data to extract followers and following lists
    and identifies users who do not follow back.

    Parameters
    ----------
     export_path:str | Path
      The file system path to the extracted Instagram data export folder
    '''

    def __init__(self, export_path: Union[str, Path]):

        self.export_path = Path(export_path)
        self._followers_cache = None
        self._following_cache = None


    def _locate_file(self, filename: str) -> Optional[Path]:

        '''
        It searches recursively across the export directory to find the specified JSON file.

        Parameters
        ----------
         filename:str
          The name of the JSON file to locate

        Outputs
        -------
         filepath:Optional[Path]
          The first matching Path found, or None if not found
        '''

        if not self.export_path.is_dir():
            return None

        direct_path = self.export_path / filename
        if direct_path.exists():
            return direct_path

        return next(self.export_path.rglob(filename), None)


    def _parse_user_entry(self, item: Any) -> Optional[Dict[str, Any]]:

        '''
        It extracts the username, profile URL and connection date from a raw Instagram item.

        Parameters
        ----------
         item:Any
          A single raw item from the Instagram JSON export

        Outputs
        -------
         entry:Optional[Dict[str, Any]]
          The extracted user dictionary containing 'username', 'url' and 'connection_date', or None
        '''

        if not isinstance(item, dict):
            return None

        username, timestamp, url = None, None, None

        if 'string_list_data' in item and len(item['string_list_data']) > 0:

            str_data = item['string_list_data'][0]
            username = str_data.get('value')
            timestamp = str_data.get('timestamp')
            url = str_data.get('href')
        
        elif 'username' in item:
            username = item.get('username')

        if not username:
            return None

        date_str = ""
        if timestamp:
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        return {
                    'username': username,
                    'url': url or f"https://instagram.com/{username}",
                    'connection_date': date_str
                }


    def _parse_users(self, data: Any) -> List[Dict[str, Any]]:

        '''
        It extracts and normalizes user records from the raw Instagram JSON data.

        Parameters
        ----------
         data:Any
          The raw data loaded from the JSON export file

        Outputs
        -------
         results:List[Dict[str, Any]]
          The list of user dictionaries containing 'username', 'url', and 'connection_date'
        '''

        items = data
        if isinstance(data, dict):
            for val in data.values():
                if isinstance(val, list):
            
                    items = val
                    break

        if not isinstance(items, list):
            return []

        results = []
        for item in items:
            
            entry = self._parse_user_entry(item)
            
            if entry:
                results.append(entry)

        return results


    def _parse_file(self, filename: str) -> List[Dict[str, Any]]:

        '''
        It reads and parses an Instagram JSON export file to extract user profiles and connection metadata.

        Parameters
        ----------
         filename:str
          The name of the JSON file to parse (e.g. 'followers_1.json' or 'following.json')

        Outputs
        -------
         results:List[Dict[str, Any]]
          The list of user dictionaries containing 'username', 'url', and 'connection_date'
        '''

        filepath = self._locate_file(filename)

        if not filepath:
            console.print(f"[bold yellow]⚠️  Warning:[/] Could not find [cyan]{filename}[/cyan] in [bold]{self.export_path}[/bold]")
            return []

        with filepath.open('r', encoding='utf-8') as f:
            data = json.load(f)

        return self._parse_users(data)


    def get_followers(self) -> List[Dict[str, Any]]:

        '''
        It retrieves the list of followers from the Instagram export, caching the result.

        Parameters
        ----------
         None

        Outputs
        -------
         followers:List[Dict[str, Any]]
          The list of dictionaries containing follower usernames, profile URLs, and connection dates
        '''

        if self._followers_cache is None:
            self._followers_cache = self._parse_file('followers_1.json')
            
        return self._followers_cache


    def get_following(self) -> List[Dict[str, Any]]:

        '''
        It retrieves the list of users followed from the Instagram export, caching the result.

        Parameters
        ----------
         None

        Outputs
        -------
         following:List[Dict[str, Any]]
          The list of dictionaries containing followed usernames, profile URLs, and connection dates
        '''

        if self._following_cache is None:
            self._following_cache = self._parse_file('following.json')

        return self._following_cache
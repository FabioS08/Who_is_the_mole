from .social_media_checker import SocialMediaChecker
from typing import List, Dict, Any, Union, Optional
from urllib.parse import urlparse
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


    @staticmethod
    def _extract_from_string_list_data(item: Dict[str, Any]) -> tuple[Optional[str], Optional[int], Optional[str]]:

        '''
        It extracts the username, timestamp and profile URL from the 'string_list_data' attribute.

        Parameters
        ----------
         item:Dict[str, Any]
          A single raw item dictionary from the Instagram JSON export

        Outputs
        -------
         data:tuple[Optional[str], Optional[int], Optional[str]]
          A tuple containing (username, timestamp, url)
        '''

        entries = item.get('string_list_data')
        if entries:

            entry = entries[0]
            username = (entry.get('value') or '').strip() or None
            
            return username, entry.get('timestamp'), entry.get('href')

        return None, None, None


    @staticmethod
    def _extract_username_from_title(item: Dict[str, Any]) -> Optional[str]:

        '''
        It extracts the account username from the 'title' attribute (used by Meta in following.json).

        Parameters
        ----------
         item:Dict[str, Any]
          A single raw item dictionary from the Instagram JSON export

        Outputs
        -------
         username:Optional[str]
          The extracted username from the title, or None if missing or empty
        '''

        return (item.get('title') or '').strip() or None


    @staticmethod
    def _extract_username_from_field(item: Dict[str, Any]) -> Optional[str]:

        '''
        It extracts the account username from the direct 'username' attribute of an Instagram entry.

        Parameters
        ----------
         item:Dict[str, Any]
          A single raw item dictionary from the Instagram JSON export

        Outputs
        -------
         username:Optional[str]
          The extracted username, or None if the attribute is missing or empty
        '''

        return (item.get('username') or '').strip() or None


    @staticmethod
    def _extract_username_from_href(href: Optional[str]) -> Optional[str]:

        '''
        It extracts the username from an Instagram profile URL, handling both standard and internal link formats.

        Parameters
        ----------
         href:Optional[str]
          The Instagram profile URL (e.g. 'https://www.instagram.com/username' or 'https://www.instagram.com/_u/username')

        Outputs
        -------
         username:Optional[str]
          The extracted account username or None if the URL is invalid or empty
        '''

        if not href:
            return None

        parts = [p for p in urlparse(href).path.split('/') if p]

        if not parts:
            return None

        return parts[1] if parts[0] == '_u' and len(parts) > 1 else parts[0]


    @staticmethod
    def _format_timestamp(timestamp: Optional[int]) -> str:

        '''
        It formats a Unix epoch timestamp into a human-readable date-time string.

        Parameters
        ----------
         timestamp:Optional[int]
          The Unix epoch timestamp in seconds

        Outputs
        -------
         date_str:str
          The formatted date string ('YYYY-MM-DD HH:MM:SS') or an empty string if invalid or absent
        '''

        if not timestamp:
            return ""

        try:

            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        except (ValueError, OverflowError, OSError):
            return ""


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

        username, timestamp, url = self._extract_from_string_list_data(item)

        # Fallback 1: check 'title' (used by Meta in following.json)
        if not username:
            username = self._extract_username_from_title(item)

        # Fallback 2: check 'username' key (legacy export format)
        if not username:
            username = self._extract_username_from_field(item)

        # Fallback 3: extract username from profile URL
        if not username and url:
            username = self._extract_username_from_href(url)

        if not username:
            return None

        return {
                    'username': username,
                    'url': url or f"https://instagram.com/{username}",
                    'connection_date': self._format_timestamp(timestamp)
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
          The list of user dictionaries containing 'username', 'url' and 'connection_date'
        '''

        if isinstance(data, dict):

            items = data.get('relationships_following') or data.get('relationships_followers')
            if not items:
                items = next((v for v in data.values() if isinstance(v, list)), [])
        
        else:
            items = data or []

        results = []
        seen = set()
        for item in items:
            
            entry = self._parse_user_entry(item)
            
            if entry:
               
                u_lower = entry['username'].lower()
            
                if u_lower not in seen:
                    seen.add(u_lower)
                    results.append(entry)

        return results


    def _parse_file_path(self, filepath: Path) -> List[Dict[str, Any]]:

        '''
        It reads a JSON export file from disk and parses its user records.

        Parameters
        ----------
         filepath:Path
          The file system Path to the JSON file to parse

        Outputs
        -------
         results:List[Dict[str, Any]]
          The list of user dictionaries parsed from the file
        '''

        try:

            with filepath.open('r', encoding = 'utf-8') as f:
                data = json.load(f)
            
            return self._parse_users(data)
        
        except Exception as e:
            console.print(f"[bold yellow]⚠️  Warning:[/] Error reading [cyan]{filepath.name}[/cyan]: {e}")
            return []


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

        return self._parse_file_path(filepath)


    def _parse_pattern(self, pattern: str, fallback_file: str) -> List[Dict[str, Any]]:

        '''
        It searches and parses all files matching a glob pattern or falls back to a single file.

        Parameters
        ----------
         pattern:str
          The glob pattern to match chunked files (e.g. 'followers*.json')

         fallback_file:str
          The fallback file name if no matching files are found

        Outputs
        -------
         results:List[Dict[str, Any]]
          The aggregated and deduplicated list of parsed user records
        '''

        matching = sorted(self.export_path.rglob(pattern)) if self.export_path.is_dir() else []
        if not matching:
            return self._parse_file(fallback_file)

        results = []
        seen = set()

        for filepath in matching:
            for user in self._parse_file_path(filepath):
        
                u_lower = user['username'].lower()
        
                if u_lower not in seen:
        
                    seen.add(u_lower)
                    results.append(user)

        return results


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
            self._followers_cache = self._parse_pattern('followers*.json', 'followers_1.json')

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
            self._following_cache = self._parse_pattern('following*.json', 'following.json')

        return self._following_cache
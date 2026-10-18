from .utils import resolve_project_path
from typing import List, Dict, Any
from rich.console import Console
from datetime import datetime
from pathlib import Path
import json


console = Console()


class SnapshotManager:

    '''
    It manages the snapshots of followers over time to detect and track unfollow dates.
    '''

    def __init__(self, platform_name: str, account_id: str, dir: str = 'snapshots'):

        '''
        It initializes the snapshot manager with the platform and account details, ensuring the snapshots 
        storage directory exists.

        Parameters
        ----------
         platform_name:str
          The social media platform name (e.g. 'github', 'instagram')
        
         account_id:str
          The account username or identifier associated with the snapshot

        Outputs
        -------
         None
        '''

        self.snapshots_dir = resolve_project_path(dir)
        self.snapshots_dir.mkdir(parents = True, exist_ok = True)
        self.history_file = self.snapshots_dir / f"{platform_name}_{account_id}_history.json"
        self.new_unfollowers_count = 0
    

    def load_history(self) -> Dict[str, Any]:

        '''
        It loads the previous followers and recorded unfollow dates from the persistent JSON file.

        Parameters
        ----------
         None

        Outputs
        -------
         history:Dict[str, Any]
          The dictionary containing previously saved followers and recorded unfollow dates
        '''

        if not self.history_file.exists():
            return {"followers": [], "unfollow_dates": {}}
        
        with open(self.history_file, 'r', encoding = 'utf-8') as f:
            return json.load(f)
            

    def save_history(self, history: Dict[str, Any]) -> None:

        '''
        It saves the updated followers and unfollow dates to the persistent JSON file.

        Parameters
        ----------
         history:Dict[str, Any]
          The dictionary containing the current followers and unfollow dates to persist

        Outputs
        -------
         None
        '''

        with open(self.history_file, 'w', encoding = 'utf-8') as f:
            json.dump(history, f, indent = 4)
            

    def _update_unfollow_dates(self, previous_followers: set, current_followers_set: set, unfollow_dates: Dict[str, str]) -> Dict[str, str]:

        '''
        It identifies the followers who unfollowed you since the last snapshot and records the today's date for them.

        Parameters
        ----------
         previous_followers:set
          Set of usernames from the previous snapshot
         
         current_followers_set:set
          Set of usernames from the current followers
         
         unfollow_dates:Dict[str, str]
          Mapping of usernames to recorded unfollow dates

        Outputs
        -------
         unfollow_dates:Dict[str, str]
          Updated mapping of usernames to unfollow date strings
        '''

        today = datetime.now().strftime('%Y-%m-%d')
        current_lower = {u.lower() for u in current_followers_set}
        unfollowed = {u for u in previous_followers if u.lower() not in current_lower}

        for username in unfollowed:
            if username not in unfollow_dates:
                unfollow_dates[username] = today

        return unfollow_dates


    def _enrich_non_followers(self, non_followers: List[Dict], unfollow_dates: Dict[str, str]) -> List[Dict]:

        '''
        It attaches the recorded unfollow date metadata to each user in the non-followers list.

        Parameters
        ----------
         non_followers:List[Dict]
          The list of dictionaries representing users followed who do not follow back

         unfollow_dates:Dict[str, str]
          The mapping of usernames to recorded unfollow dates

        Outputs
        -------
         non_followers:List[Dict]
          The enhanced non-followers list containing 'unfollow_date' metadata
        '''

        dates_lower = {k.lower(): v for k, v in unfollow_dates.items()}

        for nf in non_followers:

            username = nf['username']
            nf['unfollow_date'] = dates_lower.get(username.lower(), "Unknown (Not in history)")

        return non_followers


    def process(self, current_followers: List[Dict], non_followers: List[Dict]) -> List[Dict]:

        '''
        It compares the current followers against the previous snapshot, updates unfollow
        dates, enhances the non-followers list with date metadata and saves the new snapshot.

        Parameters
        ----------
         current_followers:List[Dict]
          The list of dictionaries representing the current followers
          
         non_followers:List[Dict]
          The list of dictionaries representing users followed that do not follow back

        Outputs
        -------
         non_followers:List[Dict]
          The enhanced non-followers list containing 'unfollow_date' metadata
        '''

        history = self.load_history()

        previous_followers = set(history.get("followers", []))
        unfollow_dates = history.get("unfollow_dates", {})
        current_followers_set = {f['username'] for f in current_followers}

        if not previous_followers:
            self.new_unfollowers_count = 0
            console.print("[dim]First snapshot recorded for this account. Future checks will track unfollow dates.[/dim]")

        else:

            current_lower = {u.lower() for u in current_followers_set}
            new_unfollowers = [u for u in previous_followers if u.lower() not in current_lower and u not in unfollow_dates]
            self.new_unfollowers_count = len(new_unfollowers)

            if new_unfollowers:
                console.print(f"[bold yellow]⚠️  Detected [bold]{len(new_unfollowers)}[/bold] new unfollower(s) since last check![/bold yellow]")

        unfollow_dates = self._update_unfollow_dates(previous_followers, current_followers_set, unfollow_dates)
        enriched_non_followers = self._enrich_non_followers(non_followers, unfollow_dates)

        # Save current state
        history["followers"] = list(current_followers_set)
        history["unfollow_dates"] = unfollow_dates
        self.save_history(history)

        return enriched_non_followers
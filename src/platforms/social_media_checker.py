from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SocialMediaChecker(ABC):

    '''
    It defines the abstract base interface for social media platform checkers.
    '''

    @abstractmethod
    def get_followers(self) -> List[Dict[str, Any]]:

        '''
        It returns the current list of followers to track unfollowers over time.

        Parameters
        ----------
         None

        Outputs
        -------
         followers:List[Dict[str, Any]]
          The list of dictionaries representing the current followers
        '''

        pass


    @abstractmethod
    def get_following(self) -> List[Dict[str, Any]]:

        '''
        It returns the current list of users being followed.

        Parameters
        ----------
         None

        Outputs
        -------
         following:List[Dict[str, Any]]
          The list of dictionaries representing the currently followed users
        '''

        pass


    def get_non_followers(self) -> List[Dict[str, Any]]:

        '''
        It identifies and returns the list of users followed by the target account who do not follow back.

        Parameters
        ----------
         None

        Outputs
        -------
         non_followers:List[Dict[str, Any]]
          The list of dictionaries containing users followed who do not follow back
        '''

        followers = {f['username'].lower() for f in self.get_followers()}
        non_followers = []

        for user in self.get_following():
            if user['username'].lower() not in followers:
                non_followers.append(user)

        return non_followers
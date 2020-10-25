# PyFantasyFootball
## A package designed to gather NFL player statistics for easy analysis
Clean NFL data is hard to come by, and this package aims to alleviate the pain in gathering it. Essentially, this package scrapes the Pro Football Reference website (PFR) and formats the data nicely into [pandas](https://pandas.pydata.org/) dataframes. This is a very much unofficial method of gathering data through PFR, so please use at your own risk.

---

## Features
- Collects fantasy rankings from PFR into a pandas df
- Get JSON like format of players, their fantasy position, and PFR profile link
- Collect player career statistics for analysis
- Get a df of a player's game history and calculate their fantasy points per game (STD only for now)
## Planned Features
- Allow the creation of training data for stats/ML models
- Gather team depth charts

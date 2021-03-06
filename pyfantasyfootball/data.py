from bs4 import BeautifulSoup
import os
import pandas as pd
import requests


YEAR = '2020'
FANT_TABLE_URL = 'https://www.pro-football-reference.com/years/'

# FANTASY POINTS
FP_PASS_YDS = 0.04
FP_PASS_TD = 4
FP_INT = -2
FP_RUSH_YDS = 0.1
FP_RUSH_TD = 6
FP_REC_YDS = 0.1
FP_REC_TD = 6
FP_KICK_PR_TD = 6
FP_FUM_LOST = -2
FP_2PT_CONV = 2


class Data:
    def __init__(self):
        self.cwd = os.getcwd()
        self.url = 'https://www.pro-football-reference.com/'

    def fantasy_table(self, year=YEAR, save=False):
        # using bs4 to scrape fantasy table from bs4
        url = f'{FANT_TABLE_URL}{year}/fantasy.htm'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        fant_table = soup.find('table')  # selecting table

        # finding links to players' profile page
        player_links_td = soup.find_all("td", {"data-stat": "player"})
        player_links = {}
        for td in player_links_td:
            _a = td.find("a", href=True)
            player_links[_a.text.strip().upper()] = _a['href']

        # passing html to pandas
        fant_df = pd.read_html(str(fant_table), index_col=0)[0]

        # cleaning df
        fant_df.columns = fant_df.columns.droplevel(0)  # rem double headers
        fant_df = fant_df[fant_df['Player'] != 'Player']
        fant_df = fant_df.fillna(0)  # filling empty cells with 0
        new_dtypes = {'Age': int, 'G': int, 'GS': int, 'Cmp': int,
                      'Yds': float, 'TD': int, 'Int': int, 'Att': int,
                      'Y/A': float, 'Tgt': int, 'Y/R': float, 'Fmb': int,
                      'FL': int, '2PM': int, '2PP': int, 'FantPt': float,
                      'PPR': float, 'DKPt': float, 'FDPt': float,
                      'PosRank': int, 'OvRank': int, 'VBD': int, 'Rec': int}
        fant_df = fant_df.astype(new_dtypes)  # assigning proper types to df
        fant_df['FantPos'] = fant_df.apply(lambda x:
                                           str(x['FantPos']).upper().strip(),
                                           axis=1)
        fant_df['Player'] = fant_df.apply(lambda x:
                                          str(x['Player']).upper().strip(),
                                          axis=1)
        fant_df['Tm'] = fant_df.apply(lambda x:
                                      str(x['Tm']).upper().strip(), axis=1)
        fant_df.set_index('Player', inplace=True)
        fant_df.sort_values(by='FantPt', ascending=False, inplace=True)

        # renaming cols to make same name cols distinct
        fant_df.columns = ['Tm', 'FantPos', 'Age', 'G', 'GS', 'Cmp', 'P_Att',
                           'P_Yds', 'P_TD', 'Int', 'Ru_Att', 'Ru_Yds',
                           'Y/Ru_A', 'Ru_TD', 'Tgt', 'Rec', 'Re_Yds', 'Y/Rec',
                           'Re_TD', 'Fmb', 'FL', 'Tot TD', '2PM', '2PP',
                           'FantPt', 'PPR', 'DKPt', 'FDPt', 'VBD', 'PosRank',
                           'OvRank']

        # adding player links col
        fant_df['Prof Link'] = 'None'
        for player in fant_df.index:
            fant_df.at[player, 'Prof Link'] = player_links[player]

        # adding additional stats if preferred
        fant_df = self._additional_stats_fant_df(fant_df)

        if save is True:
            # creating folder to store results if it does not exist
            try:
                os.mkdir(os.path.join(self.cwd, 'FantasyStandings'))
            except Exception as e:
                print(e)
            fant_df.to_csv('FantasyStandings/fantrankings.csv')

        return fant_df

    def save_current_pos_rankings(self):
        fant_df = self.fantasy_table()

        # creating new dfs for each position
        qb_df = fant_df[fant_df['FantPos'] == 'QB']
        wr_df = fant_df[fant_df['FantPos'] == 'WR']
        rb_df = fant_df[fant_df['FantPos'] == 'RB']
        te_df = fant_df[fant_df['FantPos'] == 'TE']

        # creating folder to store results if it does not exist
        try:
            os.mkdir(os.path.join(self.cwd, 'FantasyStandings'))
        except Exception as e:
            print(e)

        # saving locally to csv files
        qb_df.to_csv('FantasyStandings/qbfantstandings.csv')
        wr_df.to_csv('FantasyStandings/wrfantstandings.csv')
        rb_df.to_csv('FantasyStandings/rbfantstandings.csv')
        te_df.to_csv('FantasyStandings/tefantstandings.csv')

    def players(self, year=YEAR):
        year = str(year)
        fant_df = self.fantasy_table(year=year)

        # creating a json like dictionary containing player, pos,
        # and gamelog link
        players_dict = {}
        players = fant_df.index

        for player in players:
            pos = fant_df.loc[player]['FantPos']
            link = fant_df.loc[player]['Prof Link']
            players_dict[player] = {'Position': pos, 'Profile Link': link}

        return players_dict

    def _additional_stats_fant_df(self, df):
        df['FantPt/G'] = df['FantPt'] / df['G']

        return df

    def career_gamelogs(self, player):
        # Only able to get data for players with fantasy pts this year
        player = player.upper()

        players_dict = self.players()

        info = players_dict[player]
        # pos = info['Position']
        link = info['Profile Link']

        url = f'{self.url + link}/gamelog'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table')  # selecting table

        df = pd.read_html(str(table))[0]

        col_names = []
        for i, j in df.columns:
            if i.startswith('Unnamed'):
                col_names.append(j)
            else:
                col_names.append(f'{i}_{j}')

        # cleaning (pretty rough)
        df.columns = col_names
        df.rename(columns={df.columns[7]: 'Away?'}, inplace=True)
        df = df[df['Age'] != 'Age']
        df.drop(df.tail(1).index, inplace=True)
        df.fillna(0, inplace=True)
        df.set_index('Rk', inplace=True)
        # note this next line ignores cols with percentages
        df = df.astype(dict.fromkeys(df.columns[10:], float), errors='ignore')

        return df

    def fantasy_gamelogs(self, player):
        player = player.upper()

        df = self.career_gamelogs(player)

        scoring_cols = ['Passing_Yds', 'Passing_TD', 'Passing_Int',
                        'Rushing_Yds', 'Rushing_TD', 'Receiving_Yds',
                        'Receiving_TD', 'Fumbles_FL', 'Scoring_2PM']

        for col in scoring_cols:
            if col not in df.columns:
                df[col] = 0

        df['FantPt'] = 0

        df['FantPt'] = ((df['Passing_Yds'] * FP_PASS_YDS) +
                        (df['Passing_TD'] * FP_PASS_TD) +
                        (df['Passing_Int'] * FP_INT) +
                        (df['Rushing_Yds'] * FP_RUSH_YDS) +
                        (df['Rushing_TD'] * FP_RUSH_TD) +
                        (df['Receiving_Yds'] * FP_REC_YDS) +
                        (df['Receiving_TD'] * FP_REC_TD) +
                        (df['Fumbles_FL'] * FP_FUM_LOST) +
                        (df['Scoring_2PM'] * FP_2PT_CONV))

        return df

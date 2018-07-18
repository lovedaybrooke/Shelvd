from pyparsing import *

# Adam sez that this line means the only thing imported when I do
# 'from grammar import *' will be the value of expression.
__all__ = ['expression']

initiator = (Keyword('begin') | Keyword('start')).setResultsName("initiator")
terminator = (Keyword('end') | Keyword('finish') |
    Keyword('abandon')).setResultsName("terminator")
currentlyreading = (Keyword('reading')).setResultsName(
    "currentlyreading")
isbn = Word(nums, min=13, max=13).setResultsName("isbn")
nickname = Word(alphas).setResultsName("nickname")
percent = (Word(nums, min=1, max=2) + Word("%",
    exact=1)).setResultsName("percent")
page = Word(nums, min=1, max=4).setResultsName("page")


identifier = isbn | nickname
command = initiator | terminator | percent | page

expression = currentlyreading | identifier + command | isbn + nickname

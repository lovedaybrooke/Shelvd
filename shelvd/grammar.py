from pyparsing import *

# Adam sez that this line means the only thing imported when I do
# 'from grammar import *' will be the value of expression.
__all__ = ['expression']

initiator = (Keyword('begin') | Keyword('start')).setResultsName("initiator")
terminator = (Keyword('end') | Keyword('finish') |
    Keyword('abandon')).setResultsName("terminator")
addreadinglist = (Keyword('addtoreadinglist')).setResultsName("addreadinglist")
help = (Keyword('Help') | Keyword('help')).setResultsName("help")
currentlyreading = (Keyword('reading') | Keyword('Currently reading') |
    Keyword('currently reading') | Keyword('Reading')).setResultsName(
    "currentlyreading")
isbn = Word(nums, min=10, max=13).setResultsName("isbn")
nick = Word(alphas).setResultsName("nick")
percent = (Word(nums, min=1, max=2) + Word("%",
    exact=1)).setResultsName("percent")
page = Word(nums, min=1, max=4).setResultsName("page")


identifier = isbn | nick
command = initiator | terminator | addreadinglist | percent | page

expression = help | currentlyreading | identifier + command | isbn + nick

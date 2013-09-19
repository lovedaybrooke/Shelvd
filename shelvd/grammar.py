from pyparsing import *

# Adam sez that this line means the only thing imported when I do
# 'from grammar import *' will be the value of expression.
__all__ = ['expression']

initiator = (Keyword('begin') | Keyword('start')).setResultsName("initiator")
terminator = (Keyword('end') | Keyword('finish')
    | Keyword('abandon')).setResultsName("terminator")
readinglist = (Keyword('addtoreadinglist')).setResultsName("readinglist")
isbn = Word(nums, min=10, max=13).setResultsName("isbn")
nick = Word(alphas).setResultsName("nick")
percent = (Word(nums, min=1, max=2) + Word("%",
    exact=1)).setResultsName("percent")
page = Word(nums, min=1, max=4).setResultsName("page")


identifier = isbn | nick
command = initiator | terminator | readinglist | percent | page

expression = identifier + command | isbn + nick

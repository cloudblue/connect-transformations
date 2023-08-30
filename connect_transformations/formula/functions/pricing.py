functions = [
    """
    def gross_profit($list_price; $cogs):
        list_price - cogs
    ;
    """,

    """
    def margin($list_price; $cogs):
        gross_profit($list_price; $cogs) / $list_price * 100
    ;
    """,

    """
    def markup($list_price; $cogs):
        gross_profit($list_price; $cogs) / $cogs * 100
    ;
    """,
]

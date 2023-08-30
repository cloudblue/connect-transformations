functions = [
    # tonumber("2") -> 2
    """
    def tonumber($value):
        $value | tonumber
    ;
    """,

    # round(10.567, 2) -> 10.57
    # 10.567 | round(1) -> 10.6
    # 10.567 | round -> 10
    """
    def round($number; $precision):
        pow(10; $precision | floor) as $m | $number * $m | round / $m
    ;
    def round($precision):
        round(.; $precision)
    ;
    """,
]

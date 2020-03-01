import yagot

@yagot.leak_check(check_collected=True)
def test_selfref_dict():
    d1 = dict()
    d1['self'] = d1

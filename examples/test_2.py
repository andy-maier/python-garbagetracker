import yagot

@yagot.garbage_checked()
def test_selfref_dict():
    d1 = dict()
    d1['self'] = d1

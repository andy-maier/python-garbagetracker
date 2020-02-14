import yagot

@yagot.garbage_tracked
def test_selfref_dict():

    # Dictionary with self-referencing item:
    d1 = dict()
    d1['self'] = d1

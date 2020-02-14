from yagot import garbage_tracked

@garbage_tracked
def test_selfref_dict():

    # Dictionary with self-referencing item:
    d1 = dict()
    d1['self'] = d1
    try:
        x = y
    except NameError:
        pass

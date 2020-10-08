import pytest
from wasteland_sort import wasteland_sort as ws

def test_wasteland_already_sorted():
    landmarks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ws.wasteland_sort(landmarks, False)
    assert landmarks == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

def test_wasteland_out_of_order():
    landmarks = [10, 9, 7, 4, 6, 2, 1, 5, 8, 3]
    ws.wasteland_sort(landmarks, False)
    assert [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] == landmarks


###
def test_wasteland_reverse_already_sorted():
    landmarks = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    ws.wasteland_sort(landmarks, True)
    assert landmarks == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

def test_wasteland_reverse_out_of_order():
    landmarks = [10, 9, 7, 4, 6, 2, 1, 5, 8, 3]
    ws.wasteland_sort(landmarks, True)
    assert [10, 9, 8, 7, 6, 5, 4, 3, 2, 1] == landmarks


###
def test_wasteland_large_wastes():
    landmarks = [1,1,1,20,1,1,20,1,1,1,100,1,1,1,1,1,1,1,]
    ws.wasteland_sort(landmarks, False)
    assert [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,20,20,100] == landmarks

def test_wasteland_large_wastes_reverse():
    landmarks = [1,1,1,20,1,1,20,1,1,1,100,1,1,1,1,1,1,1,]
    ws.wasteland_sort(landmarks, True)
    assert [100,20,20,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1] == landmarks


###
def test_wasteland_empty():
    assert [] == ws.wasteland_sort([], False)

def test_wasteland_reverse_empty():
    assert [] == ws.wasteland_sort([], True)




############Helper functions##################
def test_find_extremes_empty():
    with pytest.raises(ValueError):
        ws.find_extremes([])

def test_find_extremes_nonempty():
    with pytest.raises(ValueError):
        ws.find_extremes([])

def test_find_extremes_one_value():
    assert 1, 1 == ws.find_extremes([1])

def test_find_extremes():
    input = [10, 9, 7, 4, 6, 2, 1, 5, 8, 3]
    assert 1, 10 == ws.find_extremes(input)
    
class Funcad:
    def __init__(self):
        self.cos15 = 0.965926
        self.cos30 = 0.866
        self.cos45 = 0.7071
        self.cos60 = 0.5
        self.cos75 = 0.258819

        self.__is_not_used = True

    def from_motors_to_axis(self, right: float, left: float, back: float):
        return [(right - left) * self.cos30,
                (right + left) * self.cos60 - back,
                -right - left - back]

    def from_axis_to_motors(self, x: float, y: float, z: float):
        return [(x / self.cos30) - (-y * self.cos60) - (z / 3),
                (-x / self.cos30) - (-y * self.cos60) - (z / 3),
                (-y) - (z / 3)]

    def in_range_bool(self, val: float, min_v: float, max_v: float):
        """
        Func that checks that value in range min and max
        :param val: Value that needs to check
        :param min_v: Min limit
        :param max_v: Max limit
        :return: Value in range
        """
        self.__is_not_used = True
        return (val >= min_v) and (val <= max_v)

    def transfunc_coda(self, arr: list, val: float):
        """
        Not moronic transfer function
        Powered by Coda (Vitality)
        :param arr: Input 2D array (1D array includes input and output values) like:
            [[1, 11], [2, 12], [3, 13]]
        :param val: Input of value to conversion by transfer function
        :return: Output is conversed input
        """
        self.__is_not_used = True
        min_i = 0
        max_i = 0
        min_o = 0
        max_o = 0
        if val < arr[0][0]:
            return arr[0][1]
        if val > arr[len(arr) - 1][0]:
            return arr[len(arr) - 1][1]
        for i in range(len(arr)):
            mxp_i = arr[i][0] + (arr[i][0] - arr[i - 1][0]) if i + 1 == len(arr) else arr[i + 1][0]
            mxp_o = arr[i][1] + (arr[i][1] - arr[i - 1][1]) if i + 1 == len(arr) else arr[i + 1][1]
            mixp_i = arr[i][0] + (arr[i][0] + arr[i + 1][0]) if arr[i][0] > val else arr[i][0]
            mixp_o = arr[i][1] + (arr[i][1] + arr[i + 1][1]) if arr[i][0] > val else arr[i][1]
            if self.in_range_bool(val, mixp_i, mxp_i):
                min_i = mixp_i
                max_i = mxp_i
                min_o = mixp_o
                max_o = mxp_o
                break
        return min_o + (((max_o - min_o) * ((val - min_i) * 100 / (max_i - min_i))) / 100)

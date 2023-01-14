def transform(self, x, y):
    """ Transform canvas in 2D view or Perspective view (need to comment 1 option)

    :param self:
    :type self:
    :param x: x coordinate
    :type x: int
    :param y: y coordinate
    :type y: int
    :return: tuple with x and y coordinatesq
    :rtype: tuple
    """
    # return self.transform_2d(x, y)
    return self.transform_perspetive(x, y)


def transform_2d(self, x, y):
    """ Generate the canvas in 2D view

    :param self:
    :type self:
    :param x: coordinate of x
    :type x: int
    :param y: coordinate of y
    :type y: int
    :return: tuple with x and y coordinates
    :rtype: tuple
    """
    return int(x), int(y)


def transform_perspetive(self, x, y):
    """ Transform the canvas (the lines) in perspective

    :param self:
    :type self:
    :param x: coordinate of x
    :type x: int
    :param y: coordinate of y
    :type y: int
    :return: tuple with the x and y coordiantes
    :rtype: tuple
    """
    lin_y = y * self.perspective_point_y / self.height
    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y

    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - lin_y
    factor_y = diff_y / self.perspective_point_y
    factor_y = pow(factor_y, 3)

    offset_x = diff_x * factor_y

    tr_x = self.perspective_point_x + offset_x
    tr_y = self.perspective_point_y - factor_y * self.perspective_point_y

    return int(tr_x), int(tr_y)

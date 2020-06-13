import cv2
import imageio
import numpy as np


def crop_image(img, r):
    sx, sy = [int(x / 2 - r) for x in img.shape]
    return img[sx:sx + 2 * r, sy:sy + 2 * r]


def circle_mask(img, r):
    cx, cy = [x / 2 for x in img.shape]
    x, y = [np.arange(0, x) for x in img.shape]
    mask = (x[np.newaxis, :] - cx) ** 2 + (y[:, np.newaxis] - cy) ** 2 > r ** 2

    img[mask] = 1

    return img


def make_rectangle(rect_shape, num_hooks=250, offset=0):
    """
    Make rectangle coordinates.

    :param tuple|list rect_shape:
        (width, height) of rectangle.
    :param int num_hooks:
        How many points are used to create the rectangle.
    :param int offset:
        Offset for point numbering (to shift motive around the rectangle)
    :return: np.array of rectangle coordinates (x, y)
    """

    hooks_per_x = rect_shape[0] / (
            rect_shape[0] + rect_shape[1]) * num_hooks / 2
    hooks_per_y = rect_shape[1] / (
            rect_shape[0] + rect_shape[1]) * num_hooks / 2

    # make edges non-symmetric to avoid symmetry patterns in the final result
    first_edge_x = np.linspace(0.0, rect_shape[0], int(np.ceil(hooks_per_x)))
    second_edge_x = np.linspace(0.0, rect_shape[0],
                                int(np.ceil(hooks_per_x)) - 1)
    first_edge_y = np.linspace(0.0, rect_shape[1], int(np.ceil(hooks_per_y)))
    second_edge_y = np.linspace(0.0, rect_shape[1],
                                int(np.ceil(hooks_per_y)) - 1)

    rectangle = [[x, 0] for x in first_edge_x]
    rectangle += [[first_edge_x[-1], y] for y in first_edge_y]
    rectangle += [[x, first_edge_y[-1]] for x in second_edge_x[::-1]]
    rectangle += [[0, y] for y in second_edge_y[::-1]]
    rectangle = rectangle[offset:] + rectangle[:offset]
    rectangle = np.asarray(rectangle)
    _, idx = np.unique(rectangle, return_index=True, axis=0)
    return rectangle[np.sort(idx)], num_hooks


def make_circle(img_shape, num_hooks=201):
    theta = np.linspace(0, 2 * np.pi, num_hooks)
    return np.round(np.asarray([
        (img_shape[0] / 2 - 1) * np.cos(theta),
        (img_shape[0] / 2 - 1) * np.sin(theta)]) +
                    img_shape[0] / 2).astype(int).T


def pre_proc_img(filename, img_size, crop_factor, rectangle=False):
    img = np.mean(imageio.imread(filename), axis=2) / 255
    img = crop_image(img, int(min(img.shape) / crop_factor / 2))
    img = cv2.resize(img, (img_size, img_size), interpolation=cv2.INTER_AREA)
    if rectangle:
        return img
    else:
        return circle_mask(img, img_size / 2)


def mat_line(p1, p2):
    inter = int(np.floor(np.max((np.abs(p1 - p2)))))
    return np.asarray([
        np.round(np.linspace(p1[0], p2[0], inter)),
        np.round(np.linspace(p1[1], p2[1], inter))]).astype(int).T

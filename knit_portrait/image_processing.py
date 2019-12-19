import numpy as np
import cv2
import imageio


def crop_image(img, r):
    sx, sy = [int(x / 2 - r) for x in img.shape]
    return img[sx:sx + 2 * r, sy:sy + 2 * r]


def circle_mask(img, r):
    cx, cy = [x / 2 for x in img.shape]
    x, y = [np.arange(0, x) for x in img.shape]
    mask = (x[np.newaxis, :] - cx) ** 2 + (y[:, np.newaxis] - cy) ** 2 > r ** 2

    img[mask] = 1

    return img


def make_circle(img, num_hooks=201):
    theta = np.linspace(0, 2 * np.pi, num_hooks)
    return np.round(np.asarray([
        (img.shape[0] / 2 - 1) * np.cos(theta),
        (img.shape[0] / 2 - 1) * np.sin(theta)]) +
                    img.shape[0] / 2).astype(int).T


def pre_proc_img(filename, img_size, crop_factor):
    img = np.mean(imageio.imread(filename), axis=2) / 255
    img = crop_image(img, int(min(img.shape) / crop_factor / 2))
    img = cv2.resize(img, (img_size, img_size), interpolation=cv2.INTER_AREA)
    return circle_mask(img, img_size / 2)


def mat_line(p1, p2):
    inter = np.max((np.abs(p1 - p2)))
    return np.asarray([
        np.round(np.linspace(p1[0], p2[0], inter)),
        np.round(np.linspace(p1[1], p2[1], inter))]).astype(int).T

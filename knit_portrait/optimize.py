import numpy as np
from knit_portrait.image_processing import mat_line


def accept(avg, best_avg, start_ind, ind, hook_order):
    return avg > best_avg \
                       and np.sort([start_ind, ind]).tolist() \
                       not in np.sort(hook_order, axis=0).tolist()


def string_avg(img, circle, start_ind, ind):
    line_mask = mat_line(circle[start_ind, :], circle[ind, :])
    return np.mean(img[line_mask[:, 0], line_mask[:, 1]])


def no_search(start_ind, hook_dist, num_hooks):
    search_frame = [start_ind - hook_dist, start_ind + hook_dist]

    if search_frame[0] < 0:
        return list(
            range(num_hooks + search_frame[0],
                  num_hooks)) + list(range(search_frame[1])) + [start_ind]
    elif search_frame[1] > num_hooks:
        return list(
            range(search_frame[1] - num_hooks
                  )) + list(range(search_frame[0], start_ind)) + [start_ind]
    else:
        return list(range(search_frame[0], search_frame[1])) + [start_ind]


def fit_strings(img, hook_circle, start_ind=42, num_strings=1500, hook_dist=5,
                discount=0.1, random_accept=0):
    hook_order = []
    img = np.abs(img - 1)
    for string_num in range(num_strings):
        print('strings left: {}'.format(
            num_strings - string_num))

        best_avg = 0

        inds_to_search = np.setdiff1d(range(len(hook_circle)), no_search(
            start_ind, hook_dist, len(hook_circle)))

        best_ind = []

        for ind in inds_to_search:
            avg = string_avg(img, hook_circle, start_ind, ind)

            if accept(avg, best_avg, start_ind, ind, hook_order):
                if np.random.random() < random_accept:
                    best_ind = [start_ind, start_ind]
                    while best_ind[1] == start_ind:
                        best_ind = [start_ind,
                                    np.random.randint(0, len(hook_circle))]
                    break
                else:
                    best_avg, best_ind = avg, [start_ind, ind]

        line_mask = mat_line(hook_circle[best_ind[0], :],
                             hook_circle[best_ind[1], :])

        img[line_mask[:, 0], line_mask[:, 1]] *= discount

        hook_order.append(best_ind)
        start_ind = best_ind[1]

    return hook_order

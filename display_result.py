import argparse

import matplotlib.pylab as plt

from knit_portrait.IO import load_string_order, load_config
from knit_portrait.image_processing import pre_proc_img, make_circle, \
    make_rectangle


def sign(number):
    return ((number > 0) + 0) - ((number < 0) + 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-st', '--strings', default=-1, type=int,
                        help='number of precomputed strings - set to -1 to '
                             'show all precomputed strings (default=-1)')

    parser.add_argument('-r', '--radius', default=250, type=int,
                        help='radius in mm (default=250)')

    parser.add_argument('-d', '--dpi', default=300, type=int,
                        help='resolution of output image (default=300)')

    parser.add_argument('-l', '--line', default=0.05, type=float,
                        help='line thickness (default=0.05)')

    parser.add_argument('-c', '--color', default='black', type=str,
                        help='line color (default=black)')

    parser.add_argument('-b', '--background', default='white', type=str,
                        help='background color (default=white)')

    parser.add_argument('config_file')

    args = parser.parse_args()

    config = load_config(filename=args.config_file)
    string_order = load_string_order(
        filename=config['settings']['save_file'] + '.csv')[:, 1:]

    if args.strings == -1:
        num_strings = config['settings']['strings']
    else:
        num_strings = args.strings
    ref_img = pre_proc_img(config['image']['file'],
                           config['image']['size'], 1,
                           rectangle=config['settings']['rectangle'])
    if config['settings']['rectangle']:
        shape, num_hooks = make_rectangle(
            tuple([val - 1 for val in ref_img.shape]),
            num_hooks=config['settings']['hooks'])
        config['settings']['hooks'] = num_hooks
    else:
        shape = make_circle(
            ref_img.shape, num_hooks=config['settings']['hooks'])

    plt.figure(figsize=(16, 9), facecolor=args.background)
    plt.subplot(121)
    plt.imshow(ref_img, 'gray')
    plt.axis('off')

    plt.subplot(122)
    string_length = 0

    for string_pair in string_order[:num_strings, :]:
        plt.plot([shape[string_pair[0], 1], shape[string_pair[1], 1]],
                 [shape[string_pair[0], 0], shape[string_pair[1], 0]],
                 args.color, LineWidth=args.line)
        plt.gca()
        string_length += ((shape[string_pair[0], 1] - shape[
            string_pair[1], 1]) ** 2 + (
                shape[string_pair[0], 0] - shape[string_pair[1], 0]) ** 2
                          ) ** 0.5 / config['image']['size'] * 2 * args.radius
    plt.axis('equal')
    plt.axis('off')
    plt.gca().invert_yaxis()
    plt.savefig(
        config['settings']['save_file'] + '_result_{}.jpg'.format(num_strings),
        dpi=args.dpi, facecolor=args.background)
    plt.show()
    print('A radius of {} mm, using {} strings, '
          'will require {} m string'.format(args.radius,
                                            num_strings, string_length / 1000))

    plt.figure(figsize=(16, 9))
    for number, hook in enumerate(shape):
        plt.scatter(hook[0] - config['image']['size'] / 2,
                    hook[1] - config['image']['size'] / 2,
                    c='black', marker='x')
        textx = hook[0] - config['image']['size'] / 2
        texty = hook[1] - config['image']['size'] / 2

        checked = False
        rotation = 0
        threshold = 1 - 1 / config['settings']['hooks'] * 4

        if (texty >= (config['image']['size'] / 2 * threshold)) | (
                texty <= (-config['image']['size'] / 2 * threshold)):
            texty *= 1.05
            rotation = 90
            checked = True

        if ((textx >= (config['image']['size'] / 2 * threshold)) | (
                textx <= (-config['image']['size'] / 2 * threshold))) & (
                not checked):
            textx *= 1.05
            rotation = 0

        plt.text(textx, texty, number, fontsize='xx-small', ha='center',
                 va='center', rotation=rotation)
    plt.axis('equal')
    plt.axis('off')
    plt.gca().invert_yaxis()
    plt.savefig(
        config['settings']['save_file'] + '_result_{}_drill_'
                                          'template.jpg'.format(num_strings),
        dpi=args.dpi, facecolor=args.background)
    plt.show()


if __name__ == '__main__':
    main()

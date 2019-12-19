import matplotlib.pylab as plt
from string_portrait.IO import load_string_order, load_config
from string_portrait.image_processing import pre_proc_img, make_circle
import argparse


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-st', '--strings', default=-1, type=int,
                        help='number of precomputed strings - set to -1 to show all precomputed strings (default=-1)')

    parser.add_argument('config_file')

    args = parser.parse_args()

    config = load_config(filename=args.config_file)
    string_order = load_string_order(filename=config['settings']['save_file'] + '.csv')[:, 1:]

    if args.strings == -1:
        num_strings = config['settings']['strings']
    else:
        num_strings = args.strings

    ref_img = pre_proc_img(config['image']['file'], config['image']['size'], 1)
    circle = make_circle(ref_img, num_hooks=config['settings']['hooks'])

    plt.figure(figsize=(16, 9))
    plt.subplot(121)
    plt.imshow(ref_img, 'gray')
    plt.axis('off')

    plt.subplot(122)
    for string_pair in string_order[:num_strings, :]:
        plt.plot([circle[string_pair[0], 1], circle[string_pair[1], 1]],
                 [circle[string_pair[0], 0], circle[string_pair[1], 0]], 'black', LineWidth=0.05)
        plt.gca()

    plt.axis('equal')
    plt.axis('off')
    plt.gca().invert_yaxis()
    plt.savefig(config['settings']['save_file'] + '_result.jpg')
    plt.show()


if __name__ == '__main__':
    main()

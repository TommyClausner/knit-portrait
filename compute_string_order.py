from string_portrait.image_processing import pre_proc_img, make_circle
from string_portrait.optimize import fit_strings
from string_portrait.IO import save_string_order, save_config
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', default='./tommy.jpg', type=str,
                        help='image to process')

    parser.add_argument('-sa', '--save_as', default='./tommy', type=str,
                        help='image to process')

    parser.add_argument('-s', '--size', default=2500, type=int,
                        help='new size in pixel of the input image (default=2500)')

    parser.add_argument('-cf', '--crop_factor', default=1., type=float,
                        help='crop image in every direction by this factor (default=1)')

    parser.add_argument('-st', '--strings', default=5000, type=int,
                        help='number of precomputed strings (default=5000)')

    parser.add_argument('-ho', '--hooks', default=201, type=int,
                        help='number of hooks (default=201)')

    parser.add_argument('-d', '--discount', default=0.3, type=float,
                        help='discount each selected line of the original image by multiplying with this value '
                             '(default=0.3)')

    parser.add_argument('-nd', '--neighbor_distance', default=15, type=int,
                        help='minimum hook distance (default=15)')

    parser.add_argument('-r', '--random_accept_rate', default=0, type=float,
                        help='randomly make a tring with this probability (default=0)')

    args = parser.parse_args()

    config = {'image': {'file': args.file, 'size': args.size, 'crop_factor': args.crop_factor},
              'settings': {'hooks': args.hooks, 'strings': args.strings, 'discount': args.discount,
                           'distance': args.neighbor_distance, 'random_accept': args.random_accept_rate,
                           'save_file': args.save_as}}

    ref_img = pre_proc_img(args.file, args.size, args.crop_factor)
    circle = make_circle(ref_img, num_hooks=args.hooks)

    string_order = fit_strings(
        ref_img,
        circle,
        hook_dist=args.neighbor_distance,
        discount=args.discount,
        num_strings=args.strings,
        random_accept=args.random_accept_rate)

    save_string_order(string_order, filename=args.save_as + '.csv')

    save_config(config, filename=args.save_as + '.json')


if __name__ == '__main__':
    main()

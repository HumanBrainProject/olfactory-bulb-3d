import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Olfactory-bulb-3d model simulation.')
    parser.add_argument('--tstop', type=float, metavar='TIME', default=1050.,
                        help='Simulation time (ms)')
    parser.add_argument('--coreneuron', action='store_true', default=False,
                        help='Enable CoreNEURON simulation')
    parser.add_argument('--gpu', action='store_true', default=False,
                        help='Enable GPU execution with CoreNEURON')
    parser.add_argument('--filemode', action='store_true', default=False,
                        help='Enable filemode execution of CoreNEURON')
    parser.add_argument('--filename', type=str, metavar='NAME', default='olfactory_bulb',
                        help='Output prefix (str)')
    args, _ = parser.parse_known_args()
    if args.gpu and not args.coreneuron:
        args.coreneuron = True
        print("[Warning] --gpu option was given. Enabling automatically CoreNEURON execution")
    if args.filemode and not args.coreneuron:
        args.coreneuron = True
        print("[Warning] --filemode option was given. Enabling automatically CoreNEURON execution")
    return args

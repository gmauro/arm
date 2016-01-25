import argparse
import os
import shutil
import subprocess
import sys

def make_parser():
    parser = argparse.ArgumentParser(description='dvd_utils_launcher')
    parser.add_argument('--action', type=str, choices=['backup', 'ripping'],
                        help='actions', required=True)
    parser.add_argument('--source_drive', type=str, default='/dev/sr0',
                        help='source drive path (default /dev/sr0)')
    parser.add_argument('--output_dir', type=str, help='Output dir path',
                        default="~/tmp")
    parser.add_argument('--config_file', type=str, default='dvdul.conf')
    parser.add_argument('--handbrake_preset', type=str, default='AppleTV 3',
                        help='HandBrake device preset (default AppleTV 3)')
    parser.add_argument('--extension', type=str, default='mkv',
                        help='File container extension (default mkv)')

    return parser


def main(argv):
    def check_if_path_exists(path):
        if not os.path.exists(path):
            print "error {}".format(path)
            sys.exit()

    def proc_to_exec(cmd):
        return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).communicate()[0]

    parser = make_parser()
    args = parser.parse_args(argv)

    output_dir = os.path.expanduser(args.output_dir)

    if args.action == 'backup':
        cmd = "blkid -o value -s LABEL {}".format(args.source_drive)
        dvd_title = proc_to_exec(cmd).strip().replace(' ', '_')
        with open("{}/{}".format(output_dir, args.config_file), 'w') as fp:
            fp.write(dvd_title)

        cmd2 = "dvdbackup -i {} -o {} -M -n {}".format(args.source_drive,
                                                       output_dir,
                                                       dvd_title)
        proc_to_exec(cmd2)

        cmd3 = "eject {}".format(args.source_drive)
        proc_to_exec(cmd3)

    if args.action == 'ripping':
        with open("{}/{}".format(output_dir, args.config_file), 'r') as fp:
            title = fp.readline().strip()
            ipath = "{}/{}".format(output_dir, title)
            ofile = "{}/{}.{}".format(output_dir, title, args.extension)

        cmd = """HandBrakeCLI \
                 -i {} \
                 -o {} \
                 --preset={} \
                 --native-language ita \
                 --native-dub \
                 --audio 1,2,3 \
                 --aencoder copy:ac3 \
                 --audio-fallback ac3
              """.format(ipath, ofile, args.handbrake_preset)
        proc_to_exec(cmd)

        shutil.rmtree("{}".format(ipath))
        os.remove("{}/{}".format(output_dir, args.config_file))

if __name__ == '__main__':
    main(sys.argv[1:])
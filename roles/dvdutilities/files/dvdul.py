import argparse
import os
import shutil
import subprocess
import sys

#SOURCE_DRIVE = '_source_drive'
#OUTPUT_DIR = '_output_dir'
SOURCE_DRIVE = '/dev/sr0'
OUTPUT_DIR = '/home/lgmauro/arm_tmp'


class DvdManager(object):
    def __init__(self, args):
        self.source_drive = args.source_drive
        self.opath = args.output_dir
        self.title = ''

    def _get_title_from_dvd(self):
        cmd = "blkid -o value -s LABEL {}".format(self.source_drive)
        self.title = cmd_to_exec(cmd).strip().replace(' ', '_')

    def backup(self):
        # with open(self.opath, 'w') as fp:
        #     fp.write(self.title)
        self._get_title_from_dvd()
        cmd = "dvdbackup -i {i} -o {o} -M -n {n}".format(i=self.source_drive, o=self.opath, n=self.title)
        print(cmd)
        cmd_to_exec(cmd)
        cmd = "eject {i}".format(i=self.source_drive)
        cmd_to_exec(cmd)


class RippingManager(object):
    def __init__(self, args):
        self.ipath = ''
        self.title = ''
        self.opath = ''
        self.ext = args.extension
        self.preset = args.handbrake_preset

    def _get_title_from_dir(self):
        pass

    def ripping(self):
        self._get_title_from_dir()
        ipath = "{}/{}".format(self.opath, self.title)
        ofile = "{}/{}.{}".format(self.opath, self.title, self.ext)

        cmd = """HandBrakeCLI \
                 -i {} \
                 -o {} \
                 --preset={} \
                 --native-language ita \
                 --native-dub \
                 --audio 1,2,3 \
                 --aencoder copy:ac3 \
                 --audio-fallback ac3
              """.format(ipath, ofile, self.preset)
        cmd_to_exec(cmd)

        shutil.rmtree("{}".format(ipath))
        #os.remove("{}/{}".format(output, config))


def cmd_to_exec(cmd):
    return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).communicate()[0]


def check_if_path_exists(path):
    if not os.path.exists(path):
        print("error {}".format(path))
        sys.exit()


def make_parser():
    parser = argparse.ArgumentParser(description='dvd_utils_launcher')
    parser.add_argument('--action', type=str, help='actions', required=True,
                        choices=['backup', 'ripping', 'bundle'])
    parser.add_argument('--source_drive', type=str, default=SOURCE_DRIVE,
                        help='source drive path (default {})'.format(SOURCE_DRIVE))
    parser.add_argument('--output_dir', type=str, help='Output dir path',
                        default=OUTPUT_DIR)
    parser.add_argument('--handbrake_preset', type=str, default='Fast 1080p30',
                        help='HandBrake device preset (default Fast 1080p30)')
    parser.add_argument('--extension', type=str, default='m4v',
                        help='File container extension (default m4v)')
    return parser


def main(argv):
    parser = make_parser()
    args = parser.parse_args(argv)

    action = args.action

    dm = DvdManager(args=args)

    if action in ['backup', 'bundle']:
        dm.backup()

    if action == 'ripping':
        dm.ripping()

    if action == 'bundle':
        cmd = "docker run -it --rm --name handbrake_gm gmauro/arm --action ripping"
        cmd_to_exec(cmd)


if __name__ == '__main__':
    main(sys.argv[1:])

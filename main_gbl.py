#!usr/bin/env python3

# File: main.py
# Created by: Master
# Date: 10/16/2022 at 7:44 PM

import argparse
import os
import glob
import struct
import io

import gbl

PADDING = b'<Align> '  # Yes really...
PADDING_ALT = b'\x83\x5F\x83\x7E\x81\x5B\x82\xE6'

# RANT
# 2 different teams made the BANK_X.SND and XXX.ACF files
# You can tell because they use 2 different styles of padding and standards
# .SND uses PADDING_ALT and pads the entire file to 2048
# but .ACF uses PADDING and doesn't pad the entire file to 2048
# I'm fucking confused, and these files are not very consistent
# Just Japanese dev things, I guess


def extract(fp_gbl, out_dir: str):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        pass
    elif os.path.exists(out_dir) and not os.path.isdir(out_dir):
        print(f'File path \"{out_dir}\" is not a directory!')
        return

    with open(fp_gbl, mode='rb+') as io_gbl:
        print(f'Reading file \"{io_gbl.name}\"...')
        _gbl = gbl.Gbl.from_io(io_gbl)
        print(f'Found {_gbl.num_entries} entries!')
        for i in range(len(_gbl.entries)):
            data = _gbl.entries[i].data

            fp_i = os.path.join(out_dir, str(i).zfill(3))
            assume_fe = ''  # empty by default
            if data.startswith(b'\x10\x00\x00\x00'):  # TIM
                assume_fe = '.TIM'
                pass
            elif data.startswith(b'XMD\x00'):  # wtf is this
                assume_fe = '.XMD'
                pass
            elif data.startswith(b'SCN\x00'):  # scenario script?
                assume_fe = '.SCN'
                pass
            elif data.startswith(b'SPR2'):  # sprite file - https://ffhacktics.com/smf/index.php?topic=126.0
                assume_fe = '.SPR2'
                pass
            elif data.startswith(b'VHS\x00'):  # contains pBAV .VAB
                assume_fe = '.VHS'
                pass

            fp_i += assume_fe

            if not os.path.exists(fp_i):
                mode = 'x'
                pass
            else:
                mode = 'w+'
                pass

            with open(fp_i, mode=f'{mode}b') as io_i:
                io_i.write(data)
                pass
            continue
        print('Done reading file\n')
        pass
    return


def extract_all(dir_gbl: str, dir_output: str):
    for i in glob.glob('*', root_dir=dir_gbl, recursive=True):
        fp_gbl = os.path.join(dir_gbl, i)
        if i[-4] == '.':  # .ACF or .SND - doesn't matter, we expect either one
            fldr = i[:-4]
            dir_out = os.path.join(dir_output, fldr)
            pass
        else:
            print(f'Unexpected file \"{fp_gbl}\"!')
            continue
        extract(fp_gbl, dir_out)
        continue
    return


def pad(bytes_io: io.BytesIO, alt_padding: bool = False):  # pad to 2048-factor / cd sector size
    if alt_padding:  # used for BANK_X.SND files... idk why, don't ask...
        padding = PADDING_ALT
        pass
    else:
        padding = PADDING
        pass
    i = 0
    while (bytes_io.tell() % 2048) != 0:  # pad for 2048
        bytes_io.write(padding[i].to_bytes())
        i += 1
        if i == len(padding):
            i = 0
            pass
        continue
    return


def create(dir_src: str, fp_create: str):
    print(f'Reading directory \"{dir_src[:-1]}\"...')
    all_files = []
    for i in glob.glob(f'{dir_src}{os.path.sep}*', recursive=False):
        all_files.append(i)
        continue

    print(f'Found {len(all_files)} entries')

    alt_padding = False
    if os.path.basename(dir_src[:-1]).startswith('BANK_'):
        alt_padding = True  # WTF
        pass

    bytes_gbl = io.BytesIO()
    bytes_gbl.write(struct.pack('<I', len(all_files)))

    offset_entries = bytes_gbl.tell()  # come back to actually write offset and lens
    bytes_gbl.write(bytes([1]*((4+4)*len(all_files))))  # (offset+len_data)*num_entries
    pad(bytes_gbl, alt_padding=alt_padding)  # pad header - don't know why, just how it does it

    for i in range(len(all_files)):
        file = all_files[i]
        with open(file, mode='rb+') as io_file:
            file_data = io_file.read()
            pass
        offset_data = bytes_gbl.tell()
        bytes_gbl.write(file_data)
        if i < len(all_files)-1:  # do not pad last entry (for whatever reason)
            pad(bytes_gbl, alt_padding=alt_padding)  # pad file to 2048-factor
            pass
        offset_orig = bytes_gbl.tell()

        # jump to entry in header
        bytes_gbl.seek(offset_entries+(8*i), io.SEEK_SET)
        bytes_gbl.write(struct.pack('<I', offset_data))  # write data offset
        bytes_gbl.write(struct.pack('<I', len(file_data)))  # write data length

        # jump back to original point
        bytes_gbl.seek(offset_orig)
        continue

    if alt_padding:  # this is fucking stupid
        pad(bytes_gbl, alt_padding=True)
        pass

    assume_ext = '.ACF'
    if alt_padding:
        assume_ext = '.SND'
        pass

    if len(assume_ext) > 0 and not fp_create.endswith(assume_ext):
        fp = f'{fp_create}{assume_ext.upper()}'
        pass
    else:
        fp = fp_create
        pass

    if not os.path.exists(fp):
        mode = 'x'
        pass
    else:
        mode = 'w+'
        pass
    with open(fp, mode=f'{mode}b') as io_create:
        bytes_gbl.seek(0, io.SEEK_SET)
        io_create.write(bytes_gbl.read())
        pass

    print(f'Wrote file \"{fp}\"\n')
    return


def create_all(dir_in: str, dir_out: str):
    if not os.path.exists(dir_out):
        print(f'Directory \"{dir_out}\" does not exist... creating...')
        os.makedirs(dir_out)
        print('Created\n')
        pass

    for i in glob.glob(f'*{os.path.sep}', root_dir=dir_in):
        create(os.path.join(dir_in, i), os.path.join(dir_out, i[:-1]))
        continue
    return


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--input', required=True)
    arg_parser.add_argument('--output', required=True)
    arg_parser.add_argument('--mode', required=True, type=str.lower, choices=['extract', 'create'])
    args = arg_parser.parse_args()

    if not os.path.exists(args.input):
        print(f'Given input \"{args.input}\" does not exist!')
        return
    if args.mode == 'extract':
        if os.path.isdir(args.input):
            if os.path.exists(args.output) and not os.path.isdir(args.output):
                print(f'Given output \"{args.output}\" is not also a directory!')
                return
            extract_all(args.input, args.output)
            pass
        elif os.path.isfile(args.input):
            if os.path.exists(args.output) and not os.path.isdir(args.output):
                print(f'Given output \"{args.output}\" is not a directory!')
                return
            extract(args.input, args.output)
            pass
        pass
    elif args.mode == 'create':
        if not os.path.isdir(args.input):
            print(f'Given input \"{args.input}\" is not a directory!')
            return

        peek_d = glob.glob(f'*{os.path.sep}', root_dir=args.input)
        if len(peek_d) > 0:  # directory containing extracted folders
            create_all(args.input, args.output)
            pass
        else:
            create(args.input, args.output)
            pass

        pass
    return


if __name__ == '__main__':
    main()
    pass

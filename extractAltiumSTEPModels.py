#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2020年2月18日
@author: Owen
@site: https://github.com/xiang1030 , http://git.splnet.cc:81/wcx/extractAltiumSTEPModels
@email: 1670980619@qq.com
@file: extractAltiumSTEPModels
@description: Get a 3D model (STEP format) from an Altium PCB project
WARNING: This is a PoC so you must use it in your own risk.
"""


import zlib
import sys
import os
from pathlib import Path
import argparse
import logging


class Prepare_Files(object):
    def __init__(self):
        self.target_steps_dir = Path(Path.cwd()).joinpath("steps_dir")
        self.target_dat_file = "./temp/0.dat"
        self.models_dir = "Models"
        self.target_dat_file_list = []
        self.bat_byte = b'x\x9c'

    def mk_steps_dir(self, input_steps_dir=None):
        if Path(input_steps_dir).is_dir():
            try:
                self.target_steps_dir = input_steps_dir
                logging.debug("mk_steps_dir():input_steps_dir[%s] exist." % self.target_steps_dir)
            except Exception as mk_steps_dir_isdir:
                logging.error('[%r] mk_steps_dir():target_steps_dir.' % mk_steps_dir_isdir)

        else:
            try:
                Path(self.target_steps_dir).mkdir(parents=True, exist_ok=True)
                logging.info("mk_steps_dir():target_steps_dir:%r" % self.target_steps_dir)
            except Exception as mk_steps_dir_mkdir:
                logging.error('[%r] mk_steps_dir():target_steps_dir %s.' % (mk_steps_dir_mkdir, self.target_steps_dir))

    def check_input_file(self, input_file):
        try:
            with open(input_file, 'rb') as file_temp:
                file_byte = file_temp.read(2)
                if file_byte == self.bat_byte:
                    logging.debug("check_input_file:%s is dat" % input_file)
                    return True
                else:
                    logging.debug("check_input_file:%s is not dat" % input_file)
                    return False
        except Exception as check_input_file_byte:
            logging.error('[%r] check_input_file():' % check_input_file_byte)

    def find_Models_dat(self, input_target_dat_file=None, input_models_dir=None):
        if input_target_dat_file is not None:
            self.target_dat_file = input_target_dat_file
            logging.debug('find_Models_dat():target_dat_file[%r]' % self.target_dat_file)
        if input_models_dir is not None:
            self.models_dir = input_models_dir
            logging.debug('find_Models_dat():models_dir[%r]' % self.models_dir)

        try:
            if Path(self.target_dat_file).exists():
                logging.debug('find_Models_dat():[%r] exist' % self.target_dat_file)
            else:
                logging.error('find_Models_dat():[%r] not exist' % self.target_dat_file)
        except Exception as find_Models_dat_exists:
            logging.error('[%r] find_Models_dat():[%r] not exist' % (find_Models_dat_exists, self.target_dat_file))

        try:
            if Path(self.target_dat_file).is_file():
                check_flag = self.check_input_file(self.target_dat_file)
                if check_flag:
                    self.target_dat_file_list.append(self.target_dat_file)
        except Exception as e:
            logging.warning('[%r] find_Models_dat():is_file' % e)

        try:
            if Path(self.target_dat_file).is_dir():
                for home, dirs, files in os.walk(self.target_dat_file):
                    if Path(home).parts[-1] == self.models_dir:
                        logging.debug("Models:dir:%s" % home)
                        for dat_file in files:
                            dat_file = Path(home).joinpath(dat_file)
                            logging.debug("Models:dat_file:%s" % dat_file)
                            check_flag = self.check_input_file(dat_file)
                            if check_flag:
                                self.target_dat_file_list.append(dat_file)

        except Exception as e:
            logging.error('[%r]find_Models_dat():is_dir' % e)


class  Extract_Altium_STEP_Models(object):
    def __init__(self):
        self.data_null = ""

    def determin_data_null(self):
        if sys.version_info >= (3,):
            self.data_null = b""
        else:
            self.data_null = ""

    def file_decompress(self, dat_file_path="./temp/0.dat", step_file_dir=None, step_file_name=None, read_buf_size=4096):
        self.determin_data_null()

        if step_file_name is None:
            step_file_name = Path(dat_file_path).stem + ".step"
        else:
            step_file_name = step_file_name + ".step"

        if step_file_dir is None:
            step_file_dir = Path(dat_file_path).parent

        step_file_path = Path(step_file_dir).joinpath(step_file_name)
        logging.debug("file_decompress:dat_file_path:(%s) Extracted step_file_path:(%s)" % (dat_file_path, step_file_path))

        try:
            # Open binary file for reading
            open_binary_file = open(dat_file_path, "rb")
        except Exception as e:
            logging.error('[%s] file_decompress():Open file:' % e)

        try:
            # Create a file for writing STEP data
            open_step_file = open(step_file_path, "wb")
        except Exception as e:
            logging.error('[%s] file_decompress():Create file:' % e)

        else:
            zlib_decompressobj = zlib.decompressobj()
            while True:
                zlib_data = zlib_decompressobj.unconsumed_tail
                if zlib_data == self.data_null:
                    zlib_data = open_binary_file.read(read_buf_size)
                    if zlib_data == self.data_null:
                        break
                zlib_inflate_data = zlib_decompressobj.decompress(zlib_data)
                if zlib_inflate_data == self.data_null:
                    break
                open_step_file.write(zlib_inflate_data)

            open_binary_file.close()
            open_step_file.close()
"""
    def file_decompress_other(self, dat_file_path="0.dat", step_file_path="0.step", read_buf_size=4096):
        # Open binary file for reading
        open_binary_file = open(dat_file_path, "rb")

        # Create a file for writing STEP data
        open_step_file = open(step_file_path, "wb")

        zlib_decompressobj = zlib.decompressobj()
        zlib_data = open_binary_file.read(read_buf_size)

        while zlib_data:
            open_step_file.write(zlib_decompressobj.decompress(zlib_data))
            zlib_data = open_binary_file.read(read_buf_size)

        open_step_file.write(zlib_decompressobj.flush())
"""


def main():
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', filename='extractAltiumSTEPModels.log', filemode='w',
                        level=logging.DEBUG)
    prepare_file = Prepare_Files()
    extract = Extract_Altium_STEP_Models()

    parser = argparse.ArgumentParser(description='Extract Altium STEP Models.')
    parser.add_argument("-d", "--dats", type=str, default="./temp/0.dat", help="Dat files path, default='./temp/0.dat'.")
    parser.add_argument("-m", "--models", type=str, default="Models", help="Dat files dir name, default='Models'.")
    parser.add_argument("-s", "--steps",  type=str, default="./steps_dir", help="Extract step files path, default='./steps_dir'.")
    parser.add_argument("-b", "--buffsize", type=int, choices=[1024, 2048, 4096], default=4096, help="Extract files buffsize, default=4096.")
    args = parser.parse_args()

    prepare_file.mk_steps_dir(input_steps_dir=args.steps)
    prepare_file.find_Models_dat(input_target_dat_file=args.dats, input_models_dir=args.models)
    logging.debug("prepare_file--target_dat_file_list: %s" % prepare_file.target_dat_file_list)
    for dat_file in prepare_file.target_dat_file_list:
        extract.file_decompress(dat_file_path=dat_file, step_file_dir=prepare_file.target_steps_dir, read_buf_size=args.buffsize)

    logging.debug("end....")
    sys.exit()


if __name__ == "__main__":
    main()



# Needed items:
# Python
#  - typing 
#     python --version
#    onto the command prompt will return informattion
# ffmpeg on path
#  - typing 
#     ffmpeg
#    onto the command prompt will return informattion
# ffprobe on path
#  - typing 
#     ffprobe
#    onto the command prompt will return informattion

# An example directory structure looks like this:
# project
#    \___ original_input.mp4 (original video)
#    \___ original_input.mp4_orig_audio.m4a (ffmpeg creates this audio file if needed)
#    \___ original_input.mp4_ebsynthed.mp4 (ffmpeg creates this file from the ebsynth_out directory)
#
#  |___ ffmpeg_extracted_frames (ffmpeg fills with frames)
#            \___ 00001.png
#            \___ ......png
#            \___ 00646.png (or however many frames)
#
#  |____ ebsynth_output (create this manually, set as output on ebsynth, ebsynth will fill with frames)
#            \___ 00001.png
#            \___ ......png
#            \___ 00646.png (or however many frames)


import os
import subprocess
import sys
import glob
import re
import configparser
import time

from pathlib import Path
from decimal import Decimal
from os.path import exists


# Will be adding a config reader here in the future
#config = configparser.ConfigParser()
#config.read('FILE.INI')

skip_frame_extraction = False
use_text_file_for_frame_list = False
force_attempt_to_create_video_even_if_no_first_frame = True

base_directory = "C:\\ebsynth_project\\"
video_filename = "original_input.mp4"

original_video_pull_frames_from = ""

# if we have a parameter on the command line, take it as the input video if a file, take as base directory if directory
if (len(sys.argv) > 1):
    path = sys.argv[1]
    print("Command line parameter:" + path)
    is_exist = os.path.exists(path)
    if (is_exist):
        if (os.path.isfile(path)):
            print("This parameter is going to be taken as the original video")
            base_directory = os.path.dirname(path) + "\\"
            original_video_pull_frames_from = path
        if (os.path.isdir(path)):
            print("This parameter is going to be taken as the base directory for the original video")
            if (not path.endswith("\\")):
                path = path + "\\"
            base_directory = path
            # search the directory. We are expecting to find a single file
            # Get list of all files only in the given directory
            list_of_files = filter( lambda x: os.path.isfile(os.path.join(base_directory, x)), os.listdir(base_directory) )
            # Sort list of files based on last modification time in ascending order
            list_of_files = sorted( list_of_files, key = lambda x: os.path.getmtime(os.path.join(base_directory, x)))
            # if there's multiple files, order by time, and take the first one that ffprobe thinks has a width
            for my_file in list_of_files:
              print("Checking if file is video:" + my_file)
              ffprobe_width = subprocess.getoutput('ffprobe -v error -select_streams v -show_entries stream=width -of csv=p=0:s=x "'+base_directory+my_file+'"')
              if (len(ffprobe_width) > 0):
                  if debug: print("ffprobe_width:=="+ffprobe_width+"==")
                  original_video_pull_frames_from = base_directory+my_file
                  break
            print("Done checking for video files in directory:"+ base_directory)
    else:
        print ("Parameter should be a base directory or a video filename, this parameter was not on the file system")
else:
  original_video_pull_frames_from = base_directory + video_filename

if (original_video_pull_frames_from == ""):
    print("Could not find the video to pull frames from!")
    sys.exit("No video, cannot continue")

print("Proceeding with the following:")
print("Base directory: "+base_directory)
print("Input video:    "+original_video_pull_frames_from)

# The video will either be:
# - created entirely from frames and the original audio from the original video (frames_to_create_new_video is NOT empty string "")
# - overlay a set of frames over the original video - (frames_to_overlay_over_original_video is NOT empty string "")

frames_to_create_new_video = ""
frames_to_overlay_over_original_video = ""
frames_to_overlay_over_original_video = base_directory + "\\ebsynth_output\\%05d.png"


numbering_for_new_frames = "%05d"

debug = True
#debug = False


#sys.exit()

#rename for use below
output_pngs = frames_to_create_new_video
my_file = original_video_pull_frames_from

ffprobe_framerate = subprocess.getoutput('ffprobe -v error -select_streams v -show_entries stream=r_frame_rate -of csv=p=0:s=x "'+my_file+'"')

if False:
  ffprobe_height = subprocess.getoutput('ffprobe -v error -select_streams v -show_entries stream=height -of csv=p=0:s=x "'+my_file+'"')
  print("Height:",ffprobe_height)
  ffprobe_height_decimal = Decimal(ffprobe_height)
  for divisor in range(1,33):
    ffprobe_height_check = ffprobe_height_decimal / (divisor)
    print("Height of ",divisor," :",ffprobe_height_check)
  ffprobe_width = subprocess.getoutput('ffprobe -v error -select_streams v -show_entries stream=width -of csv=p=0:s=x "'+my_file+'"')
  ffprobe_width_decimal = Decimal(ffprobe_width)
  for divisor in range(1,33):
    ffprobe_width_check = ffprobe_width_decimal / (divisor)
    print("Width of ",divisor," :",ffprobe_width_check)
print("======Audio Extraction=============")
if (len(frames_to_create_new_video) > 0):
  if not exists(my_file+'_orig_audio.m4a'):
    extract_audio_output = subprocess.getoutput('ffmpeg -hide_banner -n -i "'+my_file+'" -map 0:a "'+my_file+'_orig_audio.m4a')
    print("Audio output:" + extract_audio_output)
    print("===================")
  else:
    print("Audio extracted already")
else:
  print("Audio extraction skipped, overlaying frames will not require extracting audio")
print("===================")
print("======Frame Extraction=============")
if not skip_frame_extraction:
  #see if the ffmpeg_extracted_frames directory exists
  ffmpeg_extracted_frames_dir = base_directory+"ffmpeg_extracted_frames"
  if exists(ffmpeg_extracted_frames_dir):
    if debug: print("frame extraction dir exists:" + ffmpeg_extracted_frames_dir);
  else:
    if debug: print("creating frame extraction dir that DOES NOT YET exist: '" + ffmpeg_extracted_frames_dir + "'");
    os.mkdir(ffmpeg_extracted_frames_dir);
    if debug: print("created frame extraction dir");
  check_for_filename = ffmpeg_extracted_frames_dir+'\\00001.png'
  if not exists(check_for_filename):
    frame_output_filenames = ffmpeg_extracted_frames_dir+'\\'+numbering_for_new_frames+'.png'
    extract_frames_output = subprocess.getoutput('ffmpeg -hide_banner -n -i "'+my_file+'" "'+frame_output_filenames+'"')
    print("Frames output:" + extract_frames_output)
  else:
      print("Looks like frames have already been extracted: '"+check_for_filename+"'")
else:
  print("Frame extraction skipped")
print("===================")
print("===================")
if use_text_file_for_frame_list:
        print("Using text file for frame list:"+output_pngs)
        ffmpeg_command = 'ffmpeg -framerate '+ffprobe_framerate+' -hide_banner -n -f concat -safe 0 -i "'+output_pngs+'" -i "'+my_file+'_orig_audio.m4a" -c:v libx264 -pix_fmt yuv420p -r '+ffprobe_framerate+' "'+my_file+'_ebsynthed.mp4"'
        print("Running command:")
        print(ffmpeg_command)
        create_video_output = subprocess.getoutput(ffmpeg_command)
        print("Create video output:" + create_video_output)
        print("Final Video (if created):"+my_file+'_ebsynthed.mp4')
elif (len(frames_to_create_new_video) > 0):
    print("Forcing to create even if we cannot find first frame? " + f'{force_attempt_to_create_video_even_if_no_first_frame}')

    if exists(output_pngs.replace(numbering_for_new_frames, "00001")) or force_attempt_to_create_video_even_if_no_first_frame:
        matching_files = glob.glob(frames_to_create_new_video.replace(numbering_for_new_frames,"*"))
        if debug: print("Num matching files:")
        if debug: print(len(matching_files))
        if len(matching_files) > 0:
            matching_files.sort()
            if debug: print("file:")
            first_file = matching_files[0]
            if debug: print(first_file)
            match_parts = re.split(numbering_for_new_frames, frames_to_create_new_video)
            if debug: print(match_parts)
            initial_number_of_file = first_file
            for token_mp in match_parts:
                initial_number_of_file = initial_number_of_file.replace(token_mp,"")
            if debug: print(initial_number_of_file)
            int_initial_number_of_file = int(initial_number_of_file)
            if debug: print(int_initial_number_of_file)

            print("Using frame files with wildcard "+numbering_for_new_frames+":"+output_pngs)
            output_filename = my_file+'_ebsynthed.mp4'
            ffmpeg_command = 'ffmpeg -framerate '+ffprobe_framerate+' -hide_banner -n -start_number '+str(int_initial_number_of_file)+' -i "'+output_pngs+'" -i "'+my_file+'_orig_audio.m4a" -c:v libx264 -pix_fmt yuva420p -r '+ffprobe_framerate+' "'+output_filename+'"'
            print("Running command:")
            print(ffmpeg_command)
            create_video_output = subprocess.getoutput(ffmpeg_command)
            print("Create video output:" + create_video_output)
            print("Final Video (if created):"+output_filename)
        else:
            print("Instruction said to force creation, but could not find the files: '" + frames_to_create_new_video +"'")
            if (len(frames_to_create_new_video) == 0): print("Frame listing is the empty string")
    else:
        print("Looks like the updated frames have not been created yet: '"+output_pngs.replace(numbering_for_new_frames, "00001")+"'")
elif (len(frames_to_overlay_over_original_video) > 0):
    print("Attempting to overlay frames over original video")
    output_filename = my_file+'ebsynthed_with_overlay.mp4'
    ffmpeg_command = 'ffmpeg -i '+original_video_pull_frames_from+' -framerate '+ffprobe_framerate+' -i "'+frames_to_overlay_over_original_video+'" -filter_complex "[1:v][0:v]scale2ref=iw:ih[ovr][base];  [ovr]colorchannelmixer=aa=1.0[ovrl]; [base][ovrl]overlay[v]" -map [v] -map 0:a ' + output_filename
    print("Running command:")
    print(ffmpeg_command)
    create_video_output = subprocess.getoutput(ffmpeg_command)
    print("Create video output:" + create_video_output)
    print("Final Video (if created):"+output_filename)
else:
    print ("Seems like we has empty string for both a list of frames, and a list of overlays for frames")

print("===================")
print("===================")
print("done")

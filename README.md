# For use with ebsynth, use the script to extract frames, you'll manually run ebsynth, and then use the script to create a final video
 Needed items:
 - Python
 https://www.python.org/downloads/
  typing 
     python --version
    onto the command prompt will return information
 - ffmpeg on path
 https://ffmpeg.org/download.html
  typing 
     ffmpeg
    onto the command prompt will return information
 - ffprobe on path
 Comes with ffmpeg usually
  typing 
     ffprobe
    onto the command prompt will return information

 Example Use:
 ```
 > python ebsynth_helper.py C:\Videos\subfolderformyvideo\myvideo.mp4
 ```
 Create a keyframe for ebsynth
 Create the subdirectory C:\Videos\subfolderformyvideo\ebsynth_output
 Run ebsynth, with all output frames going to ebsynth_output
 ```
 > python ebsynth_helper.py C:\Videos\subfolderformyvideo\myvideo.mp4
 ```
 -- this is the same command as before --

 An example directory structure looks like this:
```
 project
    \___ original_input.mp4 (original video)
    \___ original_input.mp4_orig_audio.m4a (ffmpeg creates this audio file if needed)
    \___ original_input.mp4_ebsynthed.mp4 (ffmpeg creates this file from the ebsynth_out directory)

  |___ ffmpeg_extracted_frames (ffmpeg fills with frames)
            \___ 00001.png
            \___ ......png
            \___ 00646.png (or however many frames)

  |____ ebsynth_output (create this manually, set as output on ebsynth, ebsynth will fill with frames)
            \___ 00001.png
            \___ ......png
            \___ 00646.png (or however many frames)
```
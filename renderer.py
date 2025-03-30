import moviepy.editor as mp
from os.path import join, exists
import multiprocessing
import gc
from typing import List, Dict
from settings import FULL_HD
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_block_clips(
    blocks: List[Dict],
    output_dir: str,
    pack_name: str,
    processes: int = None
) -> None:
    """Render composite video clips for blocks of simultaneous notes."""
    processes = processes or multiprocessing.cpu_count()
    
    if not blocks:
        logger.warning("No blocks to render")
        return

    if not exists(output_dir):
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
    if not exists(pack_name):
        raise FileNotFoundError(f"Pack directory does not exist: {pack_name}")

    with multiprocessing.Pool(processes=min(processes, len(blocks))) as pool:
        tasks = [(block, output_dir, pack_name) for block in blocks]
        try:
            pool.starmap(_render_single_block, tasks)
        except Exception as e:
            logger.error(f"Error during block rendering: {str(e)}")
            raise
        finally:
            gc.collect()

def render_script_clips(
    script_list: List[List[Dict]],
    output_dir: str,
    pack_name: str,
    processes: int = None
) -> None:
    """Render script clips using multiprocessing."""
    processes = processes or max(1, multiprocessing.cpu_count() // 4)
    
    if not script_list:
        logger.warning("No script segments to render")
        return

    if not exists(output_dir):
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
    if not exists(pack_name):
        raise FileNotFoundError(f"Pack directory does not exist: {pack_name}")

    with multiprocessing.Pool(processes=min(processes, len(script_list))) as pool:
        tasks = [(script, output_dir, pack_name) for script in script_list]
        try:
            pool.starmap(_render_script_segment, tasks)
        except Exception as e:
            logger.error(f"Error during script rendering: {str(e)}")
            raise
        finally:
            gc.collect()
def _render_single_block(block: Dict, output_dir: str, pack_name: str) -> None:
    """
    Render a single block of notes into a composite video clip.
    
    Args:
        block: Dictionary containing notes and metadata
        output_dir: Directory to save the rendered clip
        pack_name: Path to the pack directory containing note clips
    """
    track = []
    try:
        notes = block.get("notes", [])
        block_index = block.get("index", 0)
        
        if not notes:
            logger.warning(f"Empty block with index {block_index}")
            return

        for i, note in enumerate(notes):
            clip_path = join(pack_name, f"{note}.mp4")
            
            if not exists(clip_path):
                raise FileNotFoundError(f"Note clip not found: {clip_path}")
            
            clip = mp.VideoFileClip(clip_path)
            opacity = (1/len(notes)) * (len(notes) - i)
            track.append(
                clip.subclip(0, clip.duration)
                .set_opacity(opacity)
            )

        # Create and save composite video
        output_path = join(output_dir, f"X{block_index}.mp4")
        video = mp.CompositeVideoClip(track, size=FULL_HD)
        video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            logger=None  # Disable moviepy progress output
        )
        
        logger.info(f"Successfully rendered block X{block_index}")
        
    except Exception as e:
        logger.error(f"Failed to render block X{block_index}: {str(e)}")
        raise
    finally:
        # Clean up resources
        for clip in track:
            clip.close()
        gc.collect()

def _render_script_segment(script: List[Dict], output_dir: str, pack_name: str) -> None:
    """
    Render a single script segment.
    
    Args:
        script: List of note dictionaries in the segment
        output_dir: Directory to save the rendered clip
        pack_name: Path to the pack directory containing note clips
    """
    track = []
    try:
        if not script:
            logger.warning("Empty script segment received")
            return

        start_time = script[0]["time"]
        segment_index = script[0].get("index", 0)

        for note in script:
            note_name = note["note"]
            
            if note_name.startswith('X'):
                clip_path = join(output_dir, f"{note_name}.mp4")
            else:
                clip_path = join(pack_name, f"{note_name}.mp4")
            
            if not exists(clip_path):
                raise FileNotFoundError(f"Clip not found: {clip_path}")
            
            clip = mp.VideoFileClip(clip_path)
            track.append(
                clip.set_start(note["time"] - start_time)
            )

        # Create and save composite video
        output_path = join(output_dir, f"Y{segment_index}.mp4")
        video = mp.CompositeVideoClip(track, size=FULL_HD)
        video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            logger=None  # Disable moviepy progress output
        )
        
        logger.info(f"Successfully rendered script segment Y{segment_index}")
        
    except Exception as e:
        logger.error(f"Failed to render script segment Y{segment_index}: {str(e)}")
        raise
    finally:
        # Clean up resources
        for clip in track:
            clip.close()
        gc.collect()

def render_final(script: List[Dict], output_path: str, clips_dir: str) -> None:
    """
    Render the final composite video from all script segments.
    
    Args:
        script: Final script containing references to all segments
        output_path: Final output file path
        clips_dir: Directory containing rendered segments
    """
    track = []
    try:
        if not script:
            raise ValueError("Empty final script provided")

        if not exists(clips_dir):
            raise FileNotFoundError(f"Clips directory does not exist: {clips_dir}")

        for segment in script:
            clip_path = join(clips_dir, f"{segment['note']}.mp4")
            
            if not exists(clip_path):
                raise FileNotFoundError(f"Segment clip not found: {clip_path}")
            
            clip = mp.VideoFileClip(clip_path)
            track.append(
                clip.set_start(segment["time"])
            )

        # Create and save final video
        video = mp.CompositeVideoClip(track, size=FULL_HD)
        video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            threads=8,
            bitrate="8000k",
            logger=None  # Disable moviepy progress output
        )
        
        logger.info(f"Successfully rendered final video to {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to render final video: {str(e)}")
        raise
    finally:
        # Clean up resources
        for clip in track:
            clip.close()
        gc.collect()
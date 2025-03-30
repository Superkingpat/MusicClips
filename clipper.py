import json
import os
import gc
import logging
from typing import Tuple, List, Dict
from settings import JSONS_PATH, PACK_NAME, BATCH_SIZE
from renderer import render_block_clips, render_final, render_script_clips
from scripter import check_script, optimize_script, split_load

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_script(filename: str) -> List[Dict]:
    """Load script from JSON file with validation"""
    script_path = os.path.join(JSONS_PATH, f"{filename}.json")
    
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script file not found: {script_path}")
    
    try:
        with open(script_path, 'r') as f:
            script = json.load(f)
            
        if not isinstance(script, list):
            raise ValueError("Script should be a list of note dictionaries")
            
        return script
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in script file: {str(e)}")

def process_script(script: List[Dict], project_path: str) -> Tuple[List[Dict], List[Dict], List[List[Dict]]]:
    """
    Process the script through all stages: validation, optimization, and splitting
    
    Args:
        script: The loaded script data
        project_path: Path to the project directory
        
    Returns:
        Tuple containing (final_script, blocks, script_list)
    """
    try:
        # Create scripts directory if it doesn't exist
        scripts_dir = os.path.join(project_path, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Step 1: Check and potentially transpose script
        logger.info("Checking script notes...")
        script = check_script(script, PACK_NAME)
        
        # Step 2: Optimize script (combine simultaneous notes)
        logger.info("Optimizing script...")
        _, optimized_script, blocks = optimize_script(script, PACK_NAME, scripts_dir)
        
        # Step 3: Split into batches for parallel processing
        logger.info("Splitting script for parallel processing...")
        script_list, final_script = split_load(optimized_script, scripts_dir)
        
        return final_script, blocks, script_list
        
    except Exception as e:
        logger.error(f"Script processing failed: {str(e)}")
        raise

def main(project_path: str, filename: str) -> None:
    try:
        logger.info(f"Starting processing for project: {project_path}")
        gc.enable()
        
        # Step 1: Load the script
        script = load_script(filename)
        
        # Step 2: Process the script
        final_script, blocks, script_list = process_script(script, project_path)
        
        # Create help clips directory if it doesn't exist
        help_clips_dir = os.path.join(project_path, "helpClips")
        os.makedirs(help_clips_dir, exist_ok=True)
        
        # Step 3: Render block clips (with correct parameter order)
        logger.info("Rendering block clips...")
        render_block_clips(
            blocks=blocks,
            output_dir=help_clips_dir,
            pack_name=PACK_NAME,
            processes=BATCH_SIZE
        )
        
        # Step 4: Render script clips (with correct parameter order)
        logger.info("Rendering script segments...")
        render_script_clips(
            script_list=script_list,
            output_dir=help_clips_dir,
            pack_name=PACK_NAME,
            processes=max(1, BATCH_SIZE // 4)
        )
        
        # Step 5: Render final composition
        logger.info("Rendering final composition...")
        output_path = os.path.join(project_path, "final_output.mp4")
        render_final(
            script=final_script,
            output_path=output_path,
            clips_dir=help_clips_dir
        )
        
        logger.info("Processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise
    finally:
        gc.collect()

if __name__ == '__main__':
    import argparse
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Process music clips into a video composition.')
    parser.add_argument('project_path', help='Path to the project directory')
    parser.add_argument('filename', help='Name of the script file (without extension)')
    
    args = parser.parse_args()
    
    # Run the main function with command line arguments
    main(args.project_path, args.filename)
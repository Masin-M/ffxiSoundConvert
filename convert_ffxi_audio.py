#!/usr/bin/env python3
"""
FFXI Audio Converter
Converts .bgw and .spw files to .ogg format using vgmstream-cli and ffmpeg

Usage: python3 convert_ffxi_audio.py /path/to/sound/folder
"""

import os
import sys
import subprocess
from pathlib import Path


def find_audio_files(folder: Path) -> list[Path]:
    """Recursively find all .bgw and .spw files"""
    files = []
    for ext in ('*.bgw', '*.spw', '*.BGW', '*.SPW'):
        files.extend(folder.rglob(ext))
    return sorted(files)


def convert_file(input_path: Path, vgmstream_cmd: str = 'vgmstream-cli') -> bool:
    """
    Convert a single .bgw/.spw file to .ogg
    Returns True if successful, False otherwise
    """
    # Build output paths
    wav_path = input_path.with_suffix('.wav')
    ogg_path = input_path.with_suffix('.ogg')
    
    # Skip if .ogg already exists
    if ogg_path.exists():
        print(f"  [SKIP] {ogg_path.name} already exists")
        return True
    
    try:
        # Step 1: Convert to WAV using vgmstream-cli
        result = subprocess.run(
            [vgmstream_cmd, '-o', str(wav_path), str(input_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 or not wav_path.exists():
            print(f"  [FAIL] vgmstream failed: {result.stderr.strip()}")
            return False
        
        # Step 2: Convert WAV to OGG using ffmpeg
        result = subprocess.run(
            ['ffmpeg', '-i', str(wav_path), '-c:a', 'libvorbis', '-q:a', '4', 
             str(ogg_path), '-y', '-loglevel', 'error'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 or not ogg_path.exists():
            print(f"  [FAIL] ffmpeg failed: {result.stderr.strip()}")
            # Clean up wav if ffmpeg failed
            if wav_path.exists():
                wav_path.unlink()
            return False
        
        # Step 3: Delete intermediate WAV file
        wav_path.unlink()
        
        print(f"  [OK] {ogg_path.name}")
        return True
        
    except FileNotFoundError as e:
        print(f"  [ERROR] Command not found: {e.filename}")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        # Clean up any leftover files
        if wav_path.exists():
            wav_path.unlink()
        return False


def main():
    if len(sys.argv) < 2:
        print("FFXI Audio Converter")
        print("====================")
        print()
        print("Converts .bgw and .spw files to .ogg format")
        print()
        print(f"Usage: {sys.argv[0]} <sound_folder> [vgmstream_path]")
        print("Download from: https://github.com/vgmstream/vgmstream/releases")
        print()
        print("Arguments:")
        print("  sound_folder    - Path to FFXI sound folder")
        print("  vgmstream_path  - Optional path to vgmstream-cli (default: vgmstream-cli)")
        print()
        print("Example:")
        print(f"  {sys.argv[0]} '/home/user/FINAL FANTASY XI/sound'")
        print(f"  {sys.argv[0]} '/home/user/FINAL FANTASY XI/sound' ./vgmstream-cli")
        sys.exit(1)
    
    sound_folder = Path(sys.argv[1])
    vgmstream_cmd = sys.argv[2] if len(sys.argv) > 2 else 'vgmstream-cli'
    
    # Validate folder
    if not sound_folder.exists():
        print(f"Error: Folder not found: {sound_folder}")
        sys.exit(1)
    
    if not sound_folder.is_dir():
        print(f"Error: Not a directory: {sound_folder}")
        sys.exit(1)
    
    # Check dependencies
    print("Checking dependencies...")
    
    try:
        subprocess.run([vgmstream_cmd], capture_output=True)
        print(f"  vgmstream-cli: OK ({vgmstream_cmd})")
    except FileNotFoundError:
        print(f"  vgmstream-cli: NOT FOUND")
        print()
        print("Download from: https://github.com/vgmstream/vgmstream/releases")
        print("  - Download vgmstream-linux-cli.tar.gz")
        print("  - Extract and provide path as second argument")
        sys.exit(1)
    
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        print("  ffmpeg: OK")
    except FileNotFoundError:
        print("  ffmpeg: NOT FOUND")
        print()
        print("Install with: sudo apt install ffmpeg")
        sys.exit(1)
    
    print()
    
    # Find all audio files
    print(f"Scanning: {sound_folder}")
    audio_files = find_audio_files(sound_folder)
    
    bgw_count = sum(1 for f in audio_files if f.suffix.lower() == '.bgw')
    spw_count = sum(1 for f in audio_files if f.suffix.lower() == '.spw')
    
    print(f"  Found {bgw_count} .bgw files (music)")
    print(f"  Found {spw_count} .spw files (sound effects)")
    print(f"  Total: {len(audio_files)} files")
    print()
    
    if not audio_files:
        print("No files to convert.")
        sys.exit(0)
    
    # Process files
    print("Converting...")
    print("=" * 50)
    
    converted = 0
    skipped = 0
    failed = 0
    
    for i, input_path in enumerate(audio_files, 1):
        rel_path = input_path.relative_to(sound_folder)
        print(f"[{i}/{len(audio_files)}] {rel_path}")
        
        ogg_path = input_path.with_suffix('.ogg')
        if ogg_path.exists():
            skipped += 1
            print(f"  [SKIP] Already exists")
            continue
        
        if convert_file(input_path, vgmstream_cmd):
            converted += 1
        else:
            failed += 1
    
    # Summary
    print()
    print("=" * 50)
    print("Complete!")
    print(f"  Converted: {converted}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")


if __name__ == '__main__':
    main()

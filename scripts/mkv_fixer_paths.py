"""Script to fix keyframe intervals in MKV video files."""

import os
import subprocess


def get_keyframe_times(video_path: str) -> list[float]:
    """Get keyframe timestamps from video file.

    Args:
        video_path: Path to video file to analyze

    Returns:
        List of keyframe timestamps in seconds
    """
    print(f"🔍 Analyzing keyframes for: {os.path.basename(video_path)}")
    try:
        output = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-skip_frame",
                "nokey",
                "-show_frames",
                "-show_entries",
                "frame=pkt_pts_time",
                "-of",
                "csv=p=0",
                video_path,
            ]
        ).decode()

        times = []
        for line in output.strip().split("\n"):
            line = line.strip()
            if line and line.replace(".", "").replace("-", "").isdigit():
                try:
                    times.append(float(line))
                except ValueError:
                    continue

        print(f"   Found {len(times)} keyframes")
        if times:
            print(
                f"   First keyframe: {times[0]:.2f}s, "
                f"Last keyframe: {times[-1]:.2f}s"
            )
        return times
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to analyze: {video_path}")
        print(f"   Error: {e}")
        return []


def needs_fixing(keyframes: list[float], threshold: float = 5.0) -> bool:
    """Check if video needs keyframe fixing.

    Args:
        keyframes: List of keyframe timestamps
        threshold: Maximum allowed average interval between keyframes

    Returns:
        True if fixing is needed, False otherwise
    """
    if len(keyframes) < 2:
        print(f"   ⚠️  Only {len(keyframes)} keyframe(s) found, needs fixing")
        return True

    intervals = [
        keyframes[i + 1] - keyframes[i] for i in range(len(keyframes) - 1)
    ]
    avg_interval = sum(intervals) / len(intervals)
    print(
        f"   Average keyframe interval: {avg_interval:.2f}s "
        f"(threshold: {threshold}s)"
    )
    return avg_interval > threshold


def fix_keyframes(
    input_path: str, output_path: str, keyframe_interval: int = 5
) -> None:
    """Re-encode video with fixed keyframe intervals.

    Args:
        input_path: Path to input video file
        output_path: Path to save fixed video
        keyframe_interval: Desired interval between keyframes in seconds
    """
    print(
        f"🔧 Re-encoding video only "
        f"(preserving subs/audio/etc): {os.path.basename(input_path)}"
    )

    cmd = [
        "ffmpeg",
        "-i",
        input_path,
        "-map",
        "0",  # keep all streams
        "-c:v",
        "libx264",
        "-x264opts",
        f"keyint={keyframe_interval * 25}:"
        f"min-keyint={keyframe_interval * 25}:scenecut=0",
        "-force_key_frames",
        f"expr:gte(t,n_forced*{keyframe_interval})",
        "-c:a",
        "copy",  # copy audio
        "-c:s",
        "copy",  # copy subtitles
        "-c:d",
        "copy",  # copy data (e.g. chapters)
        "-y",
        output_path,
    ]

    print("   Running: ffmpeg -i [file]... [output hidden]")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print("   ✅ Re-encoding completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Re-encoding failed: {e}")
        raise


def process_folder(
    folder_path: str, output_folder: str = None, keyframe_threshold: int = 5
) -> None:
    """Process all MKV files in a folder.

    Args:
        folder_path: Path to folder containing MKV files
        output_folder: Path to save fixed files (defaults to input folder)
        keyframe_threshold: Maximum allowed keyframe interval in seconds
    """
    if not os.path.isdir(folder_path):
        print("❌ Provided path is not a folder.")
        return

    # Use input folder as output if not specified
    if output_folder is None:
        output_folder = folder_path

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        print(f"📁 Creating output folder: {output_folder}")
        os.makedirs(output_folder)

    mkv_files = [
        f for f in os.listdir(folder_path) if f.lower().endswith(".mkv")
    ]
    if not mkv_files:
        print("ℹ️ No MKV files found in the folder.")
        return

    print(f"📁 Scanning {len(mkv_files)} MKV files in: {folder_path}")
    print(f"📁 Output folder: {output_folder}")
    # print(f"   Files found: {', '.join(mkv_files)}")
    print()

    for i, filename in enumerate(mkv_files, 1):
        print(f"📹 Processing file {i}/{len(mkv_files)}: {filename}")
        input_path = os.path.join(folder_path, filename)
        fixed_path = os.path.join(output_folder, filename)

        if os.path.exists(fixed_path):
            print(f"   ⏭️  Skipping (already exists): {filename}")
            print()
            continue

        # Check if file needs keyframe fixing
        keyframes = get_keyframe_times(input_path)
        if not keyframes:
            print(
                f"   🎯 No keyframes detected, re-encoding to add keyframes "
                f"every {keyframe_threshold}s"
            )
            try:
                fix_keyframes(input_path, fixed_path, keyframe_threshold)
                print(f"   ✅ Saved: {os.path.basename(fixed_path)}")
            except Exception as e:
                print(f"   ❌ Failed to fix: {e}")
        elif needs_fixing(keyframes, keyframe_threshold):
            print(
                f"   🎯 Keyframes too far apart, re-encoding to add keyframes "
                f"every {keyframe_threshold}s"
            )
            try:
                fix_keyframes(input_path, fixed_path, keyframe_threshold)
                print(f"   ✅ Saved: {os.path.basename(fixed_path)}")
            except Exception as e:
                print(f"   ❌ Failed to fix: {e}")
        else:
            print(f"   👍 OK: {filename} (keyframes are already good)")
        print()


if __name__ == "__main__":
    INPUT_PATH = "/Volumes/ExtremeSSD/DATA/Anime/Naruto/Naruto Complete Series + Movies Uncut"
    OUTPUT_PATH = "/Users/emif/Downloads/naruto1"
    process_folder(INPUT_PATH, OUTPUT_PATH)

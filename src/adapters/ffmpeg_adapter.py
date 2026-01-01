"""FFmpeg adapter for video processing operations"""

import subprocess
from pathlib import Path
from typing import List, Optional
from src.contracts.models.timeline import Timeline, Segment


class FFmpegAdapter:
    """Adapter for FFmpeg operations"""
    
    def __init__(self, ffmpeg_path: Optional[str] = None):
        """Initialize FFmpeg adapter
        
        Args:
            ffmpeg_path: Path to FFmpeg executable (default: system PATH)
        """
        self.ffmpeg_path = ffmpeg_path or "ffmpeg"
    
    def cut_and_concat_video(
        self,
        timeline: Timeline,
        overwrite: bool = True
    ) -> None:
        """Cut and concatenate video segments with narration
        
        Args:
            timeline: Timeline object with segments
            overwrite: Whether to overwrite existing output file
        """
        input_file = timeline.input
        narration_file = timeline.narration
        output_file = timeline.output
        segments = timeline.segments
        
        # Build filter complex for trimming and concatenation
        filters_v = []
        v_labels = []
        
        for i, seg in enumerate(segments):
            start = seg.start
            end = seg.end
            filters_v.append(
                f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]"
            )
            v_labels.append(f"[v{i}]")
        
        filter_complex = ";".join(filters_v) + ";"
        filter_complex += "".join(v_labels)
        filter_complex += f"concat=n={len(v_labels)}:v=1:a=0[outv]"
        
        # Build FFmpeg command
        cmd = [
            self.ffmpeg_path,
            "-y" if overwrite else "-n",
            "-i", str(input_file),
            "-i", str(narration_file),
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-c:a", "aac",
            "-shortest",
            "-movflags", "+faststart",
            str(output_file)
        ]
        
        # Execute FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            raise RuntimeError(
                f"FFmpeg failed with return code {result.returncode}:\n"
                f"stderr: {result.stderr}"
            )
    
    def check_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available
        
        Returns:
            True if FFmpeg is available
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False


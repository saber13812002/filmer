import json
import subprocess

FFMPEG = r"C:\Program Files (x86)\FastPCTools\Fast Screen Recorder\ffmpeg.exe"

def main():
    with open("timeline.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    input_file = config["input"]
    narration_file = config["narration"]
    output_file = config["output"]
    segments = config["segments"]

    filters_v = []
    v_labels = []

    for i, seg in enumerate(segments):
        start = seg["start"]
        end = seg["end"]

        filters_v.append(
            f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]"
        )
        v_labels.append(f"[v{i}]")

    filter_complex = ";".join(filters_v) + ";"
    filter_complex += "".join(v_labels)
    filter_complex += f"concat=n={len(v_labels)}:v=1:a=0[outv]"

    cmd = [
        FFMPEG,
        "-y",
        "-i", input_file,        # input 0: video
        "-i", narration_file,    # input 1: narration mp3
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "aac",
        "-shortest",              # اگر نریشن کوتاه‌تر بود
        "-movflags", "+faststart",
        output_file
    ]

    print("Running FFmpeg...")
    subprocess.run(cmd, check=True)
    print("Done:", output_file)

if __name__ == "__main__":
    main()

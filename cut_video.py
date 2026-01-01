from typing import Any


import json
import subprocess

def main():
    with open("timeline.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    input_file = config["input"]
    output_file = config["output"]
    segments = config["segments"]

    filters_v = []
    filters_a = []
    v_labels = []
    a_labels = []

    for i, seg in enumerate[Any](segments):
        start = seg["start"]
        end = seg["end"]

        filters_v.append(
            f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]"
        )
        filters_a.append(
            f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}]"
        )

        v_labels.append(f"[v{i}]")
        a_labels.append(f"[a{i}]")

    filter_complex = ";".join(filters_v + filters_a) + ";"
    filter_complex += "".join(v_labels) + f"concat=n={len(v_labels)}:v=1:a=0[outv];"
    filter_complex += "".join(a_labels) + f"concat=n={len(a_labels)}:v=0:a=1[outa]"

    cmd = [
        "C:\\Program Files (x86)\\FastPCTools\\Fast Screen Recorder\\ffmpeg.exe",
        "-y",
        "-i", input_file,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "aac",
        "-movflags", "+faststart",
        output_file
    ]

    print("Running FFmpeg...")
    subprocess.run(cmd, check=True)
    print("Done:", output_file)

if __name__ == "__main__":
    main()

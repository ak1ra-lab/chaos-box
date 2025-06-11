# PYTHON_ARGCOMPLETE_OK

import argparse
from pathlib import Path

import argcomplete
import cv2
import numpy
from PIL import Image, ImageDraw, ImageOps

from miscbox.logging import setup_logger

logger = setup_logger(__name__)


def gen_circle_mask(im: Image.Image, upscale=3):
    # ref: https://stackoverflow.com/a/22336005
    size = (im.size[0] * upscale, im.size[1] * upscale)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    mask = mask.resize(im.size, resample=Image.Resampling.LANCZOS)
    logger.debug(f"mask = {mask}")

    return mask


def gen_rotated_frames(im: Image.Image, step=10, trim=False):
    mask = gen_circle_mask(im)
    mask_invert = ImageOps.invert(mask)
    circle = im.copy()
    circle.putalpha(mask)

    frames = []
    for angle in range(0, 360, step):
        frame = circle.copy().rotate(angle=angle)
        if not trim:
            frame.paste(im, mask=mask_invert)
        frames.append(frame)

    return frames


def PIL_frames_to_video(filename, frames, fps):
    # ref: https://blog.extramaster.net/2015/07/python-pil-to-mp4.html
    videodim = frames[0].size
    forcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(filename, forcc, fps, videodim)
    for frame in frames:
        video.write(cv2.cvtColor(numpy.array(frame), cv2.COLOR_RGB2BGR))

    video.release()


def parse_args():
    parser = argparse.ArgumentParser(description="Rotate images and save as GIF or MP4")
    parser.add_argument(
        "-s",
        "--step",
        type=int,
        default=10,
        help="Image.rotate angles step, default: %(default)s",
    )
    parser.add_argument(
        "-f",
        "--fps",
        type=int,
        default=30,
        help="GIF/video frame per seconds, default: %(default)s",
    )
    parser.add_argument(
        "-F",
        "--format",
        choices=("gif", "mp4"),
        default="mp4",
        help="Output filename format",
    )
    parser.add_argument(
        "-t",
        "--trim",
        action="store_true",
        help="Trim surrounding background",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="Reverse direction of rotation, clockwise (cw) if set, counter clockwise (ccw) if not",
    )
    parser.add_argument(
        "images", nargs="+", metavar="image", help="Images to processing (glob allowed)"
    )

    argcomplete.autocomplete(parser)
    return parser.parse_args()


def main():
    args = parse_args()

    for image in args.images:
        image = Path(image).expanduser().resolve()
        logger.info(f"Processing image: {image}")

        with Image.open(image) as im:
            frames = gen_rotated_frames(im, step=args.step, trim=args.trim)
            logger.debug(f"len(frames) = {len(frames)}")

        if args.reverse:
            # clockwise (cw) if set, counter clockwise (ccw) if not
            # keep the first frame as first, and reverse the left
            first = frames.pop(0)
            frames = [first] + frames[::-1]

        duration = round(len(frames) / args.fps, 2)
        # cw: clockwise, ccw: counter clockwise
        direction = "cw" if args.reverse else "ccw"
        filename = (
            image.parent
            / f"{image.stem}-{args.fps}fps-{duration}s-{direction}.{args.format}"
        )
        logger.info(f"Saving frames to: {filename}")
        if args.format == "gif":
            frames[0].save(
                filename,
                save_all=True,
                append_images=frames[1:],
                duration=1000 / args.fps,
                loop=0,
            )
        elif args.format == "mp4":
            PIL_frames_to_video(filename, frames, args.fps)


if __name__ == "__main__":
    main()

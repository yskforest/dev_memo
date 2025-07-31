import cv2
from multiprocessing.pool import ThreadPool
from collections import deque
import argparse
import itertools
from tqdm import tqdm


def process_frame(frame, det):
    # some intensive computation...
    # frame = cv2.medianBlur(frame, 19)
    # frame = cv2.medianBlur(frame, 19)
    frame = cv2.resize(frame, dsize=None, fx=0.5, fy=0.5)
    # frame = det.anote(frame)
    return frame


def video2imgs(in_file, out_folder):
    cap = cv2.VideoCapture(in_file)

    threadn = cv2.getNumberOfCPUs()
    pool = ThreadPool(processes=threadn)
    pending = deque()

    for frame_num in tqdm(itertools.count()):
        while len(pending) > 0 and pending[0].ready():
            res = pending.popleft().get()

            # cv2.imshow('threaded video', res)
            cv2.imwrite(f"{out_folder}/{frame_num:06}.png", res)

        if len(pending) < threadn:
            ret, frame = cap.read()
            if ret:
                det = "dummy"
                task = pool.apply_async(process_frame, (frame.copy(), det))
                pending.append(task)
            else:
                break

        if cv2.waitKey(1) == 27:
            break

    print('Done')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-i', '--in_file',
        default="image/*.png",
        help='input files in glob format (image/*.png)')
    argparser.add_argument(
        '-o', '--out_folder',
        default="out",
        help='save file name (out.mp4)')
    args = argparser.parse_args()

    video2imgs(args.in_file, args.out_folder)

import re
import json
import argparse


def main(args):
    with open(args.in_file, "r") as file:
        log_txt = file.read()

    txt_n = log_txt.split("\n")

    json_data = {}

    map_re = 'Map: ([a-zA-Z0-9]+)'
    frames_re = 'Frames ([0-9]+)'
    duration_re = 'Duration: ([+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?) seconds'
    frame_re = 'Frame (\\d+) at ([+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?) seconds'
    location_re = 'Id: (\\d+) Location: \\(([+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?), ([+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?), ([+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?)\\) Rotation \\(([+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?), ([+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?), ([+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?)\\)'
    create_re = 'Create (\\d+): ([a-zA-Z0-9\\._-]+) \\((\\d+)\\) at \\(([+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?), ([+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?), ([+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?)\\)'
    color_re = ' color = (\\d+),(\\d+),(\\d+)'
    size_re = ' size = ([a-zA-Z0-9]+)'

    frame_dic = {}
    frame_infos = []
    frame_id = 1
    create_actors = []

    for line in txt_n:
        if "Version" in line:
            json_data["Version"] = line.split(" ")[1]
        elif "Map" in line:
            json_data["Map"] = line.split(" ")[1]
        elif "Date" in line:
            json_data["Date"] = line.split(" ")[1]
        elif "Frames" in line:
            json_data["Frames"] = line.split(" ")[1]
        elif "Duration" in line:
            json_data["Duration"] = line.split(" ")[1]
        elif "Frame " in line:
            frame_dic = {}
            # Frame 2 at 0.0333333 seconds
            frame_id = int(line.split(" ")[1])
            frame_dic["FrameId"] = frame_id
            frame_dic["Seconds"] = line.split(" ")[3]
            # frame_dic["Objects"] = []
            frame_dic["ActorId"] = {}
            frame_infos.append(frame_dic)
        elif " Create " in line:
            # if "traffic" or "spectator" in line:
            if "traffic." in line or "spectator" in line:
                continue
            # Create 24: vehicle.audi.tt (1) at (8805.62, 13414.8, 0)
            match = re.findall(create_re, line)
            actor_dic = {}
            actor_dic["ActorId"] = match[0][0]
            actor_dic["ObjectType"] = match[0][1]
            actor_dic["x"] = float(match[0][3]) / 100
            actor_dic["y"] = float(match[0][4]) / 100
            actor_dic["z"] = float(match[0][5]) / 100
            actor_dic["CreateFrame"] = frame_id
            create_actors.append(actor_dic)
        elif " Location: " in line:
            match = re.findall(location_re, line)
            ActorId = match[0][0]
            loc_dic = {}

            # loc_dic["ActorId"] = match[0][0]
            dic = {}
            dic["x"] = match[0][1]
            dic["y"] = match[0][2]
            dic["z"] = match[0][3]
            dic["roll"] = match[0][4]
            dic["pitch"] = match[0][5]
            dic["yaw"] = match[0][6]

            loc_dic[ActorId] = dic
            frame_infos[frame_id - 1]["ActorId"][ActorId] = dic

        elif " Steering: " in line:
            # Id: 24 Steering: -0.000175733 Throttle: 0.85 Brake 0 Handbrake: 0 Gear: 1?
            split = line.split(" ")
            actor_id = split[3]
            frame_infos[frame_id - 1]["ActorId"][actor_id]["Steering"] = split[5]
            frame_infos[frame_id - 1]["ActorId"][actor_id]["Throttle"] = split[7]
            frame_infos[frame_id - 1]["ActorId"][actor_id]["Brake"] = split[9]
            frame_infos[frame_id - 1]["ActorId"][actor_id]["Handbrake"] = split[11]
            frame_infos[frame_id - 1]["ActorId"][actor_id]["Gear"] = split[13]

    json_data["FrameInfos"] = frame_infos
    json_data["CreateActors"] = create_actors
    with open(args.out_file, 'w') as file:
        json.dump(json_data, file)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-i', '--in_file',
        default="test.txt",
        help='output carla log name (abs path) c:/hoge.log')
    argparser.add_argument(
        '-o', '--out_file',
        default="test_carlalog.json",
        help='output carla log name (abs path) c:/hoge.log')
    args = argparser.parse_args()

    main(args)

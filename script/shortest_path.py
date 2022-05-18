import lanelet2
import sys
import argparse


def get_shortest_path(ll2_map, start_lane_id, goal_lane_id):
    start_lane = ll2_map.laneletLayer[start_lane_id]
    goal_lane = ll2_map.laneletLayer[goal_lane_id]
    route = graph.getRoute(start_lane, goal_lane)
    shortest_path = None

    if route is None:
        print("error: no route was calculated")
    else:
        shortest_path = route.shortestPath()
        if shortest_path is None:
            print ("error: no shortest path was calculated")

    return shortest_path.getRemainingLane(start_lane)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Path to the input osm file")
    parser.add_argument("output", help="Path to resulting debug routing graph")
    parser.add_argument("--lat", help="Lateral position of origin", type=float, default=35.527715) # 49
    parser.add_argument("--lon", help="Longitudinal position of origin", type=float, default=139.68909) # 8
    args = parser.parse_args()
    
    rules_map = {"vehicle": lanelet2.traffic_rules.Participants.Vehicle,
                 "bicycle": lanelet2.traffic_rules.Participants.Bicycle,
                 "pedestrian": lanelet2.traffic_rules.Participants.Pedestrian,
                 "train": lanelet2.traffic_rules.Participants.Train}

    world_origin = lanelet2.io.Origin(args.lat, args.lon)
    proj_utm = lanelet2.projection.UtmProjector(world_origin)
    proj_mercator = lanelet2.projection.MercatorProjector(world_origin)
    ll2_map = lanelet2.io.load(args.filename, proj_utm)

    routing_cost = lanelet2.routing.RoutingCostDistance(0.)  # zero cost for lane changes
    traffic_rules = lanelet2.traffic_rules.create(lanelet2.traffic_rules.Locations.Germany,
                                                  rules_map["vehicle"])

    graph = lanelet2.routing.RoutingGraph(ll2_map, traffic_rules, [routing_cost])
    debug_map = graph.getDebugLaneletMap()
    # lanelet2.io.write(args.output, debug_map, ll2_map)

    shortest_lanes = get_shortest_path(ll2_map, 4792, 5208)

    # save the path in another OSM map with a special tag to highlight it
    ids = []
    for lane in shortest_lanes:
        ids.append(lane.id)
        ll2_map.laneletLayer[lane.id].attributes["shortestPath"] = "True"
    print(ids)

    lanelet2.io.write(args.output, ll2_map, proj_utm)

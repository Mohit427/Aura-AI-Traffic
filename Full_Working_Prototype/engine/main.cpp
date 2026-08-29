#include <iostream>
#include <vector>
#include <queue>
#include <limits>
#include <string>
#include <unordered_map>
#include <algorithm>
#include <cstdlib>

using std::min;
using std::numeric_limits;
using std::queue;
using std::string;
using std::unordered_map;
using std::vector;

// Edmonds-Karp: BFS-based Ford-Fulkerson on a residual capacity matrix.
bool bfs(const vector<vector<int>> &residual, int s, int t, vector<int> &parent)
{
    const int n = static_cast<int>(residual.size());
    vector<bool> visited(n, false);
    queue<int> q;

    q.push(s);
    visited[s] = true;
    parent[s] = -1;

    while (!q.empty())
    {
        int u = q.front();
        q.pop();

        for (int v = 0; v < n; ++v)
        {
            if (!visited[v] && residual[u][v] > 0)
            {
                parent[v] = u;
                visited[v] = true;
                q.push(v);
                if (v == t)
                {
                    return true;
                }
            }
        }
    }

    return visited[t];
}

int edmondsKarp(vector<vector<int>> &residual, int s, int t)
{
    const int n = static_cast<int>(residual.size());
    vector<int> parent(n);
    int maxFlow = 0;

    while (bfs(residual, s, t, parent))
    {
        int pathFlow = numeric_limits<int>::max();

        for (int v = t; v != s; v = parent[v])
        {
            int u = parent[v];
            pathFlow = min(pathFlow, residual[u][v]);
        }

        for (int v = t; v != s; v = parent[v])
        {
            int u = parent[v];
            residual[u][v] -= pathFlow;
            residual[v][u] += pathFlow;
        }

        maxFlow += pathFlow;
    }

    return maxFlow;
}

// Helper to obtain an integer index for a node ID string within a category map.
int getNodeIndex(unordered_map<string, int> &index, const string &id, int &nextIndex)
{
    auto it = index.find(id);
    if (it != index.end())
    {
        return it->second;
    }
    int idx = nextIndex++;
    index[id] = idx;
    return idx;
}

int main(int argc, char *argv[])
{
    int north_cars = 27;
    int south_cars = 28;
    int east_cars = 50;
    int west_cars = 41;
    int vui_score = 0;
    int ev_north_tti = 0;
    int ev_east_tti = 0;

    if (argc >= 8)
    {
        north_cars = std::atoi(argv[1]);
        south_cars = std::atoi(argv[2]);
        east_cars = std::atoi(argv[3]);
        west_cars = std::atoi(argv[4]);
        vui_score = std::atoi(argv[5]);
        ev_north_tti = std::atoi(argv[6]);
        ev_east_tti = std::atoi(argv[7]);
    }
    // Node identifiers (exact OSM IDs as requested).
    const string NORTH = "1313198082.274";
    const string SOUTH = "1313198080.250";
    const string EAST = "1110246916";
    const string WEST = "588357066";

    const string NORTH_OUT = "1313198080";
    const string SOUTH_OUT = "1313198082";
    const string EAST_OUT = "1049511450#0";
    const string WEST_OUT = "27346902#0";

    const string CROSSWALK_E0 = "E0";
    const string CROSSWALK_E1 = "E1";
    const string CROSSWALK_315262038 = "315262038_c0";
    const string CROSSWALK_300216374 = "300216374_c0";

    // Inflow and outflow nodes are modeled as separate logical nodes even when
    // their OSM ID strings overlap (e.g., North inflow and South_Out share the
    // same OSM ID but represent opposite sides of the junction).
    unordered_map<string, int> inflowIndex;
    unordered_map<string, int> outflowIndex;
    unordered_map<string, int> crosswalkIndex;
    int nextIndex = 0;

    auto inIdx = [&](const string &id) -> int
    {
        return getNodeIndex(inflowIndex, id, nextIndex);
    };
    auto outIdx = [&](const string &id) -> int
    {
        return getNodeIndex(outflowIndex, id, nextIndex);
    };
    auto cwIdx = [&](const string &id) -> int
    {
        return getNodeIndex(crosswalkIndex, id, nextIndex);
    };

    // Register all inflow nodes.
    inIdx(NORTH);
    inIdx(SOUTH);
    inIdx(EAST);
    inIdx(WEST);

    // Register all outflow nodes.
    outIdx(NORTH_OUT);
    outIdx(SOUTH_OUT);
    outIdx(EAST_OUT);
    outIdx(WEST_OUT);

    // Register crosswalk nodes.
    cwIdx(CROSSWALK_E0);
    cwIdx(CROSSWALK_E1);
    cwIdx(CROSSWALK_315262038);
    cwIdx(CROSSWALK_300216374);

    const int nodeCount = nextIndex;

    // Base directed edges with mock manual capacities (cars per phase).
    // Format: (u, v, capacity)
    vector<std::tuple<int, int, int>> baseEdges;

    // North -> South_Out, West_Out
    int north_straight = north_cars * 15 / 27;
    baseEdges.emplace_back(inIdx(NORTH), outIdx(SOUTH_OUT), north_straight);
    baseEdges.emplace_back(inIdx(NORTH), outIdx(WEST_OUT), north_cars - north_straight);

    // South -> North_Out, East_Out
    int south_straight = south_cars * 18 / 28;
    baseEdges.emplace_back(inIdx(SOUTH), outIdx(NORTH_OUT), south_straight);
    baseEdges.emplace_back(inIdx(SOUTH), outIdx(EAST_OUT), south_cars - south_straight);

    // East -> West_Out, South_Out, North_Out
    int east_first = east_cars * 14 / 50;
    int east_second = east_cars * 16 / 50;
    baseEdges.emplace_back(inIdx(EAST), outIdx(WEST_OUT), east_first);
    baseEdges.emplace_back(inIdx(EAST), outIdx(SOUTH_OUT), east_second);
    baseEdges.emplace_back(inIdx(EAST), outIdx(NORTH_OUT), east_cars - east_first - east_second);

    // West -> East_Out, North_Out, South_Out
    int west_first = west_cars * 13 / 41;
    int west_second = west_cars * 17 / 41;
    baseEdges.emplace_back(inIdx(WEST), outIdx(EAST_OUT), west_first);
    baseEdges.emplace_back(inIdx(WEST), outIdx(NORTH_OUT), west_second);
    baseEdges.emplace_back(inIdx(WEST), outIdx(SOUTH_OUT), west_cars - west_first - west_second);

    // Crosswalk passthrough edges (large capacity, present for completeness).
    baseEdges.emplace_back(cwIdx(CROSSWALK_E0), cwIdx(CROSSWALK_E1), 1000);
    baseEdges.emplace_back(cwIdx(CROSSWALK_315262038), cwIdx(CROSSWALK_300216374), 1000);

    // A large capacity used for super-source / super-sink connections.
    const int INF = 10000;

    // Phase 1: East/West combined.
    // Sources: East, West inflows.
    // Sinks: all reachable outflow nodes (West_Out, South_Out, North_Out, East_Out).
    int phase1Flow = 0;
    {
        vector<vector<int>> residual(nodeCount + 2, vector<int>(nodeCount + 2, 0));
        int superSource = nodeCount;
        int superSink = nodeCount + 1;

        for (const auto &e : baseEdges)
        {
            int u, v, c;
            std::tie(u, v, c) = e;
            residual[u][v] += c;
        }

        residual[superSource][inIdx(EAST)] = INF;
        residual[superSource][inIdx(WEST)] = INF;

        residual[outIdx(WEST_OUT)][superSink] = INF;
        residual[outIdx(SOUTH_OUT)][superSink] = INF;
        residual[outIdx(NORTH_OUT)][superSink] = INF;
        residual[outIdx(EAST_OUT)][superSink] = INF;

        phase1Flow = edmondsKarp(residual, superSource, superSink);
        // std::cout << "Phase 1 (East/West) max-flow: " << phase1Flow << " cars" << std::endl;
    }

    // Phase 2: North/South combined.
    // Sources: North, South inflows.
    // Sinks: all reachable outflow nodes (South_Out, West_Out, North_Out, East_Out).
    int phase2Flow = 0;
    {
        vector<vector<int>> residual(nodeCount + 2, vector<int>(nodeCount + 2, 0));
        int superSource = nodeCount;
        int superSink = nodeCount + 1;

        for (const auto &e : baseEdges)
        {
            int u, v, c;
            std::tie(u, v, c) = e;
            residual[u][v] += c;
        }

        residual[superSource][inIdx(NORTH)] = INF;
        residual[superSource][inIdx(SOUTH)] = INF;

        residual[outIdx(SOUTH_OUT)][superSink] = INF;
        residual[outIdx(WEST_OUT)][superSink] = INF;
        residual[outIdx(NORTH_OUT)][superSink] = INF;
        residual[outIdx(EAST_OUT)][superSink] = INF;

        phase2Flow = edmondsKarp(residual, superSource, superSink);
        // std::cout << "Phase 2 (North/South) max-flow: " << phase2Flow << " cars" << std::endl;
    }

    bool ev_active = (ev_north_tti > 0 || ev_east_tti > 0);
    string ev1_axis;
    string ev2_axis;
    int ev1_tti = 0;
    if (ev_active)
    {
        if (ev_north_tti <= ev_east_tti)
        {
            ev1_axis = "north_south";
            ev2_axis = "east_west";
            ev1_tti = ev_north_tti;
        }
        else
        {
            ev1_axis = "east_west";
            ev2_axis = "north_south";
            ev1_tti = ev_east_tti;
        }
    }

    const int CYCLE_LENGTH = 90;
    const int LOST_TIME = 6;
    int pedGreen = std::min(60, 15 + (vui_score * 2));
    const int EFFECTIVE_GREEN = CYCLE_LENGTH - LOST_TIME - pedGreen;

    double totalFlow = static_cast<double>(phase1Flow) + static_cast<double>(phase2Flow);
    double phase1Green = EFFECTIVE_GREEN * (static_cast<double>(phase1Flow) / totalFlow);
    double phase2Green = EFFECTIVE_GREEN * (static_cast<double>(phase2Flow) / totalFlow);

    std::cout << "{\n"
              << "  \"timestamp\": \"2026-08-28T10:15:30Z\",\n"
              << "  \"intersection_id\": \"vadapalani_junction\",\n";

    if (ev_active)
    {
        std::cout << "  \"ev_schedule\": {\n"
                  << "    \"ev_1_axis\": \"" << ev1_axis << "\",\n"
                  << "    \"ev_1_green_flush_duration\": " << ev1_tti << ",\n"
                  << "    \"all_red_clearance\": 3,\n"
                  << "    \"ev_2_axis\": \"" << ev2_axis << "\"\n"
                  << "  },\n"
                  << "  \"priority_mode\": \"ev_preemption\",\n";
    }
    else
    {
        std::cout << "  \"phase_durations\": {\n"
                  << "    \"north_south_green\": " << static_cast<int>(phase2Green) << ",\n"
                  << "    \"east_west_green\": " << static_cast<int>(phase1Green) << ",\n"
                  << "    \"pedestrian_crossing_green\": " << pedGreen << "\n"
                  << "  },\n"
                  << "  \"priority_mode\": \"" << (vui_score > 0 ? "vui_active" : "normal") << "\",\n";
    }

    std::cout << "  \"vui_score\": " << vui_score << "\n"
              << "}\n";

    return 0;
}

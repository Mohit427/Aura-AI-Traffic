#include <iostream>
#include <string>

// STUB ENGINE — proportional allocation, NOT the real Edmonds-Karp max-flow.
// Yashvant's real C++ engine replaces this binary later with the same
// input/output contract, so nothing else needs to change when it lands.

int main(int argc, char* argv[]) {
    if (argc != 6) {
        std::cerr << "Usage: engine_stub <north> <south> <east> <west> <pedestrian>" << std::endl;
        return 1;
    }

    int north = std::stoi(argv[1]);
    int south = std::stoi(argv[2]);
    int east = std::stoi(argv[3]);
    int west = std::stoi(argv[4]);
    int pedestrian = std::stoi(argv[5]);

    int combined_ns = north + south;
    int combined_ew = east + west;
    int total = combined_ns + combined_ew + pedestrian;

    const int CYCLE_BUDGET = 75;
    int ns_green = 5;
    int ew_green = 5;
    int ped_green = 5;

    if (total > 0) {
        ns_green = (CYCLE_BUDGET * combined_ns) / total;
        ew_green = (CYCLE_BUDGET * combined_ew) / total;
        ped_green = CYCLE_BUDGET - ns_green - ew_green;
    }

    std::string priority_mode = (pedestrian >= 10) ? "vulnerable_user" : "normal";
    int vui_score = pedestrian * 7;
    if (vui_score > 100) vui_score = 100;

    std::cout << "{"
              << "\"phase_durations\":{"
              << "\"north_south_green\":" << ns_green << ","
              << "\"east_west_green\":" << ew_green << ","
              << "\"pedestrian_crossing_green\":" << ped_green
              << "},"
              << "\"priority_mode\":\"" << priority_mode << "\","
              << "\"vui_score\":" << vui_score
              << "}" << std::endl;

    return 0;
}

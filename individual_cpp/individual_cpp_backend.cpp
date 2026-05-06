#include <cmath>
#include <cstddef>

extern "C" {

// posmods layout per slot: [left, right, above, under, touching, notTouching]
void compute_slot_boosts(const double* posmods, double* out_boosts) {
    double boost[7][4] = {{0.0}};

    for (int i = 2; i < 5; ++i) {
        for (int j = 1; j < 3; ++j) {
            int idx = (i - 2) * 2 + (j - 1);
            const double* pm = posmods + idx * 6;
            double left = pm[0];
            double right = pm[1];
            double above = pm[2];
            double under = pm[3];
            double touching = pm[4];
            double notTouching = pm[5];

            boost[i][j - 1] += left;
            boost[i][j + 1] += right;
            boost[i - 1][j] += above;
            boost[i - 2][j] += above;

            boost[i + 1][j] += under;
            boost[i + 2][j] += under;

            if (touching != 0.0) {
                boost[i][j - 1] += touching;
                boost[i][j + 1] += touching;
                boost[i + 1][j] += touching;
                boost[i - 1][j] += touching;
            }
            if (notTouching != 0.0) {
                for (int ki = 2; ki < 5; ++ki) {
                    for (int kj = 1; kj < 3; ++kj) {
                        bool excluded =
                            (ki == i - 1 && kj == j) ||
                            (ki == i + 1 && kj == j) ||
                            (ki == i && kj == j) ||
                            (ki == i && kj == j - 1) ||
                            (ki == i && kj == j + 1);
                        if (!excluded) {
                            boost[ki][kj] += notTouching;
                        }
                    }
                }
            }
        }
    }

    out_boosts[0] = boost[2][1];
    out_boosts[1] = boost[2][2];
    out_boosts[2] = boost[3][1];
    out_boosts[3] = boost[3][2];
    out_boosts[4] = boost[4][1];
    out_boosts[5] = boost[4][2];
}

double calculate_duration_cpp(double base_dura, const double* dura_values, int n) {
    double rep = base_dura;
    for (int i = 0; i < n; ++i) {
        rep += dura_values[i];
    }
    return rep;
}

double fitness_cpp(
    const double* stat_values,
    const double* slot_boosts,
    const double* req_values,
    double duration,
    double duration_min,
    const double* req_stats,
    int is_equipment,
    int apply_stat_boosts
) {
    double stat_sum = 0.0;

    for (int i = 0; i < 6; ++i) {
        double value = stat_values[i];
        if (apply_stat_boosts) {
            value = std::floor(value * (1.0 + slot_boosts[i] / 100.0));
        }
        stat_sum += value;
    }

    double rep = 0.0;
    if (duration <= 0.0) {
        rep = 0.0;
    } else if (duration < duration_min) {
        rep = stat_sum * (duration / duration_min);
    } else {
        rep = stat_sum;
    }

    if (is_equipment) {
        double req_list[5] = {0.0, 0.0, 0.0, 0.0, 0.0};
        for (int ing = 0; ing < 6; ++ing) {
            double mult = 1.0 + slot_boosts[ing] / 100.0;
            const double* req = req_values + ing * 5;
            for (int s = 0; s < 5; ++s) {
                req_list[s] += req[s] * mult;
            }
        }
        for (int s = 0; s < 5; ++s) {
            if (req_list[s] > req_stats[s]) {
                return 0.0;
            }
        }
    }

    return rep;
}

} // extern "C"

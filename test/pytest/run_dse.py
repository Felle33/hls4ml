import os
import subprocess
import sys
import itertools

MEM_LIMIT_KB = 16 * 1024 * 1024  # 16 GB

if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
    print("Usage: python3 run_dse.py <trip_count1> [trip_count2] ...")
    print("       The script should be run in the directory containing myproject_test.cpp")
    print("Output: Launch bambu in a screen session with the following command after having created and accessed the new directry for the synthesis\n")
    print("        bambu \"bambu ../firmware/myproject.cpp --top-fname=myproject -lm --compiler=I386_CLANG16\n" 
          "        --generate-interface=INFER --generate-tb=../myproject_test.cpp --simulate -DRTL_SIM --evaluation\n"
          "        --device-name=xc7a100t-1csg324 --clock-period=5 -v4 [UNROLL_FACTORS_DEFINES]+\n")
    sys.exit(1)

trip_counts = [int(tc) for tc in sys.argv[1:]]

def unroll_factors(trip_count):
    uf = 1
    factors = []
    while uf <= trip_count:
        if trip_count % uf == 0:
            factors.append(uf)
        uf *= 2
    if trip_count not in factors:
        factors.append(trip_count)
    return factors

def generate_combinations(all_factors):
    """
    If a loop is unrolled (> 1), all inner loops must be at their maximum.
    """
    max_factors = [factors[-1] for factors in all_factors]
    n = len(all_factors)
    combos = []

    for i in range(n - 1, -1, -1):
        for uf in all_factors[i]:
            combo = []
            for j in range(n):
                if j < i:
                    # outer loops stay at 1
                    combo.append(1)
                elif j == i:
                    # current loop sweeps
                    combo.append(uf)
                else:
                    # inner loops are at maximum
                    combo.append(max_factors[j])
            combos.append(tuple(combo))

    return combos

all_factors = [unroll_factors(tc) for tc in trip_counts]
combinations = generate_combinations(all_factors)

print(f"[*] Total combinations: {len(combinations)}")

if len(combinations) > 16:
    print("[*] Error: Too many combinations to run in parallel. Please reduce the number of trip counts or their factors.", file=sys.stderr)
    sys.exit(1)

for combo in combinations:
    # e.g. combo = (4, 8, 2) for 3 loops
    dir_suffix = "_".join(f"uf{i}_{v}" for i, v in enumerate(combo))
    out_dir = f"out_{dir_suffix}"
    os.makedirs(out_dir, exist_ok=True)

    defines = " ".join(f"-DUNROLL_FACTOR_{i}={v}" for i, v in enumerate(combo))

    bambu_cmd = (
        f"bambu ../firmware/myproject.cpp "
        f"--top-fname=myproject "
        f"-lm "
        f"--compiler=I386_CLANG16 "
        f"--generate-interface=INFER "
        f"--generate-tb=../myproject_test.cpp "
        f"--simulate "
        f"-DRTL_SIM "
        f"--evaluation "
        f"--device-name=xc7a100t-1csg324 "
        f"--clock-period=5 "
        f"-v4 "
        f"{defines}"
    )

    screen_name = f"dse_{dir_suffix}"
    full_cmd = f"ulimit -v {MEM_LIMIT_KB} && cd {out_dir} && ({bambu_cmd} |& tee log.log)"
    # print(f"[CMD] screen -dmS {screen_name} bash -c '{full_cmd}'")

    subprocess.run([
        "screen", "-dmS", screen_name,
        "bash", "-c", full_cmd
    ])

    print(f"[+] Launched '{screen_name}' → {out_dir}/")
    print(f"    Defines: {defines}\n")
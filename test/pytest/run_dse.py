import os
import subprocess
import sys

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

    return sorted(list(set(combos)))

def launch_screen_session(screen_name, out_dir, defines, cmd):
    subprocess.run([
        "screen", "-dmS", screen_name,
        "bash", "-c", cmd
    ])

    print(f"[+] Launched '{screen_name}' → {out_dir}/")
    print(f"    Defines: {defines}\n")

def create_output_dir(dir_suffix):
    out_dir = f"out_{dir_suffix}"
    os.makedirs(out_dir, exist_ok=True)
    return out_dir

all_factors = [unroll_factors(tc) for tc in trip_counts]
combinations = generate_combinations(all_factors)

print(f"[*] Total combinations: {len(combinations)}")

# The plus 1 is for the baseline run without array partitioning
if len(combinations) + 1 > 16:
    print("[*] Error: Too many combinations to run in parallel. Please reduce the number of trip counts or their factors.", file=sys.stderr)
    sys.exit(1)

for idx_combo, combo in enumerate(combinations):
    # e.g. combo = (4, 8, 2) for 3 loops
    ufs_dir_suffix = "_".join(f"uf{i}_{v}" for i, v in enumerate(combo))
    out_dir = create_output_dir(ufs_dir_suffix)

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
        f"--device-name=xcu55c-2Lfsvh2892 "
        f"--clock-period=5 "
        f"-v4 "
        f"{defines}"
    )

    screen_name = f"dse_{ufs_dir_suffix}"
    full_cmd = f"ulimit -v {MEM_LIMIT_KB} && cd {out_dir} && ({bambu_cmd} |& tee log.log)"
    # print(f"[CMD] screen -dmS {screen_name} bash -c '{full_cmd}'")

    launch_screen_session(screen_name, out_dir, defines, full_cmd)

    if idx_combo == 0:
        out_dir = create_output_dir(ufs_dir_suffix + "_wo_arr_part")
        screen_name_wo_arr_part = f"dse_{ufs_dir_suffix}_wo_arr_part"
        full_cmd_wo_arr_part = f"ulimit -v {MEM_LIMIT_KB} && cd {out_dir} && ({bambu_cmd} --bambu-parameter=panda-lock-csroa=1 |& tee log.log)"
        launch_screen_session(screen_name_wo_arr_part, out_dir, defines, full_cmd_wo_arr_part)
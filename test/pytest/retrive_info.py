import xml.etree.ElementTree as ET
import argparse
import os


def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # --- Extract cycles ---
    run_elem = root.find(".//timing/evaluation/run")
    cycles = int(run_elem.text) if run_elem is not None else None

    # --- Extract resources ---
    resources_elem = root.find(".//resources")
    resources = {}

    if resources_elem is not None:
        for key, value in resources_elem.attrib.items():
            try:
                if "." in value:
                    resources[key] = float(value)
                else:
                    resources[key] = int(value)
            except ValueError:
                resources[key] = value

    return cycles, resources

def print_cycles_and_resources(cycles, resources):
    print("\tCycles:", cycles)
    for k, v in resources.items():
        print(f"\t{k}: {v}")
    print()

def print_synthesis(dir_path):
    abs_dir_path = os.path.abspath(dir_path)
    if not os.path.isdir(abs_dir_path):
        print(f"[!] Error: {dir_path} is not a valid directory.")
        return
    
    for name in os.listdir(abs_dir_path):
        if os.path.isdir(os.path.join(abs_dir_path, name)) and name.startswith("out_"):
            xml_path = os.path.join(abs_dir_path, name, "bambu_results.xml")
            if os.path.isfile(xml_path):
                cycles, resources = parse_xml(xml_path)
                print(f"[+] Synthesis results for {name}:")
                print_cycles_and_resources(cycles, resources)
            else:
                print(f"[*] Warning: bambu_results.xml not found in {name}")

def main():
    parser = argparse.ArgumentParser(description="Extract cycles and resources from directory with synthesis results")
    parser.add_argument("dir_path", help="Path to the directory containing synthesis results")

    args = parser.parse_args()

    print_synthesis(args.dir_path)


if __name__ == "__main__":
    main()
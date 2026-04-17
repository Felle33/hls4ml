import xml.etree.ElementTree as ET
import argparse


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


def main():
    parser = argparse.ArgumentParser(description="Extract cycles and resources from XML")
    parser.add_argument("xml_file", help="Path to the XML file")

    args = parser.parse_args()

    cycles, resources = parse_xml(args.xml_file)

    print("Cycles:", cycles)
    print("Resources:")
    for k, v in resources.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
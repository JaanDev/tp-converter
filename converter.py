import re
import plistlib
import argparse
import os, sys
import cv2

parser = argparse.ArgumentParser(description='Geometry Dash Texture Packs Converter')
required = parser.add_argument_group('Arguments')
required.add_argument('-i', '--input', help='Input file name', required=True)
required.add_argument('-a', '--all', action='store_true', help='Specify to convert to hd and low without running twice', required=False)

args = parser.parse_args()
input_path = args.__dict__["input"]
do_all = args.__dict__["all"]

if not input_path.endswith(".plist") and not input_path.endswith(".fnt"):
    print("The input filename should be a path to .plist or .fnt!")
    sys.exit(1)

if not os.path.exists(input_path):
    print("The specified file does not exist!")
    sys.exit(1)


def replace_last(input: str, text: str, sep: str) -> str:
    return input[::-1].replace(text[::-1], sep[::-1])[::-1]
    
def divide(key: str) -> str:
    return re.sub(r"\{([0-9\-]+)\,([0-9\-]+)\}", "{{{0},{1}}}".format(*[round(int(x) / 2) for x in re.search(r"\{([0-9\-]+)\,([0-9\-]+)\}", key).groups()]), key)
    
def divide_float(key: str) -> str:
    return re.sub(r"\{([0-9\-\.]+)\,([0-9\-\.]+)\}", "{{{0},{1}}}".format(*[float(x) / 2.0 for x in re.search(r"\{([0-9\-\.]+)\,([0-9\-\.]+)\}", key).groups()]), key)

def divide2(key: str) -> str:
    return re.sub(r"\{\{([0-9\-]+)\,([0-9\-]+)\}\,\{([0-9\-]+)\,([0-9\-]+)\}\}", "{{{{{0},{1}}},{{{2},{3}}}}}".format(*[round(int(x) / 2) for x in re.search(r"\{\{([0-9\-]+)\,([0-9\-]+)\}\,\{([0-9\-]+)\,([0-9\-]+)\}\}", key).groups()]), key)

def convert_fnt(input_name: str, out_name: str, in_quality: str, out_quality: str) -> None:
    print(f'\n"{input_name}.fnt" -> "{out_name}.fnt"')
    print(f'"{input_name}.png" -> "{out_name}.png"')
    
    with open(input_name + ".fnt", 'r') as f:
        input_fnt = f.read().split("\n")
        
    for i in range(len(input_fnt)):
        l = input_fnt[i]
        
        if l.strip() == "":
            continue
        
        if l.startswith("common"):
            input_fnt[i] = re.sub(r"common lineHeight=([0-9\-]+)\s+?base=([0-9\-]+)\s+?scaleW=([0-9\-]+)\s+?scaleH=([0-9\-]+)",
                                  "common lineHeight={} base={} scaleW={} scaleH={}".format(*[round(int(x) / 2) for x in re.search(r"common lineHeight=([0-9\-]+)\s+?base=([0-9\-]+)\s+?scaleW=([0-9\-]+)\s+?scaleH=([0-9\-]+)", l).groups()]),
                                  l)

        elif l.startswith("page id="):
            input_fnt[i] = re.sub(r"file=\"(.+)\"",
                                  f"file=\"{os.path.basename(out_name)}.png\"",
                                  l)
                                  
        elif l.startswith("char id="):
            input_fnt[i] = re.sub(r"x=(\d+?)\s+?y=(\d+?)\s+?width=(\d+?)\s+?height=(\d+?)\s+?xoffset=([0-9\-]+?)\s+?yoffset=([0-9\-]+?)\s+?xadvance=([0-9\-]+?)\s+?",
                                  "x={}\ty={}\twidth={}\theight={}\txoffset={}\tyoffset={}\txadvance={}\t".format(*[round(int(x) / 2) for x in re.search(r"x=(\d+?)\s+?y=(\d+?)\s+?width=(\d+?)\s+?height=(\d+?)\s+?xoffset=([0-9\-]+?)\s+?yoffset=([0-9\-]+?)\s+?xadvance=([0-9\-]+?)\s+?", l).groups()]),
                                  l)
                                  
        elif l.startswith("kerning first="):
            input_fnt[i] = re.sub(r"amount=([0-9\-]+)",
                                  "amount={}".format(*[round(int(x) / 2) for x in re.search(r"amount=([0-9\-]+)", l).groups()]),
                                  l)
                                  
    with open(out_name + ".fnt", 'w') as f:
        f.write("\n".join(input_fnt))
        
    print("Downscaling the image")
    img = cv2.imread(input_name + ".png", cv2.IMREAD_UNCHANGED)

    resized = cv2.resize(img, (round(img.shape[1] / 2), round(img.shape[0] / 2)), interpolation=cv2.INTER_AREA)

    cv2.imwrite(out_name + ".png", resized)
    print("Done!")
    
def convert(input_name: str, out_name: str, in_quality: str, out_quality: str) -> None:
    print(f'\n"{input_name}.plist" -> "{out_name}.plist"')
    print(f'"{input_name}.png" -> "{out_name}.png"')
    
    with open(input_name + ".plist", 'rb') as f:
        input_plist = plistlib.load(f)

    print("Downscaling the .plist")
    # print(f"0/{len(input_plist['frames'])}", end="\r")
    
    for name in input_plist["frames"]:
        if input_plist["frames"][name]["spriteOffset"]:
            input_plist["frames"][name]["spriteOffset"] = divide_float(input_plist["frames"][name]["spriteOffset"])
        if input_plist["frames"][name]["spriteSize"]:
            input_plist["frames"][name]["spriteSize"] = divide(input_plist["frames"][name]["spriteSize"])
        if input_plist["frames"][name]["spriteSourceSize"]:
            input_plist["frames"][name]["spriteSourceSize"] = divide(input_plist["frames"][name]["spriteSourceSize"])
        if input_plist["frames"][name]["textureRect"]:
            input_plist["frames"][name]["textureRect"] = divide2(input_plist["frames"][name]["textureRect"])
    
    # print(f"{list(input_plist['frames'].keys()).index(name)+1}/{len(input_plist['frames'])}", end="\r") # co
    
    input_plist["metadata"]["realTextureFileName"] = replace_last(input_plist["metadata"]["realTextureFileName"], in_quality, out_quality)
    input_plist["metadata"]["size"] = divide(input_plist["metadata"]["size"])
    input_plist["metadata"]["textureFileName"] = replace_last(input_plist["metadata"]["textureFileName"], in_quality, out_quality)
    
    with open(out_name + ".plist", 'wb') as f:
        plistlib.dump(input_plist, f)
    
    print("Downscaling the image")
    img = cv2.imread(input_name + ".png", cv2.IMREAD_UNCHANGED)

    resized = cv2.resize(img, (round(img.shape[1] / 2), round(img.shape[0] / 2)), interpolation=cv2.INTER_AREA)

    cv2.imwrite(out_name + ".png", resized)
    print("Done!")

def main():
    input_filename, input_ext = os.path.splitext(input_path)
    input_filename_only = os.path.basename(input_filename)
    
    input_quality = "uhd" if input_filename_only.endswith("-uhd") else "hd" if input_filename_only.endswith("-hd") else "low"
    out_quality = "hd" if input_quality == "uhd" else "low"
    input_file_quality = f"-{input_quality}"
    out_file_quality = f"-{out_quality}" if out_quality != "low" else ""
    
    if input_quality == "low":
        print("You cant specify files in the lowest quality as it is the lowest(lol)")
        sys.exit(1)
    
    out_filename = replace_last(input_filename, input_file_quality, out_file_quality)
    
    print(f"Converting {input_filename_only} from {input_quality} to {out_quality}...")
    
    if input_ext == ".fnt":
        convert_fnt(input_filename, out_filename, input_file_quality, out_file_quality)
    else:
        convert(input_filename, out_filename, input_file_quality, out_file_quality)
    
    if do_all:
        if out_quality == "hd":
            input_filename = replace_last(out_filename, input_file_quality, out_file_quality)
            input_filename_only = os.path.basename(input_filename)
            
            input_quality = "hd"
            out_quality = "low"
            input_file_quality = "-hd"
            out_file_quality = ""
            
            out_filename = replace_last(input_filename, input_file_quality, out_file_quality)
            
            print(f"\nConverting {input_filename_only} from {input_quality} to {out_quality}...")
            
            if input_ext == ".fnt":
                convert_fnt(input_filename, out_filename, input_file_quality, out_file_quality)
            else:
                convert(input_filename, out_filename, input_file_quality, out_file_quality)
    
if __name__ == "__main__":
    main()
import pandas as pd
import tqdm
import argparse
import json


def get_linecount(file_name: str) -> int:
    """use `wc` command to get line count of large file quickly"""
    import subprocess

    out = subprocess.getoutput("wc -l %s" % file_name)
    return int(out.split()[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert json results of ASGrab into convenient csv"
    )
    parser.add_argument("--inputFile", "-i", help="file need to handle", type=str)
    parser.add_argument("--inputType", "-t", help="lzr or zgrab", type=str)
    args = parser.parse_args()
    input_type = args.inputType
    input_file = args.inputFile
    output_file = input_file + ".csv"

    display_bar = tqdm.tqdm(total=get_linecount(input_file))
    display_bar.write(f"Start to handle {input_file} in {input_type} mode:")

    res_df = None

    if input_type == "lzr":
        res_df = pd.DataFrame(
            columns=[
                "IP",
                "Port",
                "Window",
                "TTL",
                "Counter",
                "ACK",
                "ACKed",
                "SYN",
                "RST",
                "FIN",
                "PUSH",
                "HandshakeNum",
                "Fingerprint",
            ]
        )
        with open(args.inputFile, "r") as fi:
            for line in fi:
                try:
                    data: dict = json.loads(line)
                except:
                    display_bar.update(1)
                    continue
                res_df.loc[len(res_df)] = {
                    "IP": data["saddr"],
                    "Port": data["sport"],
                    "Window": data["window"],
                    "TTL": data["ttl"],
                    "Counter": data["Counter"],
                    "ACK": data["ACK"],
                    "ACKed": data["ACKed"],
                    "SYN": data["SYN"],
                    "RST": data["RST"],
                    "FIN": data["FIN"],
                    "PUSH": data["PUSH"],
                    "HandshakeNum": data["HandshakeNum"],
                    "Fingerprint": data["fingerprint"],
                }
                display_bar.update(1)
    elif input_type == "zgrab":
        res_df = pd.DataFrame(
            columns=["IP", "Port", "Protocol", "Status", "Status code", "Body"]
        )
        with open(args.inputFile, "r") as fi:
            for line in fi:
                try:
                    data: dict = json.loads(line)
                except:
                    continue
                # invalid protocol
                if data.get("data") == None:
                    display_bar.update(1)
                    continue
                res_dic = {"IP": data["ip"], "Port": data["port"]}
                if data["data"].get("http") == None:
                    res_dic["Protocol"] = "https"
                else:
                    res_dic["Protocol"] = "http"
                res_dic["Status"] = data["data"][res_dic["Protocol"]]["status"]
                if data["data"][res_dic["Protocol"]]["result"].get("response") != None:
                    res_dic["Status code"] = data["data"][res_dic["Protocol"]][
                        "result"
                    ]["response"]["status_code"]
                res_df.loc[len(res_df)] = res_dic
                display_bar.update(1)
    else:
        display_bar.write("Invalid inputType: just accept 'lzr' or 'zgrab'")
        import sys

        sys.exit()

    display_bar.write("Converted into CSV, saving now...")
    res_df.to_csv(output_file, sep=",", index=True, header=True)
    display_bar.write("Saved!")

from configparser import ConfigParser
from datetime import datetime
import argparse
import subprocess
import logging
import sys


def config_log(log_filename: str):
    """configure logging module for logging on both file and console"""
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s - %(message)s", datefmt="%Y%m%d-%H:%M:%S"
    )

    file_handler = logging.FileHandler(log_filename, mode="a", encoding="utf8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)  # log more verbose info to file

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=min(file_handler.level, console_handler.level),
        handlers=[file_handler, console_handler],
    )


def exec_cmd(cmd: str):
    """execute shell command interactively in real-time"""
    subprocess.run(cmd, shell=True, stdin=0, stdout=1, stderr=2)


# def set_multi_ini(port: str):
#     """get zgrab multiple.ini ready for specific port"""
#     with open("utils/multi.ini", "w") as f:
#         f.write(
#             f"""[Application Options]
# [http]
# name="http"
# trigger="http"
# port={port}
# user-agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 Edg/114.0.1823.43"
# endpoint="/"
# max-redirects=1
# [http]
# name="https"
# trigger="tls"
# port={port}
# user-agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 Edg/114.0.1823.43"
# endpoint="/"
# max-redirects=1"""
#         )


if __name__ == "__main__":
    # -----------------------set logging-------------------------------
    config_log("aslog.txt")

    # -----------------------parse args----------------------------
    parser = argparse.ArgumentParser(description="Probe protocol or Grab web pages")
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s version : v 0.01",
        help="show the version",
    )
    parser.add_argument(
        "--mode", "-m", help="scan, probe or grab", type=str, default="probe"
    )
    parser.add_argument(
        "--top100", "-t", help="specify the top 1-100 ports", type=int, default=0
    )
    parser.add_argument(
        "--dryrun",
        "-d",
        help="dry run without actual probing or grabbing",
        action="store_true",
    )
    args = parser.parse_args()

    # -----------------------read config---------------------------
    config = ConfigParser()
    config.read("conf.ini", encoding="utf-8")

    target_ports = config["asgrab"]["target-ports"]
    if args.top100 >= 1 and args.top100 <= 100:
        target_ports = ",".join(
            config["asgrab"]["top100ports"].split(",")[: args.top100 - 1]
        )

    allowlist = config["asgrab"]["target-hosts"]
    blocklist = config["asgrab"]["zmap-blocklist"]

    source_ip = config["asgrab"]["source-ip"]
    send_interface = config["asgrab"]["send-interface"]
    gateway_mac = config["asgrab"]["gateway-mac"]

    # get current time for result naming
    cur_time = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    lzr_results = "results/lzr_result_" + cur_time + ".json"
    zgrab_results = "results/zgrab_result_" + cur_time + ".json"
    zmap_results = "results/zmap_result_" + cur_time + ".json"

    # change directory
    # ......

    # ----------------------claim information----------------------
    logging.info(f"New task start ({cur_time})")

    # ----------------------actual scanning, probing or grabing-------------------
    cmd = ""
    if args.mode == "probe":
        cmd = f"""sudo utils/zmap -w {allowlist} -b {blocklist} -p {target_ports} --output-filter="success = 1 && repeat = 0" -f "saddr,daddr,sport,dport,seqnum,acknum,window" -O json -i {send_interface} -S {source_ip} -G {gateway_mac} | \
sudo utils/lzr --handshakes http,tls -sendInterface {send_interface} -gatewayMac {gateway_mac} -f {lzr_results}"""
    elif args.mode == "grab":
        cmd = f"""sudo utils/zmap -w {allowlist} -b {blocklist} -p {target_ports} --output-filter="success = 1 && repeat = 0" -f "saddr,daddr,sport,dport,seqnum,acknum,window" -O json -i {send_interface} -S {source_ip} -G {gateway_mac} | \
sudo utils/lzr --handshakes http,tls -sendInterface {send_interface} -gatewayMac {gateway_mac} -f {lzr_results} -feedZGrab | \
utils/zgrab2 multiple -c utils/multi.ini -o {zgrab_results}"""
    elif args.mode == "scan":
        cmd = f'sudo utils/zmap -w {allowlist} -b {blocklist} -p {target_ports} --output-filter="success = 1 && repeat = 0" -f "saddr,daddr,sport,dport,seqnum,acknum,window" -O json -i {send_interface} -S {source_ip} -G {gateway_mac} -o {zmap_results}'
    else:
        logging.error(f"Invalid mode selected: {args.mode}")
        sys.exit()

    logging.debug(f"Command to use: {cmd}")
    if not args.dryrun:
        exec_cmd(cmd)

    logging.info(f"Task finished ({cur_time})")

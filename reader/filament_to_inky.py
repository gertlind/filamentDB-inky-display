from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException
import argparse
import requests
import time
import json
import math

GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]


def get_args():
    parser = argparse.ArgumentParser(description="Read OpenPrintTag and send filament data to Inky")
    parser.add_argument(
        "--db",
        default="http://127.0.0.1:3000/api",
        help="Filament DB API base URL, e.g. http://127.0.0.1:3000/api",
    )
    parser.add_argument(
        "--inky",
        required=True,
        help="Inky receiver URL, e.g. http://192.168.123.49:5000/filament",
    )
    return parser.parse_args()


def get_reader():
    r = readers()
    if not r:
        raise RuntimeError("Ingen PC/SC-läsare hittades")
    print("Använder läsare:", r[0])
    return r[0]


def read_blocks(conn, count=220):
    data = bytearray()

    for block in range(count):
        apdu = [0xFF, 0xB0, 0x00, block, 0x04]

        try:
            resp, sw1, sw2 = conn.transmit(apdu)
        except Exception:
            break

        if sw1 == 0x90 and sw2 == 0x00:
            data.extend(resp)
        else:
            break

    return bytes(data)


def fetch_filaments(db_api):
    r = requests.get(f"{db_api}/filaments", timeout=10)
    r.raise_for_status()
    return r.json()


def find_instance_id_in_raw(raw, filaments):
    raw_text = raw.decode("latin-1", errors="ignore")

    for f in filaments:
        iid = f.get("instanceId")
        if iid and str(iid) in raw_text:
            return str(iid)

    raise RuntimeError("Hittade inget instanceId")


def find_filament(instance_id, filaments):
    for f in filaments:
        if str(f.get("instanceId")) == instance_id:
            return f
    return None


def calc_remaining_m(g, d, density):
    try:
        g = float(g)
        r = (float(d) / 10) / 2
        area = math.pi * r * r
        gpm = area * 100 * float(density)
        return round(g / gpm)
    except Exception:
        return ""


def build_json(iid, f):
    spool = f.get("spoolWeight") or 0
    spools = f.get("spools") or []
    temps = f.get("temperatures") or {}

    remaining_g = ""
    if spools:
        total = spools[0].get("totalWeight")
        if total:
            remaining_g = round(float(total) - float(spool))

    remaining_m = calc_remaining_m(
        remaining_g,
        f.get("diameter"),
        f.get("density")
    )

    return {
        "instance_id": iid,
        "vendor": f.get("vendor"),
        "name": f.get("name"),
        "material": f.get("type"),
        "color_name": f.get("colorName"),
        "color_hex": f.get("color"),
        "remaining_g": remaining_g,
        "remaining_m": remaining_m,
        "nozzle_temp": temps.get("nozzle"),
        "bed_temp": temps.get("bed"),
    }


def send_to_inky(inky_url, data):
    r = requests.post(inky_url, json=data, timeout=60)
    print("Inky:", r.status_code, r.text.strip())
    r.raise_for_status()


def main():
    args = get_args()

    print("Filament DB:", args.db)
    print("Inky URL:", args.inky)

    reader = get_reader()
    print("Väntar på tagg...")

    while True:
        try:
            filaments = fetch_filaments(args.db)

            conn = reader.createConnection()
            conn.connect()

            uid, sw1, sw2 = conn.transmit(GET_UID)
            print("UID:", "".join(f"{b:02X}" for b in uid))

            raw = read_blocks(conn)

            iid = find_instance_id_in_raw(raw, filaments)
            print("Instance:", iid)

            filament = find_filament(iid, filaments)

            if not filament:
                print("Hittade inget filament")
                time.sleep(2)
                continue

            data = build_json(iid, filament)

            print(json.dumps(data, indent=2, ensure_ascii=False))

            send_to_inky(args.inky, data)

            time.sleep(5)

        except NoCardException:
            time.sleep(1)

        except CardConnectionException:
            time.sleep(1)

        except Exception as e:
            print("Fel:", e)
            time.sleep(2)


if __name__ == "__main__":
    main()

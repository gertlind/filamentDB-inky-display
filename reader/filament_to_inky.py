from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException
from pymongo import MongoClient
import argparse
import requests
import time
import json
import math
import os

GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]


def get_args():
    parser = argparse.ArgumentParser(description="Read OpenPrintTag and send filament data to Inky")

    parser.add_argument(
        "--mongo",
        default=os.environ.get("MONGODB_URI"),
        help="MongoDB URI. Can also be set with MONGODB_URI env var.",
    )

    parser.add_argument(
        "--db-name",
        default="filament-db",
        help="MongoDB database name",
    )

    parser.add_argument(
        "--inky",
        required=True,
        help="Inky receiver URL, e.g. http://192.168.123.49:5000/filament",
    )

    args = parser.parse_args()

    if not args.mongo:
        raise RuntimeError("MongoDB URI saknas. Ange --mongo eller sätt MONGODB_URI.")

    return args


def get_reader():
    r = readers()
    if not r:
        raise RuntimeError("No PC/SC-reader found")

    print("Using reader:", r[0])
    return r[0]


def read_raw_tag(reader):
    for attempt in range(1, 6):
        try:
            conn = reader.createConnection()
            conn.connect()

            uid, sw1, sw2 = conn.transmit(GET_UID)
            if sw1 == 0x90 and sw2 == 0x00:
                print("UID:", "".join(f"{b:02X}" for b in uid), "försök", attempt)

            raw = bytearray()

            for block in range(0, 500):
                apdu = [0xFF, 0xB0, 0x00, block, 0x04]

                try:
                    resp, sw1, sw2 = conn.transmit(apdu)
                except Exception as e:
                    print(f"Stop block {block}: {e}")
                    break

                if sw1 == 0x90 and sw2 == 0x00:
                    raw.extend(resp)
                else:
                    print(f"Stop block {block}: SW={sw1:02X} {sw2:02X}")
                    break

            if len(raw) < 80:
                raise RuntimeError(f"Too little data read: {len(raw)} bytes")

            print("Bytes read:", len(raw))
            return bytes(raw)

        except Exception as e:
            print(f"Read attempt {attempt} failed:", e)
            time.sleep(0.5)

    raise RuntimeError("could not read the tag after several tries")


def extract_instance_id_from_raw(raw):
    # OpenPrintTag CBOR-pattern:
    # 05 6A <10 ascii bytes>
    # 05 = instanceId-fält
    # 6A = CBOR text string with length 10

    for i in range(len(raw) - 12):
        if raw[i] == 0x05 and raw[i + 1] == 0x6A:
            candidate = raw[i + 2:i + 12]

            try:
                text = candidate.decode("ascii")
            except Exception:
                continue

            if len(text) == 10 and all(c in "0123456789abcdefABCDEF" for c in text):
                instance_id = text.lower()
                print("Instance ID found:", instance_id)
                return instance_id

    raise RuntimeError("found no instanceId in OpenPrintTag-rawdata")


def get_filament_from_mongo(mongo_uri, db_name, instance_id):
    client = MongoClient(mongo_uri)

    try:
        db = client[db_name]
        collection = db["filaments"]

        filament = collection.find_one({"instanceId": instance_id})

        if not filament:
            return None

        return filament

    finally:
        client.close()


def calc_remaining_m(grams, diameter_mm, density):
    try:
        grams = float(grams)
        radius_cm = (float(diameter_mm) / 10) / 2
        area_cm2 = math.pi * radius_cm * radius_cm
        grams_per_meter = area_cm2 * 100 * float(density)
        return round(grams / grams_per_meter)
    except Exception:
        return ""


def build_json(instance_id, filament):
    spool_weight = filament.get("spoolWeight") or 0
    spools = filament.get("spools") or []
    temps = filament.get("temperatures") or {}

    remaining_g = ""

    if spools:
        total_weight = spools[0].get("totalWeight")
        if total_weight is not None:
            remaining_g = round(float(total_weight) - float(spool_weight))
    elif filament.get("totalWeight") is not None and spool_weight is not None:
        remaining_g = round(float(filament.get("totalWeight")) - float(spool_weight))

    remaining_m = calc_remaining_m(
        remaining_g,
        filament.get("diameter"),
        filament.get("density"),
    )

    return {
        "instance_id": instance_id,
        "vendor": filament.get("vendor") or "",
        "name": filament.get("name") or "",
        "material": filament.get("type") or "",
        "color_name": filament.get("colorName") or "",
        "color_hex": filament.get("color") or "",
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

    print("Mongo DB:", args.db_name)
    print("Inky URL:", args.inky)

    reader = get_reader()
    print("waiting for tagg...")

    while True:
        try:
            raw = read_raw_tag(reader)
            instance_id = extract_instance_id_from_raw(raw)

            filament = get_filament_from_mongo(args.mongo, args.db_name, instance_id)

            if not filament:
                print("found no filament in MongoDB for instanceId:", instance_id)
                time.sleep(2)
                continue

            data = build_json(instance_id, filament)

            print("Sending JSON to Inky:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            send_to_inky(args.inky, data)

            time.sleep(5)

        except NoCardException:
            time.sleep(1)

        except CardConnectionException:
            time.sleep(1)

        except Exception as e:
            print("Error:", e)
            time.sleep(2)


if __name__ == "__main__":
    main()


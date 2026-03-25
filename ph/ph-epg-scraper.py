import gzip
import os
import xml.etree.ElementTree as ET

import requests

name = "ph"
save_as_gz = True

output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "epgs")
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, f"{name}-epg.xml")
output_file_gz = output_file + ".gz"
temp_gz_file = os.path.join(output_dir, f"{name}-temp.xml.gz")

VALID_TVG_IDS = {
    "A2Z.ph",
    "Abc.Australia.ph",
    "Aljazeera.ph",
    "ANC.ph",
    "ANIMAL.PLANET.ph",
    "ANIMAX.ph",
    "Arirang.ph",
    "ASIAN.FOOD.NETWORK.ph",
    "AXN.ph",
    "BBC.WORLD.NEWS.ph",
    "Bbcearth.Hd.ph",
    "Bilyonaryoch.ph",
    "BLOOMBERG.ph",
    "Buko.ph",
    "CARTOON.NETWORK.ph",
    "CELESTIAL.CLASSIC.MOVIES.ph",
    "CHANNEL.NEWS.ASIA.ph",
    "Cctv4.ph",
    "Cg.Dreamworktag.ph",
    "Cg.Hitsnow.ph",
    "Cg.Tvnpre.ph",
    "Cgnl.Nba.ph",
    "Cgtnenglish.ph",
    "CINEMA.ONE.ph",
    "CINEMAX.ph",
    "CINEMO!.ph",
    "CNN.ph",
    "CRIME.&amp;.INVESTIGATION.ph",
    "DEUTSCHEWELLE.ph",
    "DISCOVERY.CHANNEL.ph",
    "DREAMWORKS.ph",
    "DZMM.TELERADYO.ph",
    "FASHION.TV.ph",
    "FOOD.NETWORK.ph",
    "France24.ph",
    "GLOBAL.TREKKER.HD.ph",
    "GMA.ph",
    "GTV.ph",
    "HBO.FAMILY.ph",
    "HBO.HITS.ph",
    "HBO.SIGNATURE.ph",
    "HBO.ph",
    "HGTV.ph",
    "HISTORY.ph",
    "Hits.Hd.ph",
    "Hits.Movies.ph",
    "Ibc13.ph",
    "JEEPNEY.TV.ph",
    "KAPAMILYA.CHANNEL.HD.ph",
    "KAPAMILYA.CHANNEL.ph",
    "KBS.WORLD.ph",
    "KIX.ph",
    "KNOWLEDGE.CHANNEL.ph",
    "LIFETIME.ph",
    "Lotusmacau.Prd.ph",
    "METRO.CHANNEL.SD.ph",
    "Moonbug.Kids.ph",
    "MYX.ph",
    "NET.25.ph",
    "NHK.WORLD.JAPAN.ph",
    "NICK.JR..ph",
    "NICKELODEON.ph",
    "Onenews.Hd.ph",
    "Oneph.ph",
    "Onesportsplus.Hd.ph",
    "ONE.SPORTS.ph",
    "Pbarush.Hd.ph",
    "PBO.ph",
    "PREMIER.SPORTS.ph",
    "PREMIERFOOTBALL.ph",
    "PREMIERSPORTS2.ph",
    "RPTV.ph",
    "Rptv.ph",
    "Sari.Sari.ph",
    "SOLAR.SPORTS.ph",
    "SOLARFLIX.ph",
    "SPOTV.ph",
    "Spotv.Hd2.ph",
    "TapAction.Flix.ph",
    "TAP.EDGE.ph",
    "TAP.MOVIES.ph",
    "TAPSPORTS.ph",
    "TAPTV.ph",
    "THRILL.ph",
    "TMC.(TAGALIZED.MOVIE.CHANNEL).ph",
    "TRAVEL.CHANNEL.ph",
    "TV5.ph",
    "TVNMOVIESPINOY.ph",
    "Uaap.Varsity.ph",
    "VIVA.Cinema.ph",
    "WARNER.TV.ph",
}


def download_file(url, destination, chunk_size=1024 * 1024):
    print(f"Downloading {url}...")

    try:
        with requests.get(url, stream=True, timeout=60) as response:
            if response.status_code != 200:
                print(f"Failed to fetch {url} - HTTP {response.status_code}")
                return False

            with open(destination, "wb") as file:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        print(
                            f"\rDownloaded: {downloaded / (1024 * 1024):.2f} MB",
                            end="",
                            flush=True,
                        )

        print("\nDownload complete.")
        return True

    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False


def extract_gz_to_xml(gz_file):
    try:
        print("Decompressing .gz file...")
        with gzip.open(gz_file, "rb") as f:
            decompressed_data = f.read()

        print(f"Decompression successful! Extracted {len(decompressed_data)} bytes.")
        return ET.fromstring(decompressed_data)

    except Exception as e:
        print(f"Failed to decompress or parse XML: {e}")
        return None


def filter_and_build_epg(urls):
    if not VALID_TVG_IDS:
        print("No valid TVG IDs found. Exiting.")
        return

    print(f"Loaded {len(VALID_TVG_IDS)} inline TVG IDs.")
    root = ET.Element("tv")

    for url in urls:
        if not download_file(url, temp_gz_file):
            print(f"Skipping {url} due to download failure.")
            continue

        epg_data = extract_gz_to_xml(temp_gz_file)
        if epg_data is None:
            print(f"Skipping {url} due to decompression errors.")
            continue

        print(f"Processing XML from {url}...")

        channel_count = 0
        for channel in epg_data.findall("channel"):
            tvg_id = channel.get("id")
            if tvg_id in VALID_TVG_IDS:
                root.append(channel)
                channel_count += 1
        print(f"Added {channel_count} channels.")

        program_count = 0
        for programme in epg_data.findall("programme"):
            tvg_id = programme.get("channel")
            if tvg_id in VALID_TVG_IDS:
                root.append(programme)
                program_count += 1
        print(f"Added {program_count} programmes.")

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"New EPG saved to {output_file}")

    if save_as_gz:
        with gzip.open(output_file_gz, "wb") as f:
            tree.write(f, encoding="utf-8", xml_declaration=True)
        print(f"New EPG saved to {output_file_gz}")

    if os.path.exists(temp_gz_file):
        os.remove(temp_gz_file)


urls = [
    "https://epgshare01.online/epgshare01/epg_ripper_PH1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_PH2.xml.gz",
]


if __name__ == "__main__":
    filter_and_build_epg(urls)

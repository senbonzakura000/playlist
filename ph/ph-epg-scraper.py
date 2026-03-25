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
    "ANC.ph",
    "ANIMAX.ph",
    "AXN.ph",
    "Abc.Australia.ph",
    "Aljazeera.ph",
    "Animal.Planet.ph",
    "Arirang.ph",
    "Asianfoodnetwork.ph",
    "Bbcearth.Hd.ph",
    "Bbcworld.News.ph",
    "Bilyonaryoch.ph",
    "Bloomberg.ph",
    "Buko.ph",
    "CELESTIAL.CLASSIC.MOVIES.ph",
    "CINEMO!.ph",
    "Cartoon.Net.Hd.ph",
    "Cctv4.ph",
    "Cg.Dreamworktag.ph",
    "Cg.Hitsnow.ph",
    "Cg.Tvnpre.ph",
    "Cgnl.Nba.ph",
    "Cgtnenglish.ph",
    "Channelnews.Asia.ph",
    "Cinema.One.ph",
    "Cinemax.ph",
    "Cnn.Hd.ph",
    "Crime.Investigation.ph",
    "DEUTSCHEWELLE.ph",
    "DZMM.TELERADYO.ph",
    "Discovery.ph",
    "Dreamworks.Hd.ph",
    "Fashiontv.Hd.ph",
    "Foodnetwork.Hd.ph",
    "France24.ph",
    "GMA.ph",
    "GTV.ph",
    "Globaltrekker.ph",
    "HBO.FAMILY.ph",
    "HBO.HITS.ph",
    "HBO.SIGNATURE.ph",
    "HBO.ph",
    "Hgtv.Hd.ph",
    "History.Hd.ph",
    "Hits.Hd.ph",
    "Hits.Movies.ph",
    "Ibc13.ph",
    "Jeepney.TV.ph",
    "Kapamilya.Channel.ph",
    "Kbs.World.ph",
    "Kix.Hd.ph",
    "Knowledge.Channel.ph",
    "Lifetime.ph",
    "Lotusmacau.Prd.ph",
    "MYX.ph",
    "Metro.Channel.ph",
    "Moonbug.Kids.ph",
    "NHK.WORLD.JAPAN.ph",
    "Net.25.ph",
    "Nickelodeon.ph",
    "Nickjr.ph",
    "Onenews.Hd.ph",
    "Oneph.ph",
    "Onesports.ph",
    "Onesportsplus.Hd.ph",
    "PBO.ph",
    "PREMIERFOOTBALL.ph",
    "PREMIERSPORTS1.ph",
    "PREMIERSPORTS2.ph",
    "Pbarush.Hd.ph",
    "ROCK.ENTERTAINMENT.ph",
    "Rptv.ph",
    "SOLAR.SPORTS.ph",
    "Sari.Sari.ph",
    "Solar.Flix.ph",
    "Spotv.Hd.ph",
    "Spotv.Hd2.ph",
    "TAPEDGE.ph",
    "TMC.(TAGALIZED.MOVIE.CHANNEL).ph",
    "TV5.ph",
    "TVNMOVIESPINOY.ph",
    "Tap.Sports.ph",
    "Tapactionflix.Hd.ph",
    "Tapmovies.Hd.ph",
    "Taptv.ph",
    "Thrill.ph",
    "Travel.Channel.ph",
    "Uaap.Varsity.ph",
    "VIVA.Cinema.ph",
    "Warnertv.Hd.ph",
    "a2z.Channel.11.ph",
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
    "https://epgshare01.online/epgshare01/epg_ripper_PH2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_PH1.xml.gz",
]


if __name__ == "__main__":
    filter_and_build_epg(urls)

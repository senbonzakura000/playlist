import gzip
import os
import xml.etree.ElementTree as ET

import requests

name = "ad"
save_as_gz = True

root_dir = os.path.dirname(os.path.dirname(__file__))
output_dir = os.path.join(root_dir, "epgs")
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, f"{name}-epg.xml")
output_file_gz = output_file + ".gz"
temp_gz_file = os.path.join(output_dir, f"{name}-temp.xml.gz")

VALID_TVG_IDS = {
    "4seven.uk",
    "ABC.National.Feed.us2",
    "ABC.News.Live.us2",
    "ACC.Network.us2",
    "AMC+.us2",
    "AMC.HD.us2",
    "Adult.Swim.ca2",
    "Altitude.Sports.us2",
    "Animal.Planet.HD.us2",
    "Astro.Premier.League.2.my",
    "Astro.Premier.League.3.my",
    "Astro.Premier.League.my",
    "BBC.America.HD.us2",
    "BBC.Four.HD.uk",
    "BBC.NEWS.HD.uk",
    "BBC.News.(North.America).HD.us2",
    "BBC.One.Lon.HD.uk",
    "BBC.Three.HD.uk",
    "BBC.Two.HD.uk",
    "Big.Ten.Network.HD.us2",
    "CBS.News.National.Stream.us2",
    "CBS.Sports.Network.HD.us2",
    "CHSN.Chicago.Sports.Network.us2",
    "CNBC.HD.us2",
    "CNN.HD.uk",
    "CNN.HD.us2",
    "Cartoon.Network.HD.Canada.ca2",
    "Cartoon.Network.HD.us2",
    "Cartoon.Netwrk.uk",
    "Channel.4.HD.uk",
    "Channel.5.HD.uk",
    "Cinemax.HD.(Pacific).us2",
    "Comedy.Central.HD.us2",
    "DAZN.Dummy.us",
    "Discovery.Channel.HD.us2",
    "Discovery.HD.uk",
    "Discovery.Life.Channel.us2",
    "Disney.Channel.HD.us2",
    "Disney.Junior.HD.us2",
    "E4.HD.uk",
    "ESPN.Deportes.HD.us2",
    "ESPN.HD.us2",
    "ESPN2.HD.us2",
    "ESPNEWS.HD.us2",
    "ESPNU.HD.us2",
    "Eurosport.1.nl",
    "Eurosport.2.nl",
    "FOX.(KSWB).San.Diego,.CA.us",
    "FS1.Fox.Sports.1.HD.us2",
    "FS2.Fox.Sports.2.HD.us2",
    "FS2.HD.us2",
    "FXX.HD.us2",
    "FanDuel.Sports.Network.Extra.HDTV.(Sun).us",
    "FanDuel.Sports.Network.Extra.HDTV.DirecTV.(Florida).us",
    "FanDuel.Sports.Network.Midwest.us",
    "FanDuel.Sports.Network.North.HDTV.us",
    "FanDuel.Sports.Network.South.(Atlanta.DMA).24/7.HDTV.us",
    "FanDuel.Sports.Network.West.HDTV.us",
    "FanDuel.Sports.Network.Wisconsin.24/7.HDTV.us",
    "FanDuel.TV.us",
    "Fight.Network.us2",
    "Film4.HD.uk",
    "Fox.Deportes.HD.us2",
    "Fox.News.Channel.HD.us2",
    "Fox.Soccer.Plus.HD.us2",
    "FoxCricket.au",
    "FoxFooty.au",
    "FoxLeague.au",
    "FoxSports503.au",
    "FoxSports505.au",
    "FoxSports506.au",
    "FoxSportsMore.au",
    "GB.News.HD.uk",
    "GREAT!.movies.uk",
    "Golf.Channel.HD.us2",
    "HBO.Comedy.HD.us2",
    "HBO.East.us2",
    "HBO.Latino.HD.us2",
    "HBO.Signature.HD.us2",
    "HBO.West.us2",
    "HBO.Zone.HD.us2",
    "HBO2.HD.us2",
    "Hub.Premier.1.sg",
    "Hub.Premier.2.sg",
    "Hub.Premier.3.sg",
    "Hub.Premier.4.sg",
    "ITV1.HD.uk",
    "ITV2.HD.uk",
    "ITV3.HD.uk",
    "ITV4.HD.uk",
    "LALIGA.TV.BAR.es",
    "LALIGA.TV.HYPERMOTION.es",
    "LFCTV.HD.uk",
    "MLB.Network.HD.us2",
    "MS.NOW.HD.us2",
    "MSG.National.us2",
    "MSG.Plus.us2",
    "MTV.HD.uk",
    "MUTV.HD.uk",
    "Marquee.Sports.Network.HD.us2",
    "More4.HD.uk",
    "NBA.TV.HD.us2",
    "NBC.East.Stream.us2",
    "NBC.Sports.Bay.Area.HD.us2",
    "NBC.Sports.Boston.HD.us2",
    "NBC.Sports.California.SAT.us2",
    "NBC.Sports.Philadelphia.HD.us2",
    "NFL.Network.HD.us2",
    "NFL.RedZone.HD.us2",
    "NHL.Network.HD.us2",
    "New.England.Sports.Network.HD.us2",
    "Newsmax.TV.HD.us2",
    "Nick.Jr..HD.uk",
    "Nick.Jr.HD.us2",
    "Nickelodeon.HD.us2",
    "NickelodeonHD.uk",
    "Nicktoons.uk",
    "Now.Sports.Premier.League.1.hk",
    "Now.Sports.Premier.League.2.hk",
    "PREMIERSPORTS1.ph",
    "PREMIERSPORTS2.ph",
    "Peacock.Dummy.us",
    "Premier.Sports.1.HD.uk",
    "Premier.Sports.2.HD.uk",
    "Premier.Sports.Rugby.my",
    "Racing.TV.HD.uk",
    "SEC.Network.HD.us2",
    "SKY.Sport.1.nz",
    "SKY.Sport.2.nz",
    "SKY.Sport.3.nz",
    "SKY.Sport.4.nz",
    "SKY.Sport.5.nz",
    "SKY.Sport.6.nz",
    "SKY.Sport.7.nz",
    "SKY.Sport.8.nz",
    "SNY.SportsNet.New.York.HD.us2",
    "Sky.Action.uk",
    "Sky.Atlantic.HD.uk",
    "Sky.Cinema.Hits.HD.uk",
    "Sky.Cinema.Select.uk",
    "Sky.Comedy.Cinema.uk",
    "Sky.Family.HD.uk",
    "Sky.News.HD.uk",
    "Sky.Premiere.uk",
    "Sky.Sport.Bundesliga.de",
    "Sky.Sport.Premier.League.de",
    "Sky.Sport.Top.Event.de",
    "SkyAnimationHD.uk",
    "SkySp+HD.uk",
    "SkySp.ActionHD.uk",
    "SkySp.F1.HD.uk",
    "SkySp.Fball.HD.uk",
    "SkySp.Golf.HD.uk",
    "SkySp.Mix.HD.uk",
    "SkySp.News.HD.uk",
    "SkySp.PL.HD.uk",
    "SkySp.Racing.HD.uk",
    "SkySp.Tennis.HD.uk",
    "SkySpCricket.HD.uk",
    "SkySpMainEvHD.uk",
    "Spectrum.SportsNet.LA.Dodgers.HD.us2",
    "Spectrum.SportsNet.us",
    "Spectrum.Sportsnet.Dodgers.us",
    "SporTV.2.br",
    "SporTV.br",
    "Sportsnet.(Pacific).HD.ca2",
    "Sportsnet.360.HD.ca2",
    "Sportsnet.East.HD.ca2",
    "Sportsnet.One.HD.ca2",
    "Sportsnet.Ontario.HD.ca2",
    "Sportsnet.West.HD.ca2",
    "Sportsnet.World.HD.ca2",
    "SuperSport.1.al",
    "SuperSport.2.al",
    "SuperSport.3.al",
    "TBS.HD.us2",
    "TNT.HD.us2",
    "TNT.Sports.1.HD.uk",
    "TNT.Sports.2.HD.uk",
    "TNT.Sports.3.HD.uk",
    "TNT.Sports.4.HD.uk",
    "TNT.Sports.Ultimate.uk",
    "TSN.1.ca2",
    "TSN.2.HD.ca2",
    "TSN.3.HD.ca2",
    "TSN.4.HD.ca2",
    "TSN.5.HD.ca2",
    "Teen.Nick.us2",
    "Tennis.Channel.HD.us2",
    "UNIVERSO.HD.us2",
    "USA.Network.HD.us2",
    "Virgin.Media.One.HD.ie",
    "Virgin.Media.Three.HD.ie",
    "WWE.Network.us2",
    "Willow.Cricket.HD.us2",
    "Willow.Xtra.us2",
    "World.Fishing.Network.HD.(US).us2",
    "Ziggo.Sport.2.nl",
    "Ziggo.Sport.3.nl",
    "Ziggo.Sport.4.nl",
    "Ziggo.Sport.5.nl",
    "Ziggo.Sport.6.nl",
    "Ziggo.Sport.nl",
    "beIN.SPORTS.1.my",
    "beIN.SPORTS.2.my",
    "beIN.SPORTS.3.my",
    "beIN.Sports.USA.HD.us2",
    "beINSports1.au",
    "beINSports2.au",
    "beINSports3.au",
    "plex.tv.CBS.Sports.HQ.plex",
    "plex.tv.NBC.News.NOW.plex",
    "plex.tv.Tennis.Channel.2.plex",
    "sportdigital.Fussball.de",
    "truTV.HD.us2",
    "unifi.spotv.my",
    "unifi.spotv2.my",
    "unifi.unifisports1.my",
}

urls = [
    "https://epgshare01.online/epgshare01/epg_ripper_AL1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_AU1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_BR1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_BR2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_CA2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_ES1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_HK1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_IE1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_MY1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_NL1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_NZ1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_PH2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_PH1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_PLEX1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_SG1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US_SPORTS1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
    "https://raw.githubusercontent.com/senbonzakura000/playlist/refs/heads/main/unifi/unifi_epg.xml.gz",
]


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


def extract_xml_file(xml_file):
    try:
        if xml_file.endswith(".gz"):
            print("Decompressing .gz file...")
            with gzip.open(xml_file, "rb") as f:
                data = f.read()
        else:
            print("Reading XML file...")
            with open(xml_file, "rb") as f:
                data = f.read()

        print(f"XML load successful! Extracted {len(data)} bytes.")
        return ET.fromstring(data)

    except Exception as e:
        print(f"Failed to load or parse XML: {e}")
        return None


def filter_and_build_epg(urls):
    if not VALID_TVG_IDS:
        print("No valid TVG IDs found. Exiting.")
        return

    print(f"Loaded {len(VALID_TVG_IDS)} inline TVG IDs.")
    print(f"Fetching {len(urls)} source files.")
    root = ET.Element("tv")

    for url in urls:
        if not download_file(url, temp_gz_file):
            print(f"Skipping {url} due to download failure.")
            continue

        epg_data = extract_xml_file(temp_gz_file)
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


if __name__ == "__main__":
    filter_and_build_epg(urls)

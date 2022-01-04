import os
import subprocess
import urllib.request
from dataclasses import dataclass

# osmupdate
from datetime import datetime
from pathlib import Path

default_path = Path("/tmp") / "osm"


@dataclass
class OSMUpdate:
    """
    Handle initial fetch and updates of a particular region
    from geofabrik

    """

    region: str
    country: str
    cache_dir: Path = Path("/tmp") / "osm"
    server: str = "download.geofabrik.de"

    @property
    def full_url(self):
        return f"http://{self.server}/{self.region}/{self.country}-latest.osm.pbf"

    @property
    def updates_url(self):
        return f"http://{self.server}/{self.region}/{self.country}-updates/"

    @property
    def get_cache_dir(self) -> Path:
        return Path() / (self.cache_dir or default_path) / self.region

    @property
    def get_cache_file(self) -> Path:
        return self.get_cache_dir / self.filename

    @property
    def get_temp_dir(self) -> Path:
        return self.get_cache_dir / f"{self.country}-updates"

    @property
    def filename(self) -> Path:
        return Path(f"{self.country}-latest.osm.pbf")

    @property
    def file_exists(self) -> bool:
        return os.path.exists(self.get_cache_file)

    def ensure_cache_dir(self):
        os.makedirs(self.get_cache_dir(), exist_ok=True)

    def fetch(self):
        # Ensure that the directory to save the file to exists
        os.makedirs(self.get_cache_dir, exist_ok=True)
        os.makedirs(self.get_temp_dir, exist_ok=True)
        if self.file_exists:
            # The file itself should not exist
            raise FileExistsError
        urllib.request.urlretrieve(self.full_url, self.get_cache_file)

    def update_file(self):
        """
        Calls osmupdate to pull the changes relevant for the area
        """
        try:
            now = datetime.today().strftime("%Y-%m-%d")
            cachefile = self.get_cache_file
            cmd = "osmupdate"
            params = [
                f"{cachefile}",
                str(cachefile).replace("latest", f"update-{now}"),
                f"--base-url={self.updates_url}",
                f"--tempfiles={self.get_temp_dir}/",
                "--keep-tempfiles",
                "--trust-tempfiles",
            ]
            print(" ".join([cmd, *params]))
            subprocess.call([cmd, *params])
        except Exception as E:  # noqa: F841
            raise


@dataclass
class EastTimor(OSMUpdate):
    region: str = "asia"
    country: str = "east-timor"

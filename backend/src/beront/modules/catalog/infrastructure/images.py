import hashlib
import io
import re
import warnings
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError

from beront.shared.domain.errors import DomainError, NotFound


class LocalImageStorage:
    def __init__(self, root):
        self.uploads, self.staging = root / "uploads", root / "staging"
        self.uploads.mkdir(parents=True, exist_ok=True)
        self.staging.mkdir(parents=True, exist_ok=True)

    def save(self, stream):
        payload = stream.read(5 * 1024 * 1024 + 1)
        if len(payload) > 5 * 1024 * 1024:
            raise DomainError("IMAGE_TOO_LARGE", "La fotografía excede 5 MiB.")
        filename = uuid4().hex + ".webp"
        temporary = self.staging / filename
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(payload)) as image:
                    if image.format not in {"JPEG", "PNG", "WEBP"}:
                        raise DomainError("INVALID_IMAGE_TYPE", "Usa JPEG, PNG o WebP.")
                    if image.width * image.height > 20_000_000 or getattr(
                        image, "is_animated", False
                    ):
                        raise DomainError(
                            "INVALID_IMAGE",
                            "La imagen debe ser estática y de hasta 20 megapíxeles.",
                        )
                    image.verify()
                with Image.open(io.BytesIO(payload)) as image:
                    normalized = ImageOps.exif_transpose(image).convert("RGB")
                    normalized.info.clear()
                    normalized.save(temporary, "WEBP", quality=88, exif=b"", icc_profile=b"")
            temporary.replace(self.uploads / filename)
            return filename
        except (
            UnidentifiedImageError,
            OSError,
            SyntaxError,
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
        ) as exc:
            raise DomainError("INVALID_IMAGE", "No se pudo validar la fotografía.") from exc
        finally:
            temporary.unlink(missing_ok=True)

    def path(self, filename):
        if not re.fullmatch(r"[a-f0-9]{32}\.webp", filename):
            raise NotFound()
        return self.uploads / filename

    def delete(self, filename):
        self.path(filename).unlink(missing_ok=True)

    def describe(self, filename):
        path = self.path(filename)
        with Image.open(path) as image:
            width, height = image.size
        return {
            "filename": filename,
            "width": width,
            "height": height,
            "size_bytes": path.stat().st_size,
            "checksum": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

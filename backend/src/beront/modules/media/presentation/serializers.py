def asset_data(asset):
    return {
        "id": str(asset.id),
        "url": asset.url,
        "name": asset.name,
        "width": asset.width,
        "height": asset.height,
        "size_bytes": asset.size_bytes,
        "created_at": asset.created_at.isoformat(),
        "version": asset.version,
    }

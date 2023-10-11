from beanie import Document
from typing import Optional


class DBWorkspace(Document):
    """
    Model to store a workspace in the mongo-database.

    Information to handle workspaces and from bag-info.txt are stored here.

    Attributes:
        ocrd_identifier             Ocrd-Identifier (mandatory)
        bagit_profile_identifier    BagIt-Profile-Identifier (mandatory)
        ocrd_base_version_checksum  Ocrd-Base-Version-Checksum (mandatory)
        ocrd_mets                   Ocrd-Mets (optional)
        bag_info_adds               bag-info.txt can also (optionally) contain additional
                                    key-value-pairs which are saved here
        deleted                     the document is deleted if set, however, the record is still preserved
        pages_locked                a data structure that holds output `fileGrp`s and their respective locked `page_id`
                                    that are currently being processed by an OCR-D processor (server or worker).
                                    If no `page_id` field is set, an identifier "all_pages" will be used.
        mets_server_url             If set, the reading from and writing to the mets file happens through the METS Server
    """
    workspace_id: str
    workspace_mets_path: str
    ocrd_identifier: str
    bagit_profile_identifier: str
    ocrd_base_version_checksum: Optional[str]
    ocrd_mets: Optional[str]
    bag_info_adds: Optional[dict]
    mets_server_url: Optional[str]
    deleted: bool = False

    class Settings:
        name = "workspace"

"""
Definition of the :class:`CsaAsciiHeader`.
"""

from csa_header.ascii.ascconv import parse_ascconv


class CsaAsciiHeader:
    """
    Represents and handles the parsing of
    `CSA header <https://nipy.org/nibabel/dicom/siemens_csa.html>`_ values
    returned by `pydicom <https://github.com/pydicom/pydicom>`_ as bytes.
    """

    #: The header's ASCII-based character encoding.
    ENCODING = "ISO-8859-1"

    def __init__(self, header: str | bytes):
        """
        Decodes the header and sets empty property caches to be overriden on
        request.

        Parameters
        ----------
        header : Union[str, bytes]
            String or bytes containing ASCCONV header information.
        """
        if isinstance(header, bytes):
            header = header.decode(self.ENCODING)
        self._header = header

        # Property cache
        self._parsed: dict[str, dict] = {}

    def parse(self) -> dict:
        """
        Parses ``ASCCONV`` header values as dict of dicts / list / scalars.
        :class:`~csa_header.ascii.element.CsaAsciiElement`
        instances (or all if left None) as a dictionary.

        Parameters
        ----------
        elements : list, optional
            :class:`~csa_header.ascii.element.CsaAsciiElement`
            instances, by default None

        Returns
        -------
        dict
            Header information as a dictionary
        """
        return parse_ascconv(self._header, '""')[0]

    @property
    def parsed(self) -> dict:
        """
        Caches the parsed dictionary as a private attribute.

        Returns
        -------
        dict
            Header information as dictionary
        """
        if not self._parsed:
            self._parsed = self.parse()
        return self._parsed

    @property
    def n_slices(self) -> int:
        """
        Returns the number of slices (tiles) in a mosaic.

        Returns
        -------
        int
            Number of slices encoded as a 2D mosaic
        """
        return self.parsed["sSliceArray"]["lSize"]

"""Field-specific validation rules for the CBAM intake template.

The Rules sheet of the source Excel file describes the expected constraints
in natural language. This module translates those rules into machine-readable
form so they can be applied during validation.

Rules that depend on external reference data we do not have access to
(CBAM Annex I codes, EU exemption country list, the full list of EU Member
State competent authorities) are explicitly **not** implemented and are
marked with a TODO comment near the relevant field.

The mandatory flag for every field is derived dynamically from the Rules
sheet (columns 3 and 4) and lives on :class:`app.schemas.workbook.FieldSpec`,
so it is not repeated here.
"""
from __future__ import annotations

# ISO 3166-1 alpha-2 country codes.
# Source: ISO 3166-1 (offline copy; no external dependency required).
ISO_3166_ALPHA2: list[str] = [
    "AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AQ", "AR", "AS", "AT",
    "AU", "AW", "AX", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI",
    "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS", "BT", "BV", "BW", "BY",
    "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN",
    "CO", "CR", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM",
    "DO", "DZ", "EC", "EE", "EG", "EH", "ER", "ES", "ET", "FI", "FJ", "FK",
    "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF", "GG", "GH", "GI", "GL",
    "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM",
    "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IO", "IQ", "IR",
    "IS", "IT", "JE", "JM", "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN",
    "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC", "LI", "LK", "LR", "LS",
    "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME", "MF", "MG", "MH", "MK",
    "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW",
    "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP",
    "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM",
    "PN", "PR", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW",
    "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM",
    "SN", "SO", "SR", "SS", "ST", "SV", "SX", "SY", "SZ", "TC", "TD", "TF",
    "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TR", "TT", "TV", "TW",
    "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI",
    "VN", "VU", "WF", "WS", "YE", "YT", "ZA", "ZM", "ZW",
]


# Each entry maps a Template header to the list of (validator_name, params)
# tuples that will be applied IN ADDITION to the dynamic checks derived
# from the Rules sheet (required, max_length, digit_pattern, is_iso_3166).
FIELD_RULES: dict[str, list[tuple[str, dict]]] = {
    "EORI Number": [
        (
            "regex",
            {
                "pattern": r"^[A-Z]{2}[A-Z0-9]{1,15}$",
                "message": (
                    "Must start with a 2-letter country code followed by "
                    "up to 15 alphanumeric characters"
                ),
            },
        ),
    ],
    "TARIC Code": [
        (
            "regex",
            {"pattern": r"^\d{10}$", "message": "Must be exactly 10 digits"},
        ),
    ],
    "CN Code": [
        (
            "regex",
            {"pattern": r"^\d{8}$", "message": "Must be exactly 8 digits"},
        ),
        # TODO: also require the code to fall within CBAM Annex I codes.
        #       We do not have the official list; only format is checked.
    ],
    "Product Type": [
        (
            "allowed_values",
            {
                "values": ["Simple", "Complex"],
                "message": "Must be 'Simple' or 'Complex'",
            },
        ),
    ],
    "Import Volume": [
        ("positive_number", {}),
    ],
    "Date of importation": [
        # The Rules sheet marks this as "Integer", but the example value
        # "05.05.2026" makes the real intent clear: a European-format date.
        ("date", {"format": "%d.%m.%Y"}),
    ],
    "Country of Origin": [
        (
            "allowed_values",
            {
                "values": ISO_3166_ALPHA2,
                "message": "Must be a valid ISO 3166-1 alpha-2 country code",
            },
        ),
        # TODO: also reject EU member states and exemption countries per the
        #       regulation. We do not have the official exemption list.
    ],
    # TODO: Competent Authority — "Must match a valid EU Member State
    #       competent authority". We do not have the official list.
    # TODO: Contact Person — "Must include name and at least one contact
    #       method". Heuristic check is possible but not implemented.
    # TODO: Data Owner — "must be a valid internal contact". External
    #       data source required.
    # TODO: Goods Description / Sector Category — "Must match CN Code
    #       classification". Cross-field check, deferred.
}

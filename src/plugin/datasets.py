"""Built-in legacy batches; all strings deliberately preserve whitespace and zero-padded ZIPs."""
FIXTURES = {
    "messy": [
        {"id": 101, "full_name": "  Ada   Lovelace ", "email": " ADA@EXAMPLE.COM ", "active": " YES ", "zip": " 00501 ", "country": " "},
        {"id": 102, "full_name": "Grace Hopper", "email": "Grace@Example.org", "active": "no", "zip": "02108", "country": "us"},
        {"id": 103, "full_name": "  Alan   Turing", "email": "a.turing@example.com", "active": "1", "zip": "00001", "country": "gb"},
        {"id": 104, "full_name": " Lin  Q.  ", "email": " Lin@example.com ", "active": "FALSE", "zip": "10001", "country": "US"},
        {"id": 105, "full_name": "Émilie du  Châtelet", "email": "EMILIE@example.fr", "active": "true", "zip": "75001", "country": "fr"},
    ],
    "international": [
        {"id": 7, "full_name": "  Marie  Curie ", "email": " MARIE@EXAMPLE.PL", "active": "0", "zip": " 00-001 ", "country": " pl "},
        {"id": 8, "full_name": "Niels  Bohr", "email": " niels@EXAMPLE.DK ", "active": "TRUE", "zip": " 0100 ", "country": " dk"},
        {"id": 9, "full_name": "\u674e \u96f7", "email": " LEI@example.cn ", "active": "False", "zip": "00100", "country": " cn "},
    ],
    "empty": [],
}
RULES = (
    "For every legacy record: user_id=id, display_name=full_name.strip() with internal whitespace runs "
    "collapsed to single spaces, email=email.strip().lower(), enabled true for active in "
    "{yes,true,1} ignoring case and surrounding spaces, false for {no,false,0}; "
    "postal_code=zip.strip() as STRING preserving leading zeros; country_code=country.strip().upper() "
    "or US if blank. Preserve all records and IDs. Candidate record order is irrelevant."
)

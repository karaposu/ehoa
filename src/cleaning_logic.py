import re

def extract_identifier_section(record):
    # Define the patterns to match various sections, ensuring "Gelen Transfer" or "Giden Transfer" are included in the identifier
    patterns = [
        r'(Giden Transfer, [^,]+),',  # Matches 'Giden Transfer'
        r'(Gelen Transfer, [^,]+),',  # Matches 'Gelen Transfer'
        r'Encard Harcaması, ([^,]+?)(?=\d+\.\d+ [A-Z]{3}|,|$)',  # Improved to handle line breaks and end of string
        r'Ödeme, ([^,]+)-',  # Matches 'Ödeme'
        r'Para Çekme, ([^,]+),',  # Matches 'Para Çekme'
        r'Masraf/Ücret, ([^,]+),',  # Matches 'Masraf/Ücret'
        r'Diğer, ([^\n]+)$',  # Matches 'Diğer' till the end or newline
    ]

    # Merge patterns into a single regex with alternation
    combined_pattern = '|'.join(patterns)
    match = re.search(combined_pattern, record, re.DOTALL)  # Use DOTALL to match across multiple lines
    if match:
        # Return the first non-empty group found
        return next(group for group in match.groups() if group is not None)

    return None

# Test the function with various records
test_records = [
    "Giden Transfer, Hayriye Meltem Özgür, Bireysel Ödeme, EFT (FAST) sorgu no: 1727327234",
    "Encard Harcaması, I.-SHOP WWW.PZZ.BY PAR g.p. MACHULI BY, 9.01 USD, işlem kuru 32.980000 TL",
    "Ödeme, Türk Telekom Mobil (TT Mobil)-Faturalı Hat faturası, abone no : 5059704043",
    "Gelen Transfer, ENES ESVET KUZUCU, Bireysel Ödeme",
    "Para Çekme, Yurtdışında ATM'den para çekme, 46.97 USD, işlem kuru 33.325000 TL.",
    "Masraf/Ücret, Yurtdışında ATM'den para çekme komisyon.",
    "Diğer, EMK GIDA ISTANBUL TR"
]

for record in test_records:
    identifier = extract_identifier_section(record)
    print(f"Record: {record}\nIdentifier: {identifier}\n")






# import re
#
# patterns = [
#     {"pattern": r'\d+\.\d+ USD', "replacement": ""},  # Example pattern to remove amounts in USD
#     {"pattern": r', işlem kuru \d+\.\d+ TL', "replacement": ""},  # Example pattern to remove exchange rate info
#     # Add your other patterns here
# ]
#
# # Test string
# test_str = "Encard Harcaması, I.-SHOP WWW.PZZ.BY PAR g.p. MACHULI BY, 9.01 USD, işlem kuru 32.980000 TL"
# "Encard Harcaması, I.-SHOP WWW.PZZ.BY PAR g.p. MACHULI BY, 9.01 USD, işlem kuru 32.980000 TL"
#
# # Apply each pattern
# for pat in patterns:
#     test_str = re.sub(pat['pattern'], pat['replacement'], test_str)
#
# print(test_str)  # Check
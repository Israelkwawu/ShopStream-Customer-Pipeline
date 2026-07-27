import pandas as pd

from deduplicate import deduplicate_customers


def test_deduplicate_keeps_highest_priority_record():

    df = pd.DataFrame({
        "email": [
            "a@test.com",
            "a@test.com"
        ],
        "email_valid": [
            True,
            True
        ],
        "first_name": [
            "John",
            None
        ],
        "last_name": [
            "Doe",
            "Doe"
        ],
        "phone": [
            None,
            "1234567890"
        ],
        "region": [
            None,
            "US"
        ],
        "registration_date": [
            None,
            "2026-01-01"
        ],
        "opt_out": [
            False,
            False
        ],
        "source": [
            "crm",
            "website"
        ],
    })


    result = deduplicate_customers(df)


    assert len(result) == 1


    row = result.iloc[0]


    assert row["source"] == "crm"

    # Missing values should be filled from duplicate record
    assert row["phone"] == "1234567890"
    assert row["region"] == "US"

    assert row["first_name"] == "John"

    assert row["source_count"] == 2



def test_opt_out_is_true_if_any_source_true():

    df = pd.DataFrame({
        "email": [
            "a@test.com",
            "a@test.com"
        ],
        "email_valid": [
            True,
            True
        ],
        "first_name": [
            "John",
            "John"
        ],
        "last_name": [
            "Doe",
            "Doe"
        ],
        "phone": [
            "123",
            "123"
        ],
        "region": [
            "US",
            "US"
        ],
        "registration_date": [
            "2026-01-01",
            "2026-01-01"
        ],
        "opt_out": [
            False,
            True
        ],
        "source": [
            "crm",
            "website"
        ],
    })


    result = deduplicate_customers(df)


    assert bool(result.iloc[0]["opt_out"]) is True



def test_invalid_emails_are_not_deduplicated():

    df = pd.DataFrame({
        "email": [
            "bad",
            "bad"
        ],
        "email_valid": [
            False,
            False
        ],
        "first_name": [
            "John",
            "Johnny"
        ],
        "last_name": [
            "Doe",
            "Doe"
        ],
        "phone": [
            "111",
            "222"
        ],
        "region": [
            "US",
            "US"
        ],
        "registration_date": [
            "2026-01-01",
            "2026-01-01"
        ],
        "opt_out": [
            False,
            False
        ],
        "source": [
            "crm",
            "website"
        ],
    })


    result = deduplicate_customers(df)


    # Invalid emails should remain separate
    assert len(result) == 2



def test_sources_are_tracked():

    df = pd.DataFrame({
        "email": [
            "a@test.com",
            "a@test.com",
            "a@test.com"
        ],
        "email_valid": [
            True,
            True,
            True
        ],
        "first_name": [
            "John",
            "John",
            "John"
        ],
        "last_name": [
            "Doe",
            "Doe",
            "Doe"
        ],
        "phone": [
            "111",
            "111",
            "111"
        ],
        "region": [
            "US",
            "US",
            "US"
        ],
        "registration_date": [
            "2026-01-01",
            "2026-01-01",
            "2026-01-01"
        ],
        "opt_out": [
            False,
            False,
            False
        ],
        "source": [
            "crm",
            "website",
            "marketing"
        ],
    })


    result = deduplicate_customers(df)


    row = result.iloc[0]


    assert row["source_count"] == 3

    assert "crm" in row["sources"]
    assert "website" in row["sources"]
    assert "marketing" in row["sources"]
    
    
import pytest
import polars as pl
import os
import tempfile

from app.services.anonymization import AnonymizationService
from app.services.strategies import *  

# Helpers

def create_test_csv():
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    tmp_file.close()

    df = pl.DataFrame({
        "firstname": ["joao", "maria", "kaykay", "marcello"],
        "lastname": ["pedro", "clark", "san", "song"],
        "email": [
            "joao@gmail.com",
            "maria@gmail.com",
            "kaynan2993san@gmail.com",
            "marcello321@gmail.com"
        ],
        "cpf": [
            "12345678900",
            "98765432100",
            "08785939349",
            "98765432103"
        ]
    })

    df.write_csv(tmp_file.name)
    return tmp_file.name


class MockDataset:
    def __init__(self, path):
        self.file_path = path


class MockDatasetService:
    def __init__(self, path):
        self.path = path

    async def get_dataset(self, *args, **kwargs):
        return MockDataset(self.path)


def print_comparison(input_path, output_path):
    original = pl.read_csv(input_path)
    anonymized = pl.read_csv(output_path)

    print("\n--- ORIGINAL ---")
    print(original)

    print("\n--- ANONYMIZED ---")
    print(anonymized)


#test

@pytest.mark.asyncio
async def test_anonymization_service_full_flow():
    input_path = create_test_csv()

    service = AnonymizationService(
        dataset_repository=None,
        dataset_service=MockDatasetService(input_path)
    )

    try:
        #PROPORTIONAL
        class FakeRequest:
            def __init__(self):
                self.columns = [
                    type("col", (), {"column_name": "email", "alpha": 0.5}),
                    type("col", (), {"column_name": "lastname", "alpha": 0.5}),
                ]

        response1 = await service.anonymize_proportional(
            dataset_id=1,
            request=FakeRequest(),
            user=None
        )

        output1 = response1["output_path"]

        print("\n\n===== RESULT: PROPORTIONAL =====")
        print_comparison(input_path, output1)

        df1 = pl.read_csv(output1)

        assert "*" in df1["email"][0]
        assert "*" in df1["lastname"][0]

        #STRUCTURE AWARE
        class FakeRequest2:
            def __init__(self):
                self.columns = [
                    type("col", (), {"column_name": "cpf", "p": 3, "q": 2}),
                    type("col", (), {"column_name": "email", "p": 3, "q": 2}),
                ]

        response2 = await service.anonymize_structure_aware(
            dataset_id=1,
            request=FakeRequest2(),
            user=None
        )

        output2 = response2["output_path"]

        print("\n\n===== RESULT: STRUCTURE AWARE =====")
        print_comparison(input_path, output2)

        df2 = pl.read_csv(output2)

        value = df2["cpf"][0]
        assert value.startswith("123")
        assert value.endswith("00")
        assert "*" in value
        assert "*" in df2["email"][0]

    finally:
        for path in [input_path, output1, output2]:
            if path and os.path.exists(path):
                os.remove(path)
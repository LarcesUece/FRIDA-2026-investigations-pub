import polars as pl
import anyio

#from app.core.exceptions import DatasetValidationException
from app.services.strategies.base import MaskingRegistry
from app.schemas.anonymization import MaskingConfig
from app.services.strategies import proportional, structure_aware


class AnonymizationService:

    def __init__(self, dataset_repository, dataset_service):
        self.dataset_repository = dataset_repository
        self.dataset_service = dataset_service

    async def anonymize_proportional(self, dataset_id, request, user):
        configs = [
            MaskingConfig(
                column_name=col.column_name,
                method="proportional",
                params={"alpha": col.alpha}
            )
            for col in request.columns
        ]

        return await self._anonymize(dataset_id, configs, user)


    async def anonymize_structure_aware(self, dataset_id, request, user):
        configs = [
            MaskingConfig(
                column_name=col.column_name,
                method="structure_aware",
                params={"p": col.p, "q": col.q}
            )
            for col in request.columns
        ]

        return await self._anonymize(dataset_id, configs, user)


    #CORE

    async def _anonymize(self, dataset_id, configs, user):

        dataset = await self.dataset_service.get_dataset(dataset_id, user)

        if not dataset.file_path:
            #raise DatasetValidationException("Dataset has no file.")
            raise KeyError

        output_path = self._generate_output_path(dataset.file_path)

        await anyio.to_thread.run_sync(
            self._process_csv_streaming,
            dataset.file_path,
            output_path,
            configs
        )

        return {"output_path": output_path}


    #streaming with polars

    def _process_csv_streaming(self, input_path, output_path, configs):

        lf = pl.scan_csv(input_path)

        lf = self._apply_masking(lf, configs)

        lf.sink_csv(output_path)


    def _apply_masking(self, lf: pl.LazyFrame, configs):

        for config in configs:
            strategy_cls = MaskingRegistry.get(config.method)
            strategy = strategy_cls(**config.params)

            if config.column_name not in lf.columns:
                continue

            lf = lf.with_columns(
                pl.col(config.column_name)
                .cast(pl.Utf8)
                .map_elements(
                    lambda x: strategy.apply(x) if x is not None else x
                )
                .alias(config.column_name)
            )

        return lf


    def _generate_output_path(self, input_path: str) -> str:
        return input_path.replace(".csv", "_anonymized.csv")